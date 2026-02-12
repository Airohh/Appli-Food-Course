# Vérifie que les données sont correctes avant et après les appels LLM

from __future__ import annotations

from typing import Any, Dict, List


def validate_course_item(item: Dict[str, Any], strict: bool = False) -> tuple[bool, str]:
    # Vérifie qu'un item de course est valide
    if not isinstance(item, dict):
        return False, f"Item doit être un dictionnaire, reçu: {type(item)}"
    
    # Champs requis
    if "Aliment" not in item:
        return False, "Champ 'Aliment' manquant"
    
    aliment = item.get("Aliment")
    if not aliment or (isinstance(aliment, str) and not aliment.strip()):
        return False, "Champ 'Aliment' vide ou invalide"
    
    # Champs optionnels mais avec validation si présents
    qty = item.get("Quantité")
    if qty is not None:
        if not isinstance(qty, (int, float, str)):
            return False, f"Quantité doit être un nombre ou chaîne, reçu: {type(qty)}"
        if isinstance(qty, (int, float)) and qty < 0:
            return False, f"Quantité ne peut pas être négative: {qty}"
    
    unit = item.get("Unité")
    if unit is not None and not isinstance(unit, str):
        return False, f"Unité doit être une chaîne, reçu: {type(unit)}"
    
    # Validation stricte
    if strict:
        if qty is None or qty == "" or qty == 0:
            return False, "Quantité manquante (validation stricte)"
        if not unit or not unit.strip():
            return False, "Unité manquante (validation stricte)"
    
    return True, ""


def validate_courses_list(courses: List[Dict[str, Any]], strict: bool = False) -> tuple[bool, List[str]]:
    # Vérifie qu'une liste de courses est valide
    if not isinstance(courses, list):
        return False, [f"courses doit être une liste, reçu: {type(courses)}"]
    
    errors: List[str] = []
    
    for idx, item in enumerate(courses):
        is_valid, error = validate_course_item(item, strict=strict)
        if not is_valid:
            errors.append(f"Item {idx}: {error}")
    
    return len(errors) == 0, errors


def validate_recipe_item(recipe: Dict[str, Any]) -> tuple[bool, str]:
    # Vérifie qu'une recette est valide (au moins un nom)
    if not isinstance(recipe, dict):
        return False, f"Recipe doit être un dictionnaire, reçu: {type(recipe)}"
    
    # Il faut au moins un nom
    name = recipe.get("Nom") or recipe.get("title") or recipe.get("name")
    if not name or (isinstance(name, str) and not name.strip()):
        return False, "Recette doit avoir un nom (champ 'Nom', 'title' ou 'name')"
    
    return True, ""


def validate_recipes_list(recipes: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
    # Vérifie qu'une liste de recettes est valide
    if not isinstance(recipes, list):
        return False, [f"recipes doit être une liste, reçu: {type(recipes)}"]
    
    errors: List[str] = []
    
    for idx, recipe in enumerate(recipes):
        is_valid, error = validate_recipe_item(recipe)
        if not is_valid:
            errors.append(f"Recette {idx}: {error}")
    
    return len(errors) == 0, errors


def sanitize_course_item(item: Dict[str, Any]) -> Dict[str, Any]:
    # Nettoie un item de course (enlève les espaces, convertit les types, etc.)
    cleaned = dict(item)
    
    # Nettoie les champs
    if "Aliment" in cleaned:
        aliment = cleaned["Aliment"]
        if isinstance(aliment, str):
            cleaned["Aliment"] = aliment.strip()
    
    if "Unité" in cleaned:
        unit = cleaned["Unité"]
        if isinstance(unit, str):
            cleaned["Unité"] = unit.strip()
        elif unit is None:
            cleaned["Unité"] = ""
    
    if "Quantité" in cleaned:
        qty = cleaned["Quantité"]
        if qty == "" or qty is None:
            cleaned["Quantité"] = ""
        elif isinstance(qty, str):
            try:
                # Essaie de convertir en nombre
                cleaned["Quantité"] = float(qty)
            except ValueError:
                cleaned["Quantité"] = qty.strip()
    
    # Ajoute les champs manquants avec des valeurs vides
    if "Recettes" not in cleaned:
        cleaned["Recettes"] = ""
    if "Categorie" not in cleaned:
        cleaned["Categorie"] = ""
    if "Notes" not in cleaned:
        cleaned["Notes"] = ""
    
    return cleaned

