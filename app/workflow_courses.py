"""Workflow pour générer la liste de courses depuis les recettes sélectionnées."""

from __future__ import annotations

import sys
import codecs

# Forcer UTF-8 pour la console Windows
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from integrations.notion.groceries import push_groceries_to_notion
from integrations.notion.client import get_client
from notion_tools.notion_reader import export_database, normalize_id

from .config import DATA_DIR, NOTION_COURSES_VIEW_URL, NOTION_RECIPES_DB
from .spoonacular import get_recipe_ingredients_with_quantities, AllAPIKeysExhaustedError
from .utils import extract_spoon_id_from_url, notify_ntfy, week_label


def get_selected_recipes_this_week(
    semaine_label: str | None = None
) -> List[Dict[str, Any]]:
    """
    Lit les recettes sélectionnées depuis Notion.
    
    Filtre : Semaine = semaine_label ET (Sélectionnée = true si la colonne existe, sinon toutes les recettes)
    Pour chaque recette : récupère Portions (défaut 2, ou depuis la colonne si elle existe) et spoon_id
    
    Args:
        semaine_label: Label de la semaine (défaut: semaine actuelle)
    
    Returns:
        Liste de recettes sélectionnées avec portions et spoon_id
    """
    if semaine_label is None:
        semaine_label = week_label()
    
    client = get_client()
    db_id = normalize_id(NOTION_RECIPES_DB)
    if not db_id:
        raise RuntimeError("Base Recettes non configurée")
    
    # Récupérer toutes les pages
    pages = export_database(client, db_id)
    
    # Debug : afficher les colonnes disponibles (seulement pour la première page)
    if pages and len(pages) > 0:
        first_page = pages[0]
        available_columns = list(first_page.keys())
        print(f"   🔍 Colonnes disponibles dans Notion: {', '.join(available_columns)}")
        # Vérifier spécifiquement la colonne "ID"
        if "ID" in first_page:
            print(f"   ✅ Colonne 'ID' trouvée: {first_page.get('ID')}")
        else:
            print(f"   ⚠️  Colonne 'ID' non trouvée dans les colonnes disponibles")
    
    selected = []
    for page in pages:
        # Vérifier Semaine = semaine_label (obligatoire)
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
        
        # Vérifier Sélectionnée = true (optionnel : si la colonne n'existe pas, on prend toutes les recettes de la semaine)
        selected_prop = page.get("Sélectionnée") or page.get("Selected")
        is_selected = True  # Par défaut, on prend toutes les recettes de la semaine
        if selected_prop is not None:  # Si la colonne existe
            if isinstance(selected_prop, dict):
                is_selected = selected_prop.get("checkbox", False)
            elif isinstance(selected_prop, bool):
                is_selected = selected_prop
        
        if not is_selected:
            continue
        
        # Portions : toujours 2 par défaut (colonne optionnelle)
        portions = 2  # Toujours 2 portions
        portions_prop = page.get("Portions") or page.get("Portion")
        if portions_prop is not None:  # Si la colonne existe, on peut la lire
            if isinstance(portions_prop, dict):
                portions_num = portions_prop.get("number")
                if portions_num is not None:
                    portions = int(portions_num)
            elif isinstance(portions_prop, (int, float)):
                portions = int(portions_prop)
        
        # Récupérer spoon_id
        spoon_id = None
        url = None
        
        # 1. Champ "ID" en priorité absolue (nom exact de la colonne)
        id_prop = page.get("ID")
        if id_prop:
            if isinstance(id_prop, dict):
                spoon_id = id_prop.get("number")
            elif isinstance(id_prop, (int, float)):
                spoon_id = int(id_prop)
            if spoon_id:
                print(f"   ✅ ID trouvé dans la colonne 'ID': {spoon_id}")
        
        # 2. Fallback sur autres champs ("Spoon ID", "SpoonID", etc.)
        if not spoon_id:
            spoon_id_prop = page.get("Spoon ID") or page.get("SpoonID") or page.get("spoon_id")
            if spoon_id_prop:
                if isinstance(spoon_id_prop, dict):
                    spoon_id = spoon_id_prop.get("number")
                elif isinstance(spoon_id_prop, (int, float)):
                    spoon_id = int(spoon_id_prop)
                if spoon_id:
                    print(f"   ✅ ID trouvé dans la colonne 'Spoon ID': {spoon_id}")
        
        # 3. Extraction depuis Lien (URL)
        if not spoon_id:
            link_prop = page.get("Lien") or page.get("link") or page.get("sourceUrl")
            if link_prop and isinstance(link_prop, dict):
                url = link_prop.get("url")
            elif isinstance(link_prop, str):
                url = link_prop
            
            if url:
                spoon_id = extract_spoon_id_from_url(url)
                if spoon_id:
                    print(f"   ✅ ID extrait depuis 'Lien': {spoon_id} (URL: {url[:50]}...)")
                else:
                    print(f"   ⚠️  Impossible d'extraire l'ID depuis 'Lien': {url[:50]}...")
        
        # 3. Extraction depuis Photo (URL image Spoonacular contient souvent l'ID)
        if not spoon_id:
            photo_prop = page.get("Photo") or page.get("Image") or page.get("image")
            photo_url = None
            if photo_prop and isinstance(photo_prop, dict):
                # Gérer url ou files
                if "url" in photo_prop:
                    photo_url = photo_prop.get("url")
                elif "files" in photo_prop:
                    files = photo_prop.get("files", [])
                    if files and isinstance(files, list) and len(files) > 0:
                        first_file = files[0]
                        if isinstance(first_file, dict):
                            if "external" in first_file:
                                photo_url = first_file.get("external", {}).get("url")
                            elif "file" in first_file:
                                photo_url = first_file.get("file", {}).get("url")
            elif isinstance(photo_prop, str):
                photo_url = photo_prop
            
            if photo_url:
                extracted_id = extract_spoon_id_from_url(photo_url)
                if extracted_id:
                    spoon_id = extracted_id
                    print(f"   ✅ ID extrait depuis 'Photo': {spoon_id} (URL: {photo_url[:50]}...)")
                else:
                    print(f"   ⚠️  Impossible d'extraire l'ID depuis 'Photo': {photo_url[:50]}...")
        
        # 4. Depuis le champ "id" de la recette (si présent dans les données)
        if not spoon_id:
            recipe_id = page.get("id")
            if recipe_id and isinstance(recipe_id, (int, float)):
                spoon_id = int(recipe_id)
        
        name = page.get("Name") or page.get("Nom") or page.get("title") or ""
        
        # Debug : afficher pourquoi l'ID n'est pas trouvé
        if not spoon_id:
            debug_info = []
            # Vérifier si le champ "ID" existe
            id_check = page.get("ID")
            if not id_check:
                debug_info.append("pas de champ 'ID'")
            else:
                debug_info.append(f"champ 'ID' existe mais vide ou invalide: {id_check}")
            # Vérifier si le champ "Spoon ID" existe
            spoon_id_check = page.get("Spoon ID") or page.get("SpoonID") or page.get("spoon_id")
            if not spoon_id_check:
                debug_info.append("pas de champ 'Spoon ID'")
            
            # Vérifier le champ "Lien"
            link_check = page.get("Lien") or page.get("link") or page.get("sourceUrl")
            if not link_check:
                debug_info.append("pas de champ 'Lien'")
            elif not url:
                # Le lien existe mais l'ID n'a pas pu être extrait
                link_value = link_check.get("url") if isinstance(link_check, dict) else str(link_check)
                debug_info.append(f"Lien trouvé mais ID non extrait depuis: {link_value[:50]}...")
            
            # Vérifier le champ "Photo"
            photo_check = page.get("Photo") or page.get("Image") or page.get("image")
            if not photo_check:
                debug_info.append("pas de champ 'Photo'")
            elif not photo_url:
                debug_info.append("Photo trouvée mais ID non extrait")
            
            print(f"   ⚠️  Pas d'ID Spoonacular pour '{name}' ({', '.join(debug_info)})")
        
        selected.append({
            "name": name,
            "portions": portions,
            "spoon_id": spoon_id,
            "page_id": page.get("id"),
            "link": url,
        })
    
    return selected


def generate_courses_from_selection(
    semaine_label: str | None = None,
    dry_run: bool = False,
    notion_courses_url: str | None = None,
) -> Dict[str, Any]:
    """
    Pipeline complet pour générer la liste de courses depuis les recettes sélectionnées.
    
    1. Lit les recettes sélectionnées
    2. Récupère les ingrédients avec quantités (multipliées par portions)
    3. Normalise et agrège les ingrédients
    4. Soustrait le stock (durable uniquement)
    5. Push vers Notion
    6. Envoie notif
    
    Args:
        semaine_label: Label de la semaine (défaut: semaine actuelle)
        dry_run: Si True, ne fait rien, juste valide
        notion_courses_url: URL de la vue Notion Courses (pour la notif)
    
    Returns:
        Dict avec les résultats
    """
    if semaine_label is None:
        semaine_label = week_label()
    
    # 1. Lire les recettes sélectionnées
    print("📖 Lecture des recettes sélectionnées...")
    selected_recipes = get_selected_recipes_this_week(semaine_label)
    print(f"   {len(selected_recipes)} recette(s) sélectionnée(s)")
    
    if not selected_recipes:
        print("   ⚠️  Aucune recette sélectionnée pour cette semaine")
        return {
            "n_selected": 0,
            "n_items": 0,
            "n_subtracted": 0,
        }
    
    # 2. Récupérer les ingrédients avec quantités depuis l'API
    print("🥘 Récupération des ingrédients depuis l'API...")
    print(f"   📋 {len(selected_recipes)} recette(s) sélectionnée(s)")
    
    # Debug : afficher les recettes sélectionnées
    for recipe in selected_recipes:
        spoon_id = recipe.get("spoon_id")
        recipe_name = recipe.get("name", "")
        portions = recipe.get("portions", 2)
        print(f"   📝 '{recipe_name}': ID={spoon_id}, Portions={portions}")
    
    all_ingredients = []
    all_keys_exhausted = False
    
    for recipe in selected_recipes:
        # Si toutes les clés sont épuisées, arrêter le traitement
        if all_keys_exhausted:
            print(f"   ⏸️  Arrêt du traitement : toutes les clés API sont épuisées")
            break
        
        spoon_id = recipe.get("spoon_id")
        # L'utilisateur veut toujours 2 portions par défaut (peut être modifié dans Notion via la colonne "Portions")
        portions = recipe.get("portions", 2)  # Défaut: 2 portions
        recipe_name = recipe.get("name", "")
        
        if not spoon_id:
            print(f"   ⚠️  Pas d'ID Spoonacular pour '{recipe_name}', ignoré")
            continue
        
        # Vérifier si c'est un ID MOCK (IDs fictifs utilisés dans get_mock_recipes)
        is_mock_id = spoon_id in [123456, 234567, 345678, 456789, 567890, 678901]
        
        if is_mock_id:
            # Récupérer les ingrédients depuis les données MOCK
            print(f"   🔄 {recipe_name}: ID MOCK ({spoon_id}) - récupération depuis les données MOCK...")
            try:
                from .spoonacular import get_mock_recipe_ingredients
                ingredients = get_mock_recipe_ingredients(spoon_id, desired_portions=portions)
                if ingredients:
                    all_ingredients.extend(ingredients)
                    print(f"   ✅ {recipe_name}: {len(ingredients)} ingrédient(s) récupéré(s) depuis MOCK")
                else:
                    print(f"   ⚠️  {recipe_name}: ID MOCK non trouvé dans les données MOCK")
            except Exception as e:
                print(f"   ❌ Erreur pour '{recipe_name}' (MOCK): {e}")
                import traceback
                traceback.print_exc()
        else:
            # Récupérer depuis l'API
            print(f"   🔄 {recipe_name}: récupération depuis l'API...")
            try:
                # Utiliser desired_portions pour que la fonction calcule automatiquement
                # le multiplicateur en fonction des servings de base de la recette
                ingredients = get_recipe_ingredients_with_quantities(
                    spoon_id,
                    desired_portions=portions  # Nombre de portions désirées (par défaut 2)
                )
                all_ingredients.extend(ingredients)
                print(f"   ✅ {recipe_name}: {len(ingredients)} ingrédient(s) récupéré(s)")
            except AllAPIKeysExhaustedError as e:
                # Toutes les clés sont épuisées, arrêter le traitement
                print(f"   ❌ {e}")
                print(f"   🛑 Arrêt du traitement : toutes les clés API Spoonacular ont épuisé leurs crédits.")
                print(f"   💡 Solution : Rechargez vos crédits sur spoonacular.com ou attendez le renouvellement de votre quota.")
                all_keys_exhausted = True
                break
            except Exception as e:
                print(f"   ❌ Erreur pour '{recipe_name}': {e}")
                import traceback
                traceback.print_exc()
    
    print(f"   📊 Total : {len(all_ingredients)} ingrédient(s) récupéré(s) pour {len(selected_recipes)} recette(s)")
    
    if not all_ingredients:
        if all_keys_exhausted:
            print("   🛑 IMPOSSIBLE DE GÉNÉRER LA LISTE DE COURSES")
            print("   ❌ Toutes les clés API Spoonacular ont épuisé leurs crédits.")
            print("   💡 Solutions possibles :")
            print("      • Rechargez vos crédits sur https://spoonacular.com/food-api")
            print("      • Attendez le renouvellement automatique de votre quota (généralement mensuel)")
            print("      • Vérifiez vos abonnements et ajoutez une nouvelle clé API si nécessaire")
        else:
            print("   ⚠️  Aucun ingrédient récupéré ! Vérifiez que les recettes ont un ID Spoonacular valide.")
        return {
            "n_selected": len(selected_recipes),
            "n_items": 0,
            "n_subtracted": 0,
        }
    
    # 3. Normaliser et agrégation simple (pour l'instant)
    print("🔄 Normalisation et agrégation...")
    from .shopping import normalize_aliment
    
    aggregated: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "name": "",
        "amount": 0.0,
        "unit": "",
        "aisle": "Divers",
        "recipes": set(),
    })
    
    for ing in all_ingredients:
        name = ing.get("name", "")
        norm_name = normalize_aliment(name)
        if not norm_name:
            continue
        
        entry = aggregated[norm_name]
        if not entry["name"]:
            entry["name"] = name
        entry["amount"] += ing.get("amount", 0)
        unit = ing.get("unit", "")
        if not entry["unit"] and unit:
            entry["unit"] = unit
        aisle = ing.get("aisle", "Divers")
        if entry["aisle"] == "Divers" and aisle != "Divers":
            entry["aisle"] = aisle
        recipe_title = ing.get("recipe_title", "")
        if recipe_title:
            entry["recipes"].add(recipe_title)
    
    groceries = []
    for entry in aggregated.values():
        groceries.append({
            "Aliment": entry["name"],
            "Quantité": entry["amount"],
            "Unité": entry["unit"],
            "Catégorie": entry["aisle"],
            "Recettes": ", ".join(sorted(entry["recipes"])),
            "Semaine": semaine_label,
            "Acheté": False,
        })
    
    print(f"   {len(groceries)} article(s) agrégé(s)")
    
    # 4. Soustraire le stock (durable uniquement)
    print("📦 Soustraction du stock...")
    from notion_tools.fetch.fetch_stock import fetch_stock
    from .shopping import subtract_stock_from_groceries
    
    try:
        stock = fetch_stock()
        groceries_after_stock = subtract_stock_from_groceries(groceries, stock)
        n_subtracted = len(groceries) - len([g for g in groceries_after_stock if g.get("Quantité", 0) > 0])
        groceries = groceries_after_stock
        print(f"   {n_subtracted} article(s) soustrait(s) du stock")
    except Exception as e:
        print(f"   ⚠️  Erreur lors de la soustraction du stock: {e}")
        n_subtracted = 0
    
    # Filtrer les articles avec quantité > 0
    groceries = [g for g in groceries if g.get("Quantité", 0) > 0]
    print(f"   📝 {len(groceries)} article(s) après filtrage (quantité > 0)")
    
    if not groceries:
        print("   ⚠️  ATTENTION : Aucun article avec quantité > 0 après soustraction du stock !")
        print("   💡 Cela peut être normal si tout est déjà en stock.")
    
    # 5. Sauvegarder les fichiers JSON
    print("💾 Sauvegarde des fichiers...")
    menu_path = DATA_DIR / "menu.json"
    groceries_path = DATA_DIR / "groceries.json"
    achats_path = DATA_DIR / "achats_filtres.json"
    
    # Menu (recettes sélectionnées)
    menu_data = [
        {
            "Nom": r.get("name"),
            "Portions": r.get("portions"),
            "spoon_id": r.get("spoon_id"),
        }
        for r in selected_recipes
    ]
    
    if not dry_run:
        menu_path.parent.mkdir(parents=True, exist_ok=True)
        menu_path.write_text(
            json.dumps(menu_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        groceries_path.write_text(
            json.dumps(groceries, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        achats_path.write_text(
            json.dumps(groceries, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"   ✅ Fichiers sauvegardés")
    
    # 6. Push vers Notion
    print("📤 Push vers Notion...")
    print(f"   📋 {len(groceries)} article(s) à synchroniser")
    if not groceries:
        print("   ⚠️  ATTENTION : La liste de courses est vide !")
        print("   💡 Vérifiez que :")
        print("      - Des recettes sont sélectionnées dans Notion")
        print("      - Les recettes ont un ID Spoonacular valide")
        print("      - Les ingrédients ont été récupérés correctement")
    
    result = push_groceries_to_notion(
        path=achats_path if not dry_run else None,
        clear_week=True,
        dry_run=dry_run
    )
    
    print(f"   📊 Résultat : {result.get('n_created', 0)} créé(s), {result.get('n_updated', 0)} mis à jour, {result.get('n_errors', 0)} erreur(s)")
    
    # 7. Notif (optionnel)
    if not dry_run:
        # Utiliser l'URL passée en paramètre, sinon celle de la config
        url_to_use = notion_courses_url or NOTION_COURSES_VIEW_URL
        if url_to_use:
            notify_ntfy(
                "Liste prete - ouvre ta vue Courses",
                f"{len(groceries)} articles dans la liste de courses\n\nCliquez pour ouvrir la vue Courses",
                click_url=url_to_use
            )
        else:
            notify_ntfy(
                "Liste prete - ouvre ta vue Courses",
                f"{len(groceries)} articles dans la liste de courses"
            )
    
    return {
        **result,
        "n_selected": len(selected_recipes),
        "n_items": len(groceries),
        "n_subtracted": n_subtracted,
        "semaine": semaine_label,
    }


def main() -> None:
    """CLI pour générer les courses."""
    parser = argparse.ArgumentParser(description="Génère la liste de courses depuis les recettes sélectionnées")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode dry-run (ne fait rien)",
    )
    parser.add_argument(
        "--notion-url",
        type=str,
        default=None,
        help="URL de la vue Notion Courses (pour la notif)",
    )
    parser.add_argument(
        "--semaine",
        type=str,
        default=None,
        help="Label de la semaine (ex: 'Semaine 45 – 2025'). Par défaut: semaine actuelle",
    )
    args = parser.parse_args()
    
    try:
        result = generate_courses_from_selection(
            semaine_label=args.semaine,
            dry_run=args.dry_run,
            notion_courses_url=args.notion_url,
        )
        print(f"\n✅ Résultat: {result}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()

