"""Push des recettes vers Notion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from integrations.notion.client import get_client
from integrations.notion.config import get_config
from integrations.notion.mappers import recipe_to_notion_properties
from integrations.notion.upsert import clear_cache, upsert_page
from notion_tools.notion_reader import get_database_properties, normalize_id


def push_recipes_to_notion(
    path: Path | str | None = None,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Push les recettes depuis menu.json vers Notion.
    
    Args:
        path: Chemin vers menu.json (défaut: data/menu.json)
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
    if not config.recipes_db_id:
        raise ValueError("NOTION_RECIPES_DB non configuré")
    
    # Charge les recettes
    recipes_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(recipes_data, list):
        raise ValueError(f"Le fichier {path} doit contenir une liste de recettes")
    
    if dry_run:
        print(f"[DRY-RUN] {len(recipes_data)} recettes à synchroniser")
        return {"n_created": 0, "n_updated": 0, "n_errors": 0}
    
    # Initialise
    client = get_client()
    normalized_db_id = normalize_id(config.recipes_db_id)
    if not normalized_db_id:
        raise ValueError(f"ID de base invalide : {config.recipes_db_id}")
    
    # Récupère le schéma
    schema = get_database_properties(client, normalized_db_id)
    
    # Debug : afficher les champs disponibles dans le schéma
    print(f"   📋 Champs disponibles dans Notion: {', '.join(schema.keys())}")
    # Afficher les champs de type files ou url
    image_fields = [name for name, defn in schema.items() if defn.get("type") in ("files", "url")]
    if image_fields:
        print(f"   🖼️  Champs de type files/url: {', '.join(image_fields)}")
    else:
        print(f"   ⚠️  Aucun champ de type files ou url trouvé dans le schéma")
    
    # Trouve la propriété titre
    title_prop = None
    for prop_name, prop_def in schema.items():
        if prop_def.get("type") == "title":
            title_prop = prop_name
            break
    
    if not title_prop:
        raise RuntimeError("Impossible de trouver une propriété titre dans la base Recettes")
    
    # Clear cache pour un run propre
    clear_cache()
    
    n_created = 0
    n_updated = 0
    n_errors = 0
    
    print(f"➡️  Synchronisation de {len(recipes_data)} recettes vers Notion...")
    
    for recipe in recipes_data:
        try:
            # Récupère le nom
            name = (
                recipe.get("Nom")
                or recipe.get("name")
                or recipe.get("Name")
                or recipe.get("title")
                or "Recette sans nom"
            )
            
            # Debug : vérifier si l'image est présente
            image = recipe.get("image") or recipe.get("Image") or recipe.get("imageUrl")
            if image:
                print(f"   📷 Recette '{name}' a une image: {str(image)[:50]}...")
            else:
                print(f"   ⚠️  Recette '{name}' sans image dans les données")
            
            # Convertit en propriétés Notion
            properties = recipe_to_notion_properties(recipe, schema)
            
            # Debug : vérifier si l'image a été ajoutée aux propriétés
            has_image_in_props = False
            for prop_name in ("Photo", "Image"):
                if prop_name in properties:
                    has_image_in_props = True
                    break
            if image and not has_image_in_props:
                print(f"   ⚠️  Image présente dans les données mais non ajoutée aux propriétés Notion")
            
            # Upsert
            created, updated, page_id = upsert_page(
                client,
                normalized_db_id,
                name,
                properties,
                title_prop,
            )
            
            if created:
                n_created += 1
            elif updated:
                n_updated += 1
                
        except Exception as e:
            n_errors += 1
            print(f"   ❌ Erreur pour '{name}': {e}")
    
    print(f"   ✅ {n_created} créé(s), {n_updated} mis à jour, {n_errors} erreur(s)")
    
    return {
        "n_created": n_created,
        "n_updated": n_updated,
        "n_errors": n_errors,
    }


def main() -> None:
    """CLI pour push_recipes_to_notion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Push les recettes vers Notion")
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Chemin vers menu.json (défaut: data/menu.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode dry-run (ne fait rien)",
    )
    args = parser.parse_args()
    
    try:
        result = push_recipes_to_notion(path=args.file, dry_run=args.dry_run)
        if args.dry_run:
            print(f"[DRY-RUN] Résultat: {result}")
    except Exception as e:
        print(f"Erreur: {e}")
        exit(1)


if __name__ == "__main__":
    main()

