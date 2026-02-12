"""Push du plan de repas vers Notion."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from integrations.notion.client import get_client
from integrations.notion.config import get_config
from integrations.notion.mappers import mealplan_to_notion_properties
from integrations.notion.upsert import clear_cache, resolve_relation_by_title, upsert_page
from notion_tools.notion_reader import get_database_properties, normalize_id


def push_mealplan_to_notion(
    path: Path | str | None = None,
    start_date: Optional[date] = None,
    meal_types: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Crée un plan de repas dans Notion à partir de menu.json.
    
    Args:
        path: Chemin vers menu.json (défaut: data/menu.json)
        start_date: Date de début (défaut: aujourd'hui)
        meal_types: Types de repas à alterner (défaut: ["Déjeuner", "Dîner"])
        dry_run: Si True, ne fait rien, juste valide
    
    Returns:
        Dict avec n_created, n_updated, n_errors
    """
    from app.config import DATA_DIR
    
    if path is None:
        path = DATA_DIR / "menu.json"
    elif isinstance(path, str):
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    
    config = get_config()
    if not config.mealplan_db_id and not dry_run:
        raise ValueError("NOTION_MEALPLAN_DB non configuré")
    
    if not config.mealplan_db_id and dry_run:
        print("[DRY-RUN] NOTION_MEALPLAN_DB non configuré, skip")
        return {"n_created": 0, "n_updated": 0, "n_errors": 0}
    
    if not config.recipes_db_id:
        raise ValueError("NOTION_RECIPES_DB requis pour les relations")
    
    # Charge les recettes
    recipes_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(recipes_data, list):
        raise ValueError(f"Le fichier {path} doit contenir une liste de recettes")
    
    if not recipes_data:
        print("   ⚠️ Aucune recette dans menu.json")
        return {"n_created": 0, "n_updated": 0, "n_errors": 0}
    
    # Date de début
    if start_date is None:
        start_date = date.today()
    
    # Types de repas
    if meal_types is None:
        # Valeurs par défaut qui correspondent aux options communes dans Notion
        # Le code s'adaptera automatiquement aux options disponibles dans la base
        meal_types = ["Déjeuner", "Dîner"]
    
    if dry_run:
        print(f"[DRY-RUN] {len(recipes_data)} recettes → plan de repas à partir du {start_date}")
        return {"n_created": 0, "n_updated": 0, "n_errors": 0}
    
    # Initialise
    client = get_client()
    normalized_mealplan_db_id = normalize_id(config.mealplan_db_id)
    normalized_recipes_db_id = normalize_id(config.recipes_db_id)
    
    if not normalized_mealplan_db_id:
        raise ValueError(f"ID de base Meal Plan invalide : {config.mealplan_db_id}")
    if not normalized_recipes_db_id:
        raise ValueError(f"ID de base Recettes invalide : {config.recipes_db_id}")
    
    # Récupère le schéma
    try:
        schema = get_database_properties(client, normalized_mealplan_db_id)
    except Exception as e:
        error_msg = str(e)
        if "Could not find database" in error_msg or "NotFoundError" in error_msg:
            raise ValueError(
                f"Base Meal Plan introuvable (ID: {config.mealplan_db_id}). "
                "Vérifie que:\n"
                "  1. L'ID de la base est correct dans NOTION_MEALPLAN_DB\n"
                "  2. La base est partagée avec ton intégration Notion\n"
                "  3. L'intégration a les permissions nécessaires"
            ) from e
        raise
    
    # Trouve les propriétés
    title_prop = None
    for prop_name, prop_def in schema.items():
        if prop_def.get("type") == "title":
            title_prop = prop_name
            break
    
    if not title_prop:
        raise RuntimeError("Impossible de trouver une propriété titre dans la base Meal Plan")
    
    # Diagnostic : vérifie les propriétés disponibles
    date_prop = None
    type_prop = None
    recipe_prop = None
    for prop_name, prop_def in schema.items():
        prop_type = prop_def.get("type")
        if prop_type == "date":
            date_prop = prop_name
        elif prop_type == "select":
            # Cherche une propriété select qui pourrait être le type de repas
            # Priorité : "Type", puis "Jour", puis toute autre propriété select
            if prop_name == "Type":
                type_prop = prop_name
            elif prop_name in ("Jour", "Meal type", "type", "Repas") and type_prop is None:
                type_prop = prop_name
            elif type_prop is None:
                type_prop = prop_name
        elif prop_type == "relation":
            # Cherche "Recettes" (pluriel) ou "Recette" (singulier)
            if prop_name in ("Recettes", "Recette", "Recipe", "recette") or recipe_prop is None:
                recipe_prop = prop_name
    
    # Affiche un avertissement si des propriétés manquent
    missing = []
    if not date_prop:
        missing.append("Date (type: date)")
    if not type_prop:
        missing.append("Type (type: select, nom: 'Type' ou 'Meal type')")
    if not recipe_prop:
        missing.append("Recette (type: relation, nom: 'Recette' ou 'Recipe')")
    
    if missing:
        print(f"   ⚠️  Propriétés manquantes dans la base Meal Plan: {', '.join(missing)}")
        available_props = [f"{name} ({def_.get('type')})" for name, def_ in schema.items()]
        print(f"   📋 Propriétés disponibles: {', '.join(available_props)}")
    
    # Clear cache
    clear_cache()
    
    n_created = 0
    n_updated = 0
    n_errors = 0
    
    print(f"➡️  Création du plan de repas à partir du {start_date}...")
    
    current_date = start_date
    meal_type_index = 0
    
    for recipe in recipes_data:
        try:
            # Récupère le nom de la recette
            recipe_name = (
                recipe.get("Nom")
                or recipe.get("name")
                or recipe.get("Name")
                or recipe.get("title")
                or "Recette sans nom"
            )
            
            # Résout la relation vers la recette
            recipe_page_id = resolve_relation_by_title(
                client,
                normalized_recipes_db_id,
                recipe_name,
            )
            
            if not recipe_page_id:
                print(f"   ⚠️ Recette '{recipe_name}' non trouvée dans Notion, création sans relation")
            
            # Type de repas (alterne)
            meal_type = meal_types[meal_type_index % len(meal_types)]
            meal_type_index += 1
            
            # Crée l'entrée
            entry = {
                "date": current_date.isoformat(),
                "meal_type": meal_type,
                "recipe_name": recipe_name,
            }
            
            properties = mealplan_to_notion_properties(
                entry,
                schema,
                recipe_page_id=recipe_page_id,
            )
            
            # Debug : affiche les propriétés qui seront synchronisées (seulement pour la première recette)
            if n_created == 0 and n_updated == 0:
                print(f"   🔍 Propriétés à synchroniser: {list(properties.keys())}")
                if not properties:
                    print(f"   ⚠️  Aucune propriété trouvée ! Vérifiez le schéma de votre base.")
            
            # Titre pour l'upsert (date + type + recette)
            title = f"{current_date.strftime('%Y-%m-%d')} - {meal_type} - {recipe_name}"
            
            # Upsert
            created, updated, page_id = upsert_page(
                client,
                normalized_mealplan_db_id,
                title,
                properties,
                title_prop,
            )
            
            if created:
                n_created += 1
            elif updated:
                n_updated += 1
            
            # Passe au repas suivant (même jour si seulement 2 types, sinon jour suivant)
            if meal_type_index % len(meal_types) == 0:
                current_date += timedelta(days=1)
                
        except Exception as e:
            n_errors += 1
            print(f"   ❌ Erreur pour '{recipe_name}': {e}")
    
    print(f"   ✅ {n_created} créé(s), {n_updated} mis à jour, {n_errors} erreur(s)")
    
    return {
        "n_created": n_created,
        "n_updated": n_updated,
        "n_errors": n_errors,
    }


def main() -> None:
    """CLI pour push_mealplan_to_notion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Push le plan de repas vers Notion")
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Chemin vers menu.json (défaut: data/menu.json)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Date de début (format: YYYY-MM-DD, défaut: aujourd'hui)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode dry-run (ne fait rien)",
    )
    args = parser.parse_args()
    
    start_date = None
    if args.start_date:
        start_date = date.fromisoformat(args.start_date)
    
    try:
        result = push_mealplan_to_notion(
            path=args.file,
            start_date=start_date,
            dry_run=args.dry_run,
        )
        if args.dry_run:
            print(f"[DRY-RUN] Résultat: {result}")
    except Exception as e:
        print(f"Erreur: {e}")
        exit(1)


if __name__ == "__main__":
    main()

