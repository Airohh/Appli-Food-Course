# Pipeline principal : récupère des recettes, les sélectionne, génère la liste de courses
# Usage: python -m app.main --mode prod

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .config import (
    DATA_DIR,
    OPENAI_API_KEY,
    SPOONACULAR_API_KEY,
    SPOONACULAR_API_KEY2,
    USE_MOCK_DATA,
    N_RECIPES_FINAL,
)
from .llm import choose_recipes, consolidate_groceries_llm, deduplicate_courses_llm, complete_quantities_llm
from .shopping import consolidate_groceries, merge_courses, prepare_stock_lookup
from .spoonacular import get_candidate_recipes
from notion_tools.fetch.fetch_stock import fetch_stock as fetch_stock_from_notion


@dataclass
class PipelineOptions:
    mode: str
    dry_run: bool
    llm_enabled: bool
    llm_fallback: bool


PROJECT_ROOT = DATA_DIR.parent
DATA_DIR.mkdir(parents=True, exist_ok=True)
MENU_PATH = DATA_DIR / "menu.json"
GROCERIES_PATH = DATA_DIR / "groceries.json"
ACHATS_PATH = DATA_DIR / "achats_filtres.json"


def _print_diff(path: Path, data: object) -> None:
    details = ""
    if isinstance(data, list):
        new_len = len(data)
        old_len = None
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(existing, list):
                    old_len = len(existing)
            except Exception:
                old_len = None
        if old_len is not None:
            details = f"(ancien: {old_len}, nouveau: {new_len})"
        else:
            details = f"(nouveau: {new_len})"
    try:
        display_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = path
    print(f"   [DRY-RUN] {display_path} {details}".strip())


def _save_json(path: Path, data: object, options: PipelineOptions) -> None:
    if options.dry_run:
        _print_diff(path, data)
        return

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        display_path = path.relative_to(PROJECT_ROOT)
    except ValueError:
        display_path = path
    print(f"   Fichier mis à jour -> {display_path}")


def _stock_names(stock: Sequence[object]) -> List[str]:
    names: List[str] = []
    for item in stock:
        if isinstance(item, dict):
            name = (
                item.get("Aliment")
                or item.get("Name")
                or item.get("Nom")
                or item.get("name")
            )
        else:
            name = str(item)
        if not name:
            continue
        cleaned = str(name).strip()
        if cleaned:
            names.append(cleaned)
    # Enlève les doublons mais garde l'ordre
    seen = set()
    ordered: List[str] = []
    for name in names:
        lower = name.lower()
        if lower in seen:
            continue
        seen.add(lower)
        ordered.append(name)
    return ordered


def _enrich_with_ingredients(
    selected: List[Dict[str, Any]],
    candidates: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    # Ajoute les ingrédients détaillés aux recettes sélectionnées

    enriched: List[Dict[str, Any]] = []
    candidate_list = list(candidates)

    for recipe in selected:
        title = (recipe.get("Nom") or recipe.get("title") or "").lower().strip()
        url = recipe.get("Lien") or recipe.get("sourceUrl")

        match: Dict[str, Any] | None = None
        for candidate in candidate_list:
            cand_title = (candidate.get("title") or "").lower().strip()
            cand_url = candidate.get("sourceUrl")
            if url and cand_url and url == cand_url:
                match = candidate
                break
            if title and cand_title and (title == cand_title or title in cand_title or cand_title in title):
                match = candidate
                break

        if match and match.get("ingredients"):
            item = dict(recipe)
            item.setdefault("Nom", recipe.get("Nom") or recipe.get("title"))
            item.setdefault("Lien", recipe.get("Lien") or match.get("sourceUrl"))
            item.setdefault("Temps", recipe.get("Temps") or match.get("readyMinutes"))
            item.setdefault("Calories (~)", recipe.get("Calories (~)") or recipe.get("Calories") or (match.get("nutrition") or {}).get("calories"))
            item.setdefault("Protéines (g)", recipe.get("Protéines (g)") or recipe.get("Proteines") or (match.get("nutrition") or {}).get("protein"))
            # Ajoute l'image si disponible
            if match.get("image"):
                item["Image"] = match.get("image")
            item["ingredients"] = match.get("ingredients")
            enriched.append(item)
        else:
            enriched.append(recipe)

    return enriched


def _has_quantities(groceries: List[Dict[str, Any]]) -> bool:
    for item in groceries:
        qty = item.get("Quantité")
        if qty is None:
            continue
        if isinstance(qty, (int, float)) and qty > 0:
            return True
        if isinstance(qty, str) and qty.strip():
            return True
    return False


def _print_summary(recipes: List[Dict[str, Any]]) -> None:
    if not recipes:
        return
    print("\nRésumé rapide :")
    for idx, recipe in enumerate(recipes, start=1):
        name = recipe.get("Nom") or recipe.get("title") or "Recette"
        time = recipe.get("Temps") or recipe.get("readyMinutes") or "?"
        calories = (
            recipe.get("Calories (~)")
            or recipe.get("Calories")
            or (recipe.get("nutrition") or {}).get("calories")
        )
        protein = (
            recipe.get("Protéines (g)")
            or recipe.get("Proteines")
            or (recipe.get("nutrition") or {}).get("protein")
        )
        print(f"  {idx}. {name} - {time} min | ~{calories} kcal | ~{protein} g protéines")


def build_pipeline(
    *,
    query: str | None,
    stock_path: Path,
    options: PipelineOptions,
    refresh_stock: bool,
    mealplan_start_date: str | None = None,
) -> None:
    # Vérifie les clés API nécessaires
    if options.llm_enabled and not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY manquant. Ajoute la clé dans .env ou lance avec --no-llm."
        )

    if options.mode == "prod":
        if not SPOONACULAR_API_KEY and not SPOONACULAR_API_KEY2:
            raise RuntimeError("Mode prod : au moins une clé SPOONACULAR_API_KEY est requise.")
    else:
        os.environ.setdefault("USE_MOCK_DATA", "true")

    if not stock_path.is_absolute():
        stock_path = (PROJECT_ROOT / stock_path).resolve()

    print("Récupération des recettes...")
    candidates = get_candidate_recipes(query=query)
    print(f"   {len(candidates)} recettes trouvées")

    if refresh_stock and options.mode == "prod":
        print("Rafraîchissement du stock depuis Notion...")
        try:
            stock_snapshot = fetch_stock_from_notion()
        except Exception as exc:  # pragma: no cover - dépend Notion
            print(f"   Impossible de rafraîchir le stock : {exc}")
        else:
            if not options.dry_run:
                try:
                    stock_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception:
                    pass
                stock_path.write_text(
                    json.dumps(stock_snapshot, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            try:
                display_path = stock_path.relative_to(PROJECT_ROOT)
            except ValueError:
                display_path = stock_path
            print(f"   Stock mis à jour -> {display_path}")
    elif refresh_stock:
        print("   (Rafraîchissement ignoré en mode mock)")

    print("Chargement du stock local...")
    stock = prepare_stock_lookup(stock_path)
    if stock:
        try:
            display_path = stock_path.relative_to(PROJECT_ROOT)
        except ValueError:
            display_path = stock_path
        print(f"   {len(stock)} éléments dans {display_path}")
    else:
        print("   (Aucun stock local, lance fetch_stock.py si besoin)")

    stock_names = _stock_names(stock)

    if options.llm_enabled:
        print("Sélection des recettes via LLM...")
        selected = choose_recipes(candidates, stock_names)
        if not isinstance(selected, list):
            raise RuntimeError("Le LLM n'a pas retourné de liste de recettes.")
    else:
        print("LLM désactivé, sélection simple")
        selected = candidates[:N_RECIPES_FINAL]

    print(f"   {len(selected)} recettes retenues")

    selected = _enrich_with_ingredients(selected, candidates)
    _save_json(MENU_PATH, selected, options)

    print("Consolidation de la liste de courses...")
    groceries = consolidate_groceries(selected, stock=stock)

    if options.llm_enabled and options.llm_fallback and not _has_quantities(groceries):
        print("   (Pas de quantités, essai avec le LLM)")
        try:
            groceries_llm = consolidate_groceries_llm(selected, stock_names)
        except Exception as exc:  # pragma: no cover - dépend du service externe
            print(f"   Impossible : {exc}")
        else:
            if groceries_llm:
                groceries = groceries_llm
                print("   Quantités ajoutées via LLM")

    _save_json(GROCERIES_PATH, groceries, options)

    print("Fusion finale des achats...")
    try:
        merged, stats = merge_courses(
            groceries,
            stock=stock,
            fuzzy_threshold=0.88,
            return_stats=True,
        )
        print(
            f"   {stats['input']} entrées -> {stats['output']} après fusion"
            f" ({stats['skipped_stock']} déjà en stock)"
        )
    except Exception as exc:
        print(f"   Erreur lors de la fusion : {exc}")
        # On continue avec la liste non fusionnée plutôt que de planter
        merged = groceries
        print("   (Utilisation de la liste non fusionnée)")
    
    if options.llm_enabled and len(merged) > 0:
        print("Nettoyage et déduplication via LLM...")
        try:
            cleaned = deduplicate_courses_llm(merged)
            if cleaned and isinstance(cleaned, list) and len(cleaned) > 0:
                # Même si la longueur est pareille, le LLM peut avoir normalisé les noms
                original_len = len(merged)
                merged = cleaned
                if len(cleaned) < original_len:
                    print(f"   Liste nettoyée : {len(merged)} items (avant : {original_len})")
                else:
                    print(f"   Liste normalisée : {len(merged)} items")
            else:
                print("   (Aucun changement)")
        except Exception as exc:  # pragma: no cover - dépend du service externe
            print(f"   Impossible : {exc}")
            print("   (Utilisation de la liste consolidée)")
        
        # Compléter les quantités manquantes
        items_without_qty = [
            item for item in merged 
            if not item.get("Quantité") or item.get("Quantité") == "" or item.get("Quantité") == 0
        ]
        if items_without_qty:
            print(f"Complétion des quantités manquantes via LLM ({len(items_without_qty)} items)...")
            try:
                completed = complete_quantities_llm(merged, selected)
                if completed and isinstance(completed, list) and len(completed) > 0:
                    merged = completed
                    completed_count = len([
                        item for item in merged 
                        if item.get("Quantité") and item.get("Quantité") != "" and item.get("Quantité") != 0
                    ])
                    print(f"   {completed_count}/{len(merged)} items ont maintenant une quantité")
                else:
                    print("   (Aucune quantité complétée)")
            except Exception as exc:  # pragma: no cover - dépend du service externe
                print(f"   Impossible : {exc}")
                print("   (Utilisation de la liste sans quantités complétées)")
    
    _save_json(ACHATS_PATH, merged, options)

    # Synchronisation Notion (si activée)
    if not options.dry_run:
        try:
            from integrations.notion.config import get_config
            
            notion_config = get_config()
            if notion_config.sync_enabled:
                print("\n🔄 Synchronisation vers Notion...")
                
                try:
                    from integrations.notion.recipes import push_recipes_to_notion
                    from integrations.notion.mealplan import push_mealplan_to_notion
                    from integrations.notion.groceries import push_groceries_to_notion
                    
                    # Push recettes
                    print("   📝 Push des recettes...")
                    recipes_result = push_recipes_to_notion(path=MENU_PATH, dry_run=False)
                    
                    # Push meal plan (si DB configurée)
                    if notion_config.mealplan_db_id:
                        print("   📅 Push du plan de repas...")
                        from datetime import date
                        start_date = None
                        if mealplan_start_date:
                            start_date = date.fromisoformat(mealplan_start_date)
                        mealplan_result = push_mealplan_to_notion(
                            path=MENU_PATH,
                            start_date=start_date,
                            dry_run=False
                        )
                    else:
                        print("   ⚠️  Meal Plan DB non configurée, skip")
                    
                    # Push courses
                    print("   🛒 Push de la liste de courses...")
                    groceries_result = push_groceries_to_notion(path=ACHATS_PATH, dry_run=False)
                    
                    print("   ✅ Synchronisation Notion terminée")
                except Exception as exc:
                    print(f"   ❌ Erreur lors de la synchronisation Notion : {exc}")
                    # On continue même si Notion échoue
            else:
                print("\n   (Synchronisation Notion désactivée, NOTION_SYNC_ENABLED=false)")
        except Exception as exc:
            # Si l'import échoue (module non installé, etc.), on continue
            print(f"\n   ⚠️  Impossible de charger l'intégration Notion : {exc}")

    _print_summary(selected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline complet recettes/courses")
    parser.add_argument(
        "--mode",
        choices=["mock", "prod"],
        required=True,
        help="Mode d'exécution (mock: APIs simulées, prod: appels réels)",
    )
    parser.add_argument("--query", help="Terme de recherche Spoonacular", default=None)
    parser.add_argument(
        "--stock-path",
        help="Chemin vers le snapshot de stock JSON",
        default=DATA_DIR / "stock.json",
        type=Path,
    )
    parser.add_argument(
        "--no-llm-fallback",
        help="N'utilise pas le LLM pour inférer les quantités si elles manquent",
        action="store_true",
    )
    parser.add_argument(
        "--refresh-stock",
        help="Tire automatiquement le stock depuis Notion avant de lancer le pipeline",
        action="store_true",
    )
    parser.add_argument(
        "--dry-run",
        help="N'écrit aucun fichier et n'appelle pas Notion, affiche les diffs",
        action="store_true",
    )
    parser.add_argument(
        "--no-llm",
        help="Désactive la sélection et la consolidation LLM",
        action="store_true",
    )
    parser.add_argument(
        "--mealplan-start-date",
        type=str,
        default=None,
        help="Date de début pour le plan de repas (format: YYYY-MM-DD, défaut: aujourd'hui)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    options = PipelineOptions(
        mode=args.mode,
        dry_run=args.dry_run,
        llm_enabled=not args.no_llm,
        llm_fallback=not args.no_llm_fallback,
    )

    build_pipeline(
        query=args.query,
        stock_path=args.stock_path,
        options=options,
        refresh_stock=args.refresh_stock,
        mealplan_start_date=args.mealplan_start_date,
    )


if __name__ == "__main__":
    main()

