"""Workflow pour proposer des recettes dans Notion."""

from __future__ import annotations

import sys
import codecs

# Forcer UTF-8 pour la console Windows
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

import argparse
from typing import Any, Dict, List

from integrations.notion.recipes import push_recipes_to_notion
from integrations.notion.client import get_client
from notion_tools.notion_reader import export_database, normalize_id, get_database_properties

from .config import NOTION_GROCERIES_DB, NOTION_RECIPES_DB, NOTION_RECIPES_VIEW_URL, NOTION_STOCK_DB
from .spoonacular import get_candidate_recipes
from .utils import notify_ntfy, week_label


def archive_old_recipes(
    current_semaine: str,
    dry_run: bool = False
) -> int:
    """
    Archive les recettes qui ne sont pas de la semaine actuelle.
    
    Args:
        current_semaine: Label de la semaine actuelle (ex: "Semaine 46 – 2025")
        dry_run: Si True, ne fait rien, juste compte
    
    Returns:
        Nombre de recettes archivées
    """
    client = get_client()
    db_id = normalize_id(NOTION_RECIPES_DB)
    if not db_id:
        print("   ⚠️  Base Recettes non configurée")
        return 0
    
    pages = export_database(client, db_id)
    
    archived = 0
    for page in pages:
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            # Gérer select ou multi_select
            if "select" in semaine_prop:
                semaine_value = semaine_prop.get("select", {}).get("name")
            elif "multi_select" in semaine_prop:
                multi_values = semaine_prop.get("multi_select", [])
                if multi_values and isinstance(multi_values, list):
                    # Prendre la première valeur
                    semaine_value = multi_values[0].get("name") if isinstance(multi_values[0], dict) else str(multi_values[0])
        elif isinstance(semaine_prop, (str, list)):
            if isinstance(semaine_prop, list) and len(semaine_prop) > 0:
                semaine_value = semaine_prop[0] if isinstance(semaine_prop[0], str) else str(semaine_prop[0])
            else:
                semaine_value = str(semaine_prop)
        
        # Si pas de semaine ou semaine différente → archiver
        if semaine_value != current_semaine:
            if not dry_run:
                try:
                    page_id = page.get("id")
                    if not page_id:
                        continue
                    
                    # Option 1: Marquer comme archivée (si propriété existe)
                    archived_prop_name = None
                    schema = get_database_properties(client, db_id)
                    for prop_name, prop_def in schema.items():
                        if prop_def.get("type") == "checkbox":
                            prop_lower = prop_name.lower()
                            if "archiv" in prop_lower or "archive" in prop_lower:
                                archived_prop_name = prop_name
                                break
                    
                    if archived_prop_name:
                        client.pages.update(
                            page_id=page_id,
                            properties={archived_prop_name: {"checkbox": True}}
                        )
                    else:
                        # Option 2: Archiver la page Notion
                        client.pages.update(page_id=page_id, archived=True)
                    archived += 1
                except Exception as e:
                    print(f"   ⚠️ Erreur archivage recette {page.get('id', 'unknown')}: {e}")
            else:
                archived += 1
    
    return archived


def transfer_purchased_to_stock(
    semaine_label: str | None = None,
    dry_run: bool = False
) -> int:
    """
    Transfère les courses achetées (Acheté = true) vers le stock.
    
    Args:
        semaine_label: Label de la semaine (défaut: semaine actuelle)
        dry_run: Si True, ne fait rien, juste compte
    
    Returns:
        Nombre d'articles transférés
    """
    if semaine_label is None:
        semaine_label = week_label()
    
    client = get_client()
    groceries_db_id = normalize_id(NOTION_GROCERIES_DB)
    stock_db_id = normalize_id(NOTION_STOCK_DB)
    
    if not groceries_db_id:
        print("   ⚠️  Base Courses non configurée")
        return 0
    if not stock_db_id:
        print("   ⚠️  Base Stock non configurée")
        return 0
    
    # Récupérer les courses de la semaine
    pages = export_database(client, groceries_db_id)
    
    transferred = 0
    for page in pages:
        # Vérifier Semaine
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            # Gérer select ou multi_select
            if "select" in semaine_prop:
                semaine_value = semaine_prop.get("select", {}).get("name")
            elif "multi_select" in semaine_prop:
                multi_values = semaine_prop.get("multi_select", [])
                if multi_values and isinstance(multi_values, list):
                    # Prendre la première valeur
                    semaine_value = multi_values[0].get("name") if isinstance(multi_values[0], dict) else str(multi_values[0])
        elif isinstance(semaine_prop, (str, list)):
            if isinstance(semaine_prop, list) and len(semaine_prop) > 0:
                semaine_value = semaine_prop[0] if isinstance(semaine_prop[0], str) else str(semaine_prop[0])
            else:
                semaine_value = str(semaine_prop)
        if semaine_value != semaine_label:
            continue
        
        # Vérifier Acheté = true
        acheté_prop = page.get("Acheté") or page.get("Achete") or page.get("Purchased")
        is_purchased = False
        if acheté_prop and isinstance(acheté_prop, dict):
            is_purchased = acheté_prop.get("checkbox", False)
        elif isinstance(acheté_prop, bool):
            is_purchased = acheté_prop
        
        if not is_purchased:
            continue
        
        # Récupérer les infos
        name = (
            page.get("Aliment")
            or page.get("Article")
            or page.get("Name")
            or page.get("Nom")
            or ""
        )
        qty = page.get("Quantité") or page.get("Quantite") or page.get("Quantity")
        unit = page.get("Unité") or page.get("Unite") or page.get("Unit") or ""
        categorie = page.get("Catégorie") or page.get("Category") or ""
        
        if not name:
            continue
        
        # Ajouter au stock (upsert)
        if not dry_run:
            try:
                from integrations.notion.upsert import upsert_page
                
                # Récupérer le schéma du stock
                schema = get_database_properties(client, stock_db_id)
                
                # Préparer les propriétés
                from integrations.notion.mappers import grocery_to_notion_properties
                stock_item = {
                    "Aliment": name,
                    "Quantité": qty,
                    "Unité": unit,
                    "Catégorie": categorie,
                }
                properties = grocery_to_notion_properties(stock_item, schema)
                
                # Trouver la propriété titre
                title_prop = None
                for prop_name, prop_def in schema.items():
                    if prop_def.get("type") == "title":
                        title_prop = prop_name
                        break
                
                if title_prop:
                    upsert_page(client, stock_db_id, name, properties, title_prop)
                    transferred += 1
            except Exception as e:
                print(f"   ⚠️ Erreur transfert {name} vers stock: {e}")
        else:
            transferred += 1
    
    return transferred


def propose_recipes_to_notion(
    n_candidates: int = 9,
    n_final: int = 6,
    dry_run: bool = False,
    notion_recipes_url: str | None = None,
) -> Dict[str, Any]:
    """
    Propose des recettes dans Notion.
    
    1. Archive les anciennes recettes
    2. Transfère les courses achetées vers le stock
    3. Récupère n_candidates depuis Spoonacular
    4. Sélectionne les n_final meilleures
    5. Ajoute Portions=1, Sélectionnée=false, Semaine=week_label()
    6. Push vers Notion
    7. Envoie notif
    
    Args:
        n_candidates: Nombre de recettes candidates à récupérer
        n_final: Nombre de recettes finales à proposer
        dry_run: Si True, ne fait rien, juste valide
        notion_recipes_url: URL de la vue Notion Recettes (pour la notif)
    
    Returns:
        Dict avec les résultats
    """
    semaine = week_label()
    
    # 1. Archiver les anciennes recettes
    print("📦 Archivage des anciennes recettes...")
    archived = archive_old_recipes(semaine, dry_run=dry_run)
    print(f"   {archived} recette(s) archivée(s)")
    
    # 2. Transférer les courses achetées vers le stock
    print("🔄 Transfert des courses achetées vers le stock...")
    transferred = transfer_purchased_to_stock(semaine, dry_run=dry_run)
    print(f"   {transferred} article(s) transféré(s)")
    
    # 3-4. Récupérer et sélectionner les recettes
    print("🔍 Récupération des recettes candidates...")
    candidates = get_candidate_recipes(n_candidates=n_candidates)
    print(f"   📊 {len(candidates)} recette(s) candidate(s) récupérée(s)")
    
    selected = candidates[:n_final]  # TODO: Ou via LLM si activé
    
    # Vérifier qu'on a bien n_final recettes
    if len(selected) < n_final:
        print(f"   ⚠️  Seulement {len(selected)} recette(s) sélectionnée(s) sur {n_final} demandées")
        if len(candidates) < n_final:
            print(f"   💡 L'API Spoonacular n'a retourné que {len(candidates)} recette(s). Vérifiez les filtres (diet, max_ready_time).")
    
    # 5. Ajouter les champs Notion (colonnes optionnelles)
    for recipe in selected:
        # Portions : on ne l'ajoute que si la colonne existe dans Notion
        # Sinon, le code utilisera 2 par défaut lors de la génération des courses
        recipe["Semaine"] = semaine
        # IMPORTANT: Ne pas mettre "Sélectionnée" à true - l'utilisateur doit sélectionner manuellement
        # Note: Portions et Sélectionnée sont optionnels - on ne les ajoute que si les colonnes existent
    
    # 5.5. Sauvegarder les ingrédients structurés dans un cache (optimisation tokens)
    if not dry_run:
        print("💾 Sauvegarde du cache des ingrédients...")
        from .config import DATA_DIR
        import json
        
        ingredients_cache_path = DATA_DIR / "recipes_ingredients_cache.json"
        ingredients_cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger le cache existant ou créer un nouveau dict
        cache = {}
        if ingredients_cache_path.exists():
            try:
                cache = json.loads(ingredients_cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                cache = {}
        
        # Ajouter les ingrédients de chaque recette au cache
        for recipe in selected:
            recipe_id = recipe.get("id")
            if recipe_id:
                # Les ingrédients sont déjà dans le format normalize()
                # IMPORTANT: Les quantités dans normalize() sont pour base_servings portions
                # (ex: si servings=4, les quantités sont pour 4 portions)
                # On sauvegarde aussi le nombre de servings pour référence
                cache[str(recipe_id)] = {
                    "title": recipe.get("title", ""),
                    "servings": recipe.get("servings", 1),  # Nombre de portions de base
                    "ingredients": recipe.get("ingredients", []),
                    "image": recipe.get("image"),  # Sauvegarder aussi l'image
                }
        
        # Sauvegarder le cache
        ingredients_cache_path.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"   ✅ Cache mis à jour pour {len(selected)} recette(s)")
    
    # 6. Sauvegarder temporairement et push vers Notion
    print("📤 Push vers Notion...")
    from .config import DATA_DIR
    import json
    
    temp_menu_path = DATA_DIR / "menu.json"
    temp_menu_path.parent.mkdir(parents=True, exist_ok=True)
    temp_menu_path.write_text(
        json.dumps(selected, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    result = push_recipes_to_notion(path=temp_menu_path, dry_run=dry_run)
    
    # 7. Notif (optionnel)
    if not dry_run:
        # Utiliser l'URL passée en paramètre, sinon celle de la config
        url_to_use = notion_recipes_url or NOTION_RECIPES_VIEW_URL
        if url_to_use:
            notify_ntfy(
                "Recettes pretes - choisis-en 3",
                f"{len(selected)} recettes proposees dans Notion\n\nCliquez pour ouvrir la vue Recettes",
                click_url=url_to_use
            )
        else:
            notify_ntfy(
                "Recettes pretes - choisis-en 3",
                f"{len(selected)} recettes proposees dans Notion"
            )
    
    return {
        **result,
        "archived_recipes": archived,
        "transferred_to_stock": transferred,
        "n_candidates": len(candidates),
        "n_final": len(selected),
    }


def main() -> None:
    """CLI pour proposer les recettes."""
    parser = argparse.ArgumentParser(description="Propose des recettes dans Notion")
    parser.add_argument(
        "--n-candidates",
        type=int,
        default=9,
        help="Nombre de recettes candidates à récupérer (défaut: 9)",
    )
    parser.add_argument(
        "--n-final",
        type=int,
        default=6,
        help="Nombre de recettes finales à proposer (défaut: 6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode dry-run (ne fait rien)",
    )
    parser.add_argument(
        "--notion-url",
        type=str,
        default=None,
        help="URL de la vue Notion Recettes (pour la notif)",
    )
    args = parser.parse_args()
    
    try:
        result = propose_recipes_to_notion(
            n_candidates=args.n_candidates,
            n_final=args.n_final,
            dry_run=args.dry_run,
            notion_recipes_url=args.notion_url,
        )
        print(f"\n✅ Résultat: {result}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

