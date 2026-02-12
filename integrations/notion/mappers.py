"""Mappers pour convertir les données Python ↔ Propriétés Notion."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from unidecode import unidecode


def pick(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Récupère la première valeur non-vide parmi plusieurs clés possibles.
    
    Usage:
        name = pick(row, "name", "Nom", "Name", "title")
        calories = pick(row, "Calories (~)", "calories", "Calories")
    """
    for key in keys:
        value = data.get(key)
        if value not in (None, "", [], {}):
            return value
    return default


def normalize_text(text: str) -> str:
    """Normalise un texte pour le matching (lowercase, strip, accents)."""
    if not text:
        return ""
    return unidecode(str(text).strip().lower())


def normalize_unit(unit: str) -> str:
    """
    Normalise une unité pour éviter les doublons.
    
    Exemples:
        "g" → "g"
        "grammes" → "g"
        "ml" → "ml"
        "millilitres" → "ml"
        "pièce", "pièces" → "pièce"
    """
    if not unit:
        return ""
    
    unit_lower = normalize_text(unit)
    
    # Mapping des unités communes (avant unidecode pour gérer les accents)
    unit_map: Dict[str, str] = {
        "g": "g",
        "gramme": "g",
        "grammes": "g",
        "kg": "kg",
        "kilogramme": "kg",
        "kilogrammes": "kg",
        "ml": "ml",
        "millilitre": "ml",
        "millilitres": "ml",
        "l": "l",
        "litre": "l",
        "litres": "l",
        "cl": "cl",
        "centilitre": "cl",
        "centilitres": "cl",
        "pièce": "pièce",
        "pièces": "pièce",
        "piece": "pièce",  # Après unidecode
        "pieces": "pièce",  # Après unidecode
        "unité": "pièce",
        "unités": "pièce",
        "unite": "pièce",  # Après unidecode
        "unites": "pièce",  # Après unidecode
        "tbsp": "cuil. à soupe",
        "tsp": "cuil. à café",
        "cuillère à soupe": "cuil. à soupe",
        "cuillères à soupe": "cuil. à soupe",
        "cuillère à café": "cuil. à café",
        "cuillères à café": "cuil. à café",
    }
    
    # Vérifie d'abord avec le texte original (avec accents)
    if unit_lower in unit_map:
        return unit_map[unit_lower]
    
    # Sinon retourne tel quel (normalisé)
    return unit_lower


def recipe_to_notion_properties(recipe: Dict[str, Any], schema: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Convertit un dict recette (menu.json) en propriétés Notion.
    
    Gère les formats français ("Nom", "Temps") et anglais ("name", "time_minutes").
    """
    properties: Dict[str, Any] = {}
    
    # Nom (title)
    name = pick(recipe, "Nom", "name", "Name", "title")
    if name:
        title_prop = _find_property_by_type(schema, "title")
        if title_prop:
            properties[title_prop] = {
                "title": [{"type": "text", "text": {"content": str(name)}}]
            }
    
    # Lien (url) - Chercher par nom d'abord, puis par type
    link = pick(recipe, "Lien", "link", "sourceUrl", "url")
    
    # Si pas de lien mais qu'on a un ID Spoonacular, construire l'URL
    if not link and recipe.get("id"):
        link = f"https://spoonacular.com/recipes/{recipe['id']}"
    
    if link:
        # Chercher d'abord par nom "Lien"
        url_prop = None
        if "Lien" in schema and schema["Lien"].get("type") == "url":
            url_prop = "Lien"
        else:
            # Fallback : chercher par type, mais exclure "Photo" et "Image"
            for prop_name, prop_def in schema.items():
                if prop_def.get("type") == "url" and prop_name not in ("Photo", "Image", "photo", "image"):
                    url_prop = prop_name
                    break
        
        if url_prop:
            properties[url_prop] = {"url": str(link)}
    
    # ID Spoonacular (number) - Priorité absolue : chercher "ID" en premier
    recipe_id = recipe.get("id")
    if recipe_id is not None:
        # Chercher "ID" en premier (nom exact de la colonne)
        if "ID" in schema and schema["ID"].get("type") == "number":
            properties["ID"] = {"number": int(recipe_id)}
        # Fallback sur "Spoon ID" ou autres variantes
        else:
            id_prop = _find_property_by_name_or_type(schema, ("Spoon ID", "SpoonID", "spoon_id", "ID"), "number")
            if id_prop:
                properties[id_prop] = {"number": int(recipe_id)}
    
    # Temps (number)
    time_value = pick(recipe, "Temps", "time_minutes", "readyMinutes", "time")
    if time_value is not None:
        time_num = _to_number(time_value)
        if time_num is not None:
            time_prop = _find_property_by_name_or_type(schema, ("Temps", "Durée", "Time"), "number")
            if time_prop:
                properties[time_prop] = {"number": time_num}
    
    # Calories (number)
    calories_value = pick(
        recipe,
        "Calories (~)",
        "Calories",
        "calories",
        default=recipe.get("nutrition", {}).get("calories") if isinstance(recipe.get("nutrition"), dict) else None
    )
    # Vérifier aussi directement dans nutrition si c'est un dict
    if calories_value is None and isinstance(recipe.get("nutrition"), dict):
        calories_value = recipe.get("nutrition", {}).get("calories")
    
    if calories_value is not None:
        calories_num = _to_number(calories_value)
        if calories_num is not None and calories_num > 0:  # Ignorer les valeurs 0 ou négatives
            calories_prop = _find_property_by_name_or_type(schema, ("Calories (~)", "Calories"), "number")
            if calories_prop:
                properties[calories_prop] = {"number": int(calories_num)}
    
    # Protéines (number)
    protein_value = pick(
        recipe,
        "Protéines (g)",
        "Proteines",
        "protein",
        "Proteines (g)",
        default=recipe.get("nutrition", {}).get("protein") if isinstance(recipe.get("nutrition"), dict) else None
    )
    if protein_value is not None:
        protein_num = _to_number(protein_value)
        if protein_num is not None:
            protein_prop = _find_property_by_name_or_type(schema, ("Protéines (g)", "Proteines", "Protein"), "number")
            if protein_prop:
                properties[protein_prop] = {"number": protein_num}
    
    # Tags (multi_select)
    tags = pick(recipe, "tags", "Tags", "tag")
    if tags:
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        elif isinstance(tags, list):
            tags = [str(t).strip() for t in tags if t]
        if tags:
            tags_prop = _find_property_by_name_or_type(schema, ("Tags", "Tag"), "multi_select")
            if tags_prop:
                properties[tags_prop] = {
                    "multi_select": [{"name": str(tag)} for tag in tags]
                }
    
    # Image (url ou files)
    image = pick(recipe, "image", "Image", "imageUrl", "image_url")
    if not image:
        # Debug : afficher pourquoi l'image n'est pas trouvée
        recipe_name = pick(recipe, "Nom", "name", "Name", "title", default="Recette inconnue")
        print(f"   ⚠️  Pas d'image pour '{recipe_name}' dans les données (champs vérifiés: image, Image, imageUrl, image_url)")
    
    if image:
        # Chercher "Photo" en premier (nom exact de la colonne)
        image_prop = None
        prop_type = None
        
        # 1. Chercher "Photo" exactement (priorité absolue)
        if "Photo" in schema:
            image_prop = "Photo"
            prop_type = schema["Photo"].get("type")
            print(f"   🔍 Champ 'Photo' trouvé dans le schéma (type: {prop_type})")
        # 2. Fallback sur "Image"
        elif "Image" in schema:
            image_prop = "Image"
            prop_type = schema["Image"].get("type")
            print(f"   🔍 Champ 'Image' trouvé dans le schéma (type: {prop_type})")
        # 3. Chercher par type files
        else:
            image_prop = _find_property_by_name_or_type(schema, ("Photo", "Image"), "files")
            if image_prop:
                prop_type = "files"
                print(f"   🔍 Champ de type 'files' trouvé: '{image_prop}'")
            # 4. Chercher par type url
            else:
                image_prop = _find_property_by_name_or_type(schema, ("Photo", "Image"), "url")
                if image_prop:
                    prop_type = "url"
                    print(f"   🔍 Champ de type 'url' trouvé: '{image_prop}'")
        
        if image_prop and prop_type:
            if prop_type == "files":
                # Pour files, on doit convertir l'URL en format files
                properties[image_prop] = {
                    "files": [{"type": "external", "name": "image.jpg", "external": {"url": str(image)}}]
                }
                print(f"   ✅ Image ajoutée dans '{image_prop}' (type: files): {str(image)[:50]}...")
            elif prop_type == "url":
                # Pour url, on utilise directement l'URL
                properties[image_prop] = {"url": str(image)}
                print(f"   ✅ Image ajoutée dans '{image_prop}' (type: url): {str(image)[:50]}...")
            else:
                print(f"   ⚠️  Champ '{image_prop}' trouvé mais type '{prop_type}' non supporté (attendu: files ou url)")
        else:
            print(f"   ⚠️  Aucun champ 'Photo' ou 'Image' trouvé dans le schéma Notion")
            # Afficher les champs disponibles pour debug
            available_props = [name for name, defn in schema.items() if defn.get("type") in ("files", "url")]
            if available_props:
                print(f"   💡 Champs disponibles de type files/url: {', '.join(available_props)}")
            else:
                print(f"   💡 Aucun champ de type files ou url dans le schéma")
    
    # Ingrédients (rich_text)
    ingredients = pick(recipe, "Ingrédients", "ingredients", "Ingredients")
    if ingredients:
        if isinstance(ingredients, str):
            ingredients_text = ingredients
        elif isinstance(ingredients, list):
            # Convertir liste d'ingrédients en texte
            lines = []
            for item in ingredients:
                if isinstance(item, dict):
                    name = pick(item, "name", "nameClean", "Nom")
                    amount = item.get("amount")
                    unit = item.get("unit")
                    parts = []
                    if amount is not None:
                        parts.append(str(amount))
                    if unit:
                        parts.append(str(unit))
                    if name:
                        parts.append(str(name))
                    lines.append(" ".join(parts).strip())
                else:
                    lines.append(str(item))
            ingredients_text = "\n".join(lines)
        else:
            ingredients_text = str(ingredients)
        
        if ingredients_text:
            ingredients_prop = _find_property_by_name_or_type(
                schema, ("Ingrédients", "Ingredients", "Liste"), "rich_text"
            )
            if ingredients_prop:
                properties[ingredients_prop] = {
                    "rich_text": [{"type": "text", "text": {"content": ingredients_text}}]
                }
    
    # Portions (number) - Optionnel : on ne l'ajoute que si la colonne existe
    portions = pick(recipe, "Portions", "portions", "Portion")
    if portions is not None:
        portions_num = _to_number(portions)
        if portions_num is not None:
            portions_prop = _find_property_by_name_or_type(schema, ("Portions", "Portion"), "number")
            if portions_prop:  # Seulement si la colonne existe
                properties[portions_prop] = {"number": int(portions_num)}
    
    # Sélectionnée (checkbox) - Optionnel : on ne l'ajoute que si la colonne existe
    selected = pick(recipe, "Sélectionnée", "selected", "Selected")
    if selected is not None:
        selected_prop = _find_property_by_name_or_type(schema, ("Sélectionnée", "Selected"), "checkbox")
        if selected_prop:  # Seulement si la colonne existe
            properties[selected_prop] = {"checkbox": bool(selected)}
    
    # Semaine (select ou multi_select)
    semaine = pick(recipe, "Semaine", "semaine", "Week")
    if semaine:
        # Essayer d'abord multi_select, puis select
        semaine_prop = _find_property_by_name_or_type(schema, ("Semaine", "Week"), "multi_select")
        if semaine_prop:
            # Pour multi_select, on doit passer une liste
            semaine_value = str(semaine)
            properties[semaine_prop] = {
                "multi_select": [{"name": semaine_value}]
            }
        else:
            # Fallback sur select si multi_select n'existe pas
            semaine_prop = _find_property_by_name_or_type(schema, ("Semaine", "Week"), "select")
            if semaine_prop:
                properties[semaine_prop] = {"select": {"name": str(semaine)}}
    
    # Terminée (checkbox)
    terminee = pick(recipe, "Terminée", "terminee", "Completed", "Done")
    if terminee is not None:
        terminee_prop = _find_property_by_name_or_type(schema, ("Terminée", "Completed", "Done"), "checkbox")
        if terminee_prop:
            properties[terminee_prop] = {"checkbox": bool(terminee)}
    
    return properties


def grocery_to_notion_properties(grocery: Dict[str, Any], schema: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Convertit un dict course (achats_filtres.json) en propriétés Notion.
    """
    properties: Dict[str, Any] = {}
    
    # Article (title)
    name = pick(grocery, "Aliment", "name", "Name", "Article", "article")
    if name:
        title_prop = _find_property_by_type(schema, "title")
        if title_prop:
            properties[title_prop] = {
                "title": [{"type": "text", "text": {"content": str(name)}}]
            }
    
    # Catégorie (select)
    category = pick(grocery, "Catégorie", "category", "Categorie")
    if category:
        category_prop = _find_property_by_name_or_type(schema, ("Catégorie", "Category"), "select")
        if category_prop:
            properties[category_prop] = {"select": {"name": str(category)}}
    
    # Quantité (number)
    quantity = pick(grocery, "Quantité", "quantity", "Quantite", "quantity_needed")
    if quantity is not None:
        qty_num = _to_number(quantity)
        if qty_num is not None:
            qty_prop = _find_property_by_name_or_type(schema, ("Quantité", "Quantity"), "number")
            if qty_prop:
                properties[qty_prop] = {"number": qty_num}
    
    # Unité (rich_text)
    unit = pick(grocery, "Unité", "unit", "Unite")
    if unit:
        unit_normalized = normalize_unit(str(unit))
        unit_prop = _find_property_by_name_or_type(schema, ("Unité", "Unit"), "rich_text")
        if unit_prop:
            properties[unit_prop] = {
                "rich_text": [{"type": "text", "text": {"content": unit_normalized}}]
            }
    
    # À acheter ? (checkbox)
    to_buy = pick(grocery, "À acheter ?", "to_buy", "to buy", "A acheter", default=True)
    if isinstance(to_buy, bool):
        to_buy_prop = _find_property_by_name_or_type(
            schema, ("À acheter ?", "A acheter", "To buy", "to_buy"), "checkbox"
        )
        if to_buy_prop:
            properties[to_buy_prop] = {"checkbox": to_buy}
    
    # Recettes (rich_text, optionnel)
    recipes = pick(grocery, "Recettes", "recipes", "Recette")
    if recipes:
        recipes_prop = _find_property_by_name_or_type(schema, ("Recettes", "Recette", "Recipes"), "rich_text")
        if recipes_prop:
            properties[recipes_prop] = {
                "rich_text": [{"type": "text", "text": {"content": str(recipes)}}]
            }
    
    # Semaine (select ou multi_select)
    semaine = pick(grocery, "Semaine", "semaine", "Week")
    if semaine:
        # Essayer d'abord multi_select, puis select
        semaine_prop = _find_property_by_name_or_type(schema, ("Semaine", "Week"), "multi_select")
        if semaine_prop:
            # Pour multi_select, on doit passer une liste
            semaine_value = str(semaine)
            properties[semaine_prop] = {
                "multi_select": [{"name": semaine_value}]
            }
        else:
            # Fallback sur select si multi_select n'existe pas
            semaine_prop = _find_property_by_name_or_type(schema, ("Semaine", "Week"), "select")
            if semaine_prop:
                properties[semaine_prop] = {"select": {"name": str(semaine)}}
    
    # Acheté (checkbox)
    achete = pick(grocery, "Acheté", "achete", "Purchased", "Achete")
    if achete is not None:
        achete_prop = _find_property_by_name_or_type(schema, ("Acheté", "Achete", "Purchased"), "checkbox")
        if achete_prop:
            properties[achete_prop] = {"checkbox": bool(achete)}
    
    return properties


def mealplan_to_notion_properties(
    entry: Dict[str, Any],
    schema: Dict[str, Dict],
    recipe_page_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convertit une entrée meal plan en propriétés Notion.
    """
    properties: Dict[str, Any] = {}
    
    # Date (date)
    date_value = entry.get("date")
    if date_value:
        date_prop = _find_property_by_type(schema, "date")
        if date_prop:
            if isinstance(date_value, str):
                # Format ISO: "2024-01-15"
                properties[date_prop] = {"date": {"start": date_value}}
            elif hasattr(date_value, "isoformat"):
                properties[date_prop] = {"date": {"start": date_value.isoformat()}}
    
    # Type (select)
    meal_type = pick(entry, "meal_type", "type", "Type", "Meal type")
    if meal_type:
        # Normalise le type de repas pour correspondre aux options Notion
        # Convertit "Déjeuner" -> "dejeuner" et "Dîner" -> "diner" (minuscules, sans accents)
        meal_type_str = str(meal_type).lower()
        meal_type_normalized = meal_type_str
        
        # Mapping des valeurs françaises vers les options Notion
        type_mapping = {
            "déjeuner": "dejeuner",
            "dejeuner": "dejeuner",
            "dîner": "diner",
            "diner": "diner",
            "petit-déjeuner": "petit-dejeuner",
            "petit-dejeuner": "petit-dejeuner",
        }
        
        # Normalise en enlevant les accents et convertissant en minuscules
        from unidecode import unidecode
        meal_type_normalized = unidecode(meal_type_str)
        
        # Utilise le mapping si disponible, sinon garde la valeur normalisée
        meal_type_normalized = type_mapping.get(meal_type_normalized, meal_type_normalized)
        
        # Cherche d'abord "Type", puis "Jour" et les autres noms
        type_prop = _find_property_by_name_or_type(schema, ("Type", "Jour", "Meal type", "type", "Repas"), "select")
        if type_prop:
            properties[type_prop] = {"select": {"name": meal_type_normalized}}
        else:
            # Si pas trouvé, cherche n'importe quelle propriété select
            for prop_name, prop_def in schema.items():
                if prop_def.get("type") == "select":
                    type_prop = prop_name
                    properties[type_prop] = {"select": {"name": meal_type_normalized}}
                    break
    
    # Recette (relation)
    if recipe_page_id:
        # Cherche "Recettes" (pluriel) en premier, puis "Recette" (singulier)
        recipe_prop = _find_property_by_name_or_type(schema, ("Recettes", "Recette", "Recipe", "recette", "Plat"), "relation")
        if recipe_prop:
            properties[recipe_prop] = {
                "relation": [{"id": recipe_page_id}]
            }
        else:
            # Si pas trouvé, cherche n'importe quelle propriété relation
            for prop_name, prop_def in schema.items():
                if prop_def.get("type") == "relation":
                    recipe_prop = prop_name
                    properties[recipe_prop] = {
                        "relation": [{"id": recipe_page_id}]
                    }
                    break
    
    # Portions (number, optionnel)
    portions = pick(entry, "portions", "Portions", "portion")
    if portions is not None:
        portions_num = _to_number(portions)
        if portions_num is not None:
            portions_prop = _find_property_by_name_or_type(schema, ("Portions", "Portion"), "number")
            if portions_prop:
                properties[portions_prop] = {"number": int(portions_num)}
    
    return properties


# Helpers internes

def _to_number(value: Any) -> Optional[float]:
    """Convertit une valeur en nombre."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _find_property_by_type(schema: Dict[str, Dict], prop_type: str) -> Optional[str]:
    """Trouve une propriété par son type."""
    for prop_name, prop_def in schema.items():
        if prop_def.get("type") == prop_type:
            return prop_name
    return None


def _find_property_by_name_or_type(
    schema: Dict[str, Dict],
    name_candidates: tuple[str, ...],
    prop_type: str,
) -> Optional[str]:
    """Trouve une propriété par son nom (candidates) ou son type."""
    # D'abord par nom
    for prop_name in schema.keys():
        if prop_name in name_candidates:
            return prop_name
    
    # Sinon par type
    return _find_property_by_type(schema, prop_type)

