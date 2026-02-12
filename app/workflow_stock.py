"""Workflow pour soustraire le stock quand une recette est terminée."""

from __future__ import annotations

import argparse
from typing import Any, Dict

from integrations.notion.client import get_client
from notion_tools.notion_reader import normalize_id

from .config import NOTION_RECIPES_DB, NOTION_STOCK_DB
from .spoonacular import get_recipe_ingredients_with_quantities
from .shopping import subtract_stock_from_groceries
from .utils import extract_spoon_id_from_url


def subtract_stock_when_recipe_completed(
    recipe_page_id: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Quand une recette est marquée "Terminée" = true :
    1. Récupère les ingrédients de la recette
    2. Soustrait les quantités du stock
    3. Met à jour le stock dans Notion
    
    Args:
        recipe_page_id: ID de la page recette dans Notion
        dry_run: Si True, ne fait rien, juste valide
    
    Returns:
        Dict avec les résultats
    """
    client = get_client()
    recipes_db_id = normalize_id(NOTION_RECIPES_DB)
    stock_db_id = normalize_id(NOTION_STOCK_DB)
    
    if not recipes_db_id:
        raise RuntimeError("Base Recettes non configurée")
    if not stock_db_id:
        raise RuntimeError("Base Stock non configurée")
    
    # Récupérer la recette
    recipe_page = client.pages.retrieve(page_id=recipe_page_id)
    props = recipe_page.get("properties", {})
    
    # Vérifier que Terminée = true ou État = "Terminée"
    # Essayer d'abord "Terminée" (checkbox), puis "État" (select)
    terminee_prop = props.get("Terminée") or props.get("Completed") or props.get("Done")
    etat_prop = props.get("État") or props.get("Etat") or props.get("Status") or props.get("Statut")
    
    is_completed = False
    
    # Vérifier checkbox "Terminée"
    if terminee_prop and isinstance(terminee_prop, dict):
        is_completed = terminee_prop.get("checkbox", False)
    elif isinstance(terminee_prop, bool):
        is_completed = terminee_prop
    
    # Vérifier select "État" = "Terminée" ou similaire
    if not is_completed and etat_prop:
        if isinstance(etat_prop, dict):
            etat_value = etat_prop.get("select", {}).get("name", "")
            if etat_value:
                etat_lower = etat_value.lower()
                is_completed = "termine" in etat_lower or "completed" in etat_lower or "done" in etat_lower
        elif isinstance(etat_prop, str):
            etat_lower = etat_prop.lower()
            is_completed = "termine" in etat_lower or "completed" in etat_lower or "done" in etat_lower
    
    if not is_completed:
        return {"error": "Recette non terminée", "recipe_id": recipe_page_id}
    
    # Récupérer spoon_id et portions
    link_prop = props.get("Lien") or props.get("link")
    url = None
    if link_prop and isinstance(link_prop, dict):
        url = link_prop.get("url")
    elif isinstance(link_prop, str):
        url = link_prop
    
    spoon_id = extract_spoon_id_from_url(url) if url else None
    
    portions_prop = props.get("Portions") or props.get("Portion")
    portions = 1
    if portions_prop and isinstance(portions_prop, dict):
        portions_num = portions_prop.get("number")
        if portions_num is not None:
            portions = int(portions_num)
    elif isinstance(portions_prop, (int, float)):
        portions = int(portions_prop)
    
    if not spoon_id:
        return {
            "error": "Impossible de récupérer l'ID Spoonacular",
            "recipe_id": recipe_page_id,
            "url": url,
        }
    
    # Récupérer les ingrédients avec quantités
    print(f"🥘 Récupération des ingrédients pour la recette (portions: {portions})...")
    try:
        ingredients = get_recipe_ingredients_with_quantities(
            spoon_id,
            portions_multiplier=portions
        )
    except Exception as e:
        return {
            "error": f"Erreur récupération ingrédients: {e}",
            "recipe_id": recipe_page_id,
            "spoon_id": spoon_id,
        }
    
    print(f"   {len(ingredients)} ingrédient(s) trouvé(s)")
    
    # Récupérer le stock actuel
    print("📦 Récupération du stock...")
    from notion_tools.fetch.fetch_stock import fetch_stock
    stock = fetch_stock()
    print(f"   {len(stock)} article(s) en stock")
    
    # Convertir les ingrédients en format courses
    groceries = [
        {
            "Aliment": ing.get("name"),
            "Quantité": ing.get("amount"),
            "Unité": ing.get("unit"),
        }
        for ing in ingredients
    ]
    
    # Soustraire du stock
    print("➖ Soustraction du stock...")
    updated_groceries = subtract_stock_from_groceries(groceries, stock)
    
    # Calculer ce qui a été soustrait
    subtracted_items = []
    for orig, updated in zip(groceries, updated_groceries):
        orig_qty = orig.get("Quantité", 0)
        updated_qty = updated.get("Quantité", 0)
        if updated_qty < orig_qty:
            subtracted_items.append({
                "aliment": orig.get("Aliment"),
                "soustrait": orig_qty - updated_qty,
                "unité": orig.get("Unité"),
            })
    
    # Mettre à jour le stock dans Notion
    if not dry_run and subtracted_items:
        print("📤 Mise à jour du stock dans Notion...")
        from notion_tools.notion_reader import get_database_properties
        from integrations.notion.upsert import upsert_page
        from integrations.notion.mappers import grocery_to_notion_properties
        
        schema = get_database_properties(client, stock_db_id)
        
        # Trouver la propriété titre
        title_prop = None
        for prop_name, prop_def in schema.items():
            if prop_def.get("type") == "title":
                title_prop = prop_name
                break
        
        if not title_prop:
            print("   ⚠️  Impossible de trouver la propriété titre dans le stock")
            updated_count = 0
        else:
            updated_count = 0
            for item in subtracted_items:
                try:
                    # Trouver l'item dans le stock
                    stock_item = None
                    for s in stock:
                        if isinstance(s, dict):
                            stock_name = s.get("Aliment") or s.get("Name") or ""
                            if stock_name == item["aliment"]:
                                stock_item = s
                                break
                    
                    if stock_item:
                        # Calculer la nouvelle quantité
                        current_qty = stock_item.get("Quantité") or stock_item.get("Quantity") or 0
                        new_qty = max(current_qty - item["soustrait"], 0)
                        
                        # Préparer les propriétés
                        stock_update = {
                            "Aliment": item["aliment"],
                            "Quantité": new_qty,
                            "Unité": item["unité"],
                            "Catégorie": stock_item.get("Categorie") or stock_item.get("Category") or "",
                        }
                        properties = grocery_to_notion_properties(stock_update, schema)
                        
                        # Upsert
                        upsert_page(client, stock_db_id, item["aliment"], properties, title_prop)
                        updated_count += 1
                except Exception as e:
                    print(f"   ⚠️ Erreur mise à jour {item['aliment']}: {e}")
            
            if title_prop:
                print(f"   ✅ {updated_count} article(s) mis à jour dans le stock")
    
    return {
        "ingredients_processed": len(ingredients),
        "stock_updated": len(subtracted_items),
        "subtracted_items": subtracted_items,
        "recipe_id": recipe_page_id,
        "spoon_id": spoon_id,
    }


def main() -> None:
    """CLI pour soustraire le stock d'une recette terminée."""
    parser = argparse.ArgumentParser(
        description="Soustrait le stock quand une recette est terminée"
    )
    parser.add_argument(
        "--recipe-id",
        type=str,
        required=True,
        help="ID de la page recette dans Notion",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode dry-run (ne fait rien)",
    )
    args = parser.parse_args()
    
    try:
        result = subtract_stock_when_recipe_completed(
            recipe_page_id=args.recipe_id,
            dry_run=args.dry_run,
        )
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
            exit(1)
        print(f"\n✅ Résultat: {result}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

