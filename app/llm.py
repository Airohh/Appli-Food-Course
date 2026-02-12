# Gestion des appels LLM pour sélectionner les recettes et nettoyer les courses

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import N_RECIPES_FINAL, OPENAI_API_KEY
from .retry import retry_openai
from .validators import validate_courses_list, sanitize_course_item


ROOT = Path(__file__).parent
client = OpenAI(api_key=OPENAI_API_KEY)

# Versioning des prompts
PROMPT_VERSIONS = {
    "choose_recipes.txt": "v1.0",
    "consolidate.txt": "v1.0",
    "deduplicate_courses.txt": "v1.0",
    "complete_quantities.txt": "v1.0",
}


def _load_prompt(filename: str, version: str | None = None) -> str:
    # Charge un prompt depuis prompts/
    path = ROOT / "prompts" / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    
    content = path.read_text(encoding="utf-8").strip()
    
    # On garde juste la version en mémoire, on modifie pas le fichier
    return content


def get_prompt_version(filename: str) -> str:
    # Retourne la version du prompt, ou "unknown" si pas trouvé
    return PROMPT_VERSIONS.get(filename, "unknown")


def _lite_candidates(candidates: List[Dict[str, Any]], limit: int = 25) -> List[Dict[str, Any]]:
    # Filtre et réduit les recettes pour pas envoyer trop de données au LLM

    shortlisted: List[Dict[str, Any]] = []
    for recipe in candidates:
        nutrition = recipe.get("nutrition") or {}
        protein = nutrition.get("protein") or 0
        calories = nutrition.get("calories") or 0
        ready_minutes = recipe.get("readyMinutes") or 999

        if ready_minutes and ready_minutes <= 45 and protein and protein >= 25 and 250 <= calories <= 800:
            ingredients = recipe.get("ingredients") or recipe.get("extendedIngredients") or []
            names: List[str] = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    names.append(ing.get("name") or ing.get("nameClean") or "")
                elif isinstance(ing, str):
                    names.append(ing)
            names = [item for item in names if item][:10]
            shortlisted.append(
                {
                    "title": recipe.get("title"),
                    "readyMinutes": ready_minutes,
                    "sourceUrl": recipe.get("sourceUrl"),
                    "nutrition": {
                        "calories": float(calories or 0),
                        "protein": float(protein or 0),
                    },
                    "ingredients": names,
                }
            )

    shortlisted.sort(
        key=lambda item: (item["nutrition"]["protein"] or 0) / max(1.0, item["nutrition"]["calories"]),
        reverse=True,
    )
    return shortlisted[:limit]


def choose_recipes(candidates: List[Dict[str, Any]], stock: List[str]) -> List[Dict[str, Any]]:
    # Demande au LLM de choisir les meilleures recettes selon le stock

    lite = _lite_candidates(candidates, limit=25)
    prompt_template = _load_prompt("choose_recipes.txt")
    prompt_template = prompt_template.replace("**5 plats variés**", f"**{N_RECIPES_FINAL} plats variés**")

    stock_line = ", ".join(stock) if stock else "aucun"
    user_content = (
        f"{prompt_template}\n\n"
        f"Stock disponible: {stock_line}\n\n"
        f"Recettes candidates (format JSON):\n"
        f"{json.dumps(lite, ensure_ascii=False, indent=2)}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": user_content}],
    )

    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    recipes = data.get("recipes") or data.get("Recettes") or data
    return recipes


def consolidate_groceries_llm(selected: List[Dict[str, Any]], stock: List[str]) -> List[Dict[str, Any]]:
    # Utilise le LLM pour fusionner les ingrédients et enlever ce qui est en stock
    # Utilisé seulement si la consolidation locale n'a pas donné de quantités

    prompt_template = _load_prompt("consolidate.txt")
    stock_str = ", ".join(stock) if stock else "aucun"
    prompt_template = prompt_template.replace("{stock}", stock_str)

    prompt_template = prompt_template.replace(
        "5. Retourner une liste JSON propre au format :",
        "5. Retourner un objet JSON avec une clé \"groceries\" contenant un tableau au format :",
    )
    prompt_template = prompt_template.replace(
        "[\n  {\"Aliment\": \"\", \"Quantité\": \"\", \"Unité\": \"\", \"Recettes\": \"nom1, nom2, ...\"}\n]",
        "{\"groceries\": [{\"Aliment\": \"\", \"Quantité\": \"\", \"Unité\": \"\", \"Recettes\": \"nom1, nom2, ...\"}, ...]}",
    )

    user_content = (
        f"{prompt_template}\n\n"
        f"Recettes sélectionnées (format JSON):\n"
        f"{json.dumps(selected, ensure_ascii=False, indent=2)}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        max_tokens=2000,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": user_content}],
    )

    content = response.choices[0].message.content or "{}"

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        cleaned = content.strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                raise ValueError(
                    f"Impossible de parser la réponse JSON du LLM: {exc}\nContenu: {content[:500]}"
                ) from exc
        else:
            raise ValueError(
                f"Impossible de parser la réponse JSON du LLM: {exc}\nContenu: {content[:500]}"
            ) from exc

    groceries = data.get("groceries") or data.get("list") or data.get("items") or []
    if isinstance(groceries, list):
        return groceries
    return []


def deduplicate_courses_llm(courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Demande au LLM de nettoyer les doublons et normaliser les noms
    if not courses:
        return []
    
    # Vérifie que les données sont valides
    is_valid, errors = validate_courses_list(courses, strict=False)
    if not is_valid:
        raise ValueError(f"Données invalides: {', '.join(errors)}")
    
    prompt_template = _load_prompt("deduplicate_courses.txt")
    
    user_content = (
        f"{prompt_template}\n\n"
        f"Liste de courses à nettoyer (format JSON):\n"
        f"{json.dumps(courses, ensure_ascii=False, indent=2)}\n"
    )
    
    @retry_openai(max_attempts=3, base_delay=1.0)
    def _call_llm():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=3000,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": user_content}],
        )
    
    response = _call_llm()
    
    content = response.choices[0].message.content or "{}"
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        cleaned = content.strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                raise ValueError(
                    f"Impossible de parser la réponse JSON du LLM: {exc}\nContenu: {content[:500]}"
                ) from exc
        else:
            raise ValueError(
                f"Impossible de parser la réponse JSON du LLM: {exc}\nContenu: {content[:500]}"
            ) from exc
    
    cleaned_courses = data.get("courses") or data.get("items") or data.get("groceries") or []
    if isinstance(cleaned_courses, list):
        # Vérifie que le LLM a retourné des données valides
        is_valid, errors = validate_courses_list(cleaned_courses, strict=False)
        if not is_valid:
            print(f"   [WARN] Le LLM a retourné des données invalides: {', '.join(errors[:3])}")
            # Nettoie ce qui peut être sauvé
            cleaned_courses = [sanitize_course_item(item) for item in cleaned_courses]
        return cleaned_courses
    return courses  # Si erreur, on garde l'original


def complete_quantities_llm(
    courses: List[Dict[str, Any]], 
    recipes: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    # Demande au LLM de remplir les quantités manquantes en regardant les recettes
    if not courses:
        return []
    
    # Vérifie que les données sont valides avant d'appeler le LLM
    is_valid, errors = validate_courses_list(courses, strict=False)
    if not is_valid:
        raise ValueError(f"Données invalides avant appel LLM: {', '.join(errors)}")
    
    # Trouve les items sans quantités
    items_without_qty = [
        item for item in courses 
        if not item.get("Quantité") or item.get("Quantité") == "" or item.get("Quantité") == 0
    ]
    
    if not items_without_qty:
        return courses  # Déjà tout rempli
    
    prompt_template = _load_prompt("complete_quantities.txt")
    
    # Récupère les infos des recettes pour que le LLM puisse calculer les quantités
    recipes_context = []
    if recipes:
        for recipe in recipes:
            recipe_name = recipe.get("Nom") or recipe.get("title") or ""
            if not recipe_name:
                continue
            
            # Extrait les ingrédients avec leurs quantités
            ingredients_detailed = []
            ingredients_raw = recipe.get("ingredients") or []
            
            for ing in ingredients_raw:
                if isinstance(ing, dict):
                    ing_name = ing.get("name") or ing.get("nameClean") or ""
                    ing_amount = ing.get("amount")
                    ing_unit = ing.get("unit") or ""
                    if ing_name:
                        ingredients_detailed.append({
                            "name": ing_name,
                            "amount": ing_amount,
                            "unit": ing_unit,
                        })
                elif isinstance(ing, str):
                    # Juste un nom, pas de quantité
                    ingredients_detailed.append({"name": ing})
            
            recipe_info = {
                "Nom": recipe_name,
                "Lien": recipe.get("Lien") or recipe.get("sourceUrl") or "",
                "Temps": recipe.get("Temps") or recipe.get("readyMinutes") or "",
                "Portions": recipe.get("servings") or recipe.get("Portions") or 4,
                "Ingrédients": ingredients_detailed,
            }
            recipes_context.append(recipe_info)
    
    user_content = (
        f"{prompt_template}\n\n"
        f"Liste de courses avec quantités manquantes (format JSON):\n"
        f"{json.dumps(courses, ensure_ascii=False, indent=2)}\n"
    )
    
    if recipes_context:
        user_content += (
            f"\n\nRecettes associées (pour contexte) :\n"
            f"{json.dumps(recipes_context, ensure_ascii=False, indent=2)}\n"
        )
    
    @retry_openai(max_attempts=3, base_delay=1.0)
    def _call_llm():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=3000,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": user_content}],
        )
    
    response = _call_llm()
    
    content = response.choices[0].message.content or "{}"
    
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        cleaned = content.strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                raise ValueError(
                    f"Impossible de parser la réponse JSON du LLM: {exc}\nContenu: {content[:500]}"
                ) from exc
        else:
            raise ValueError(
                f"Impossible de parser la réponse JSON du LLM: {exc}\nContenu: {content[:500]}"
            ) from exc
    
    completed_courses = data.get("courses") or data.get("items") or data.get("groceries") or []
    # Accepter le résultat si c'est une liste valide, même si la longueur diffère
    # (le LLM peut fusionner des items pendant la complétion)
    if isinstance(completed_courses, list) and len(completed_courses) > 0:
        # Validation et nettoyage après appel LLM
        is_valid, errors = validate_courses_list(completed_courses, strict=False)
        if not is_valid:
            print(f"   [WARN] Validation post-LLM échouée: {', '.join(errors[:3])}")
            # Nettoyer les items invalides
            completed_courses = [sanitize_course_item(item) for item in completed_courses]
        return completed_courses
    return courses  # Fallback : retourne la liste originale si erreur