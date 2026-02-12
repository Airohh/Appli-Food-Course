# Plan d'Action Révisé - Flux UX Mobile avec Notion

## 📋 Ajustements basés sur le code existant

Ce plan a été révisé après analyse du code existant pour identifier ce qui existe déjà et ce qui doit être ajouté/modifié.

## 🆕 Fonctionnalités supplémentaires

### Historisation et gestion du stock
1. **Lors de la proposition de nouvelles recettes** :
   - Archiver les anciennes recettes (champ "Archivée" ou déplacer vers vue historique)
   - Transférer les courses achetées vers le stock (si "Acheté" = true)

2. **Suppression du stock** :
   - Uniquement quand une recette est marquée "Terminée"
   - Soustraire les ingrédients de la recette du stock

---

## 🔍 Ce qui existe déjà

### ✅ Déjà en place
- `app/shopping.py` : `normalize_aliment()`, conversions d'unités basiques, gestion de catégories
- `app/spoonacular.py` : `get_candidate_recipes()`, `normalize()`, `complex_search()`
- `integrations/notion/recipes.py` : `push_recipes_to_notion()`
- `integrations/notion/groceries.py` : `push_groceries_to_notion()` (avec TODO pour clear_week)
- `integrations/notion/mappers.py` : `recipe_to_notion_properties()`, `grocery_to_notion_properties()`
- `notion_tools/fetch/fetch_stock.py` : récupération du stock depuis Notion
- Gestion des catégories dans les courses (mais pas de distinction durable/frais)

### ⚠️ À modifier/ajouter
- `normalize()` ne préserve pas l'`id` Spoonacular
- Pas de fonction pour récupérer ingrédients avec quantités depuis un ID
- Pas de distinction durable/frais dans le stock
- Pas de gestion de "Semaine" (select) dans Notion
- Pas de champ "Portions", "Sélectionnée" dans les recettes
- Conversions d'unités incomplètes (manque tbsp→ml, oz→g, etc.)
- Pas de dictionnaire de synonymes d'aliments

---

## 📦 Phase 0 : Configuration & Helpers (AJUSTÉ)

### 0.1 Variables d'environnement ✅ FAIT
**Fichier : `app/config.py`**
- `NTFY_TOPIC` ajouté

### 0.2 Helper `week_label()`
**Fichier : `app/utils.py` (nouveau)**

```python
from datetime import date

def week_label(d: date | None = None) -> str:
    """Retourne 'Semaine {iso_week} – {iso_year}'"""
    if d is None:
        d = date.today()
    iso_year, iso_week, _ = d.isocalendar()
    return f"Semaine {iso_week} – {iso_year}"
```

### 0.3 Helper `notify_ntfy()`
**Fichier : `app/utils.py`**

```python
import requests
from .config import NTFY_TOPIC

def notify_ntfy(title: str, body: str) -> None:
    """Envoie une notification via ntfy.sh"""
    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=body.encode("utf-8"),
            headers={"Title": title},
            timeout=5
        )
    except Exception as e:
        print(f"⚠️ Erreur notification ntfy: {e}")
```

### 0.4 Helper `extract_spoon_id_from_url()`
**Fichier : `app/utils.py`**

```python
import re

def extract_spoon_id_from_url(url: str) -> int | None:
    """
    Extrait l'ID Spoonacular depuis une URL.
    Ex: https://spoonacular.com/recipes/123456 -> 123456
    """
    if not url:
        return None
    # Pattern: /recipes/{id} ou ?id={id}
    match = re.search(r'/recipes/(\d+)', url)
    if match:
        return int(match.group(1))
    match = re.search(r'[?&]id=(\d+)', url)
    if match:
        return int(match.group(1))
    return None
```

---

## 🍽️ Phase 1 : Étape "Proposer 6 recettes" (AJUSTÉ)

### 1.1 Modifier `normalize()` pour préserver l'ID Spoonacular ⚠️ IMPORTANT

**Fichier : `app/spoonacular.py`**

```python
def normalize(recipe: Dict[str, Any]) -> Dict[str, Any]:
    # ... code existant ...
    
    # AJOUTER : Préserver l'ID Spoonacular
    recipe_id = recipe.get("id")
    
    return {
        "id": recipe_id,  # ← AJOUTER
        "title": title,
        "readyMinutes": ready_minutes,
        "servings": servings,
        "sourceUrl": source_url,
        "image": image,
        "ingredients": ingredients,
        "nutrition": {...},
    }
```

### 1.2 Modifier `get_candidate_recipes()` pour accepter `n_candidates`

**Fichier : `app/spoonacular.py`**

```python
def get_candidate_recipes(
    query: str | None = None,
    n_candidates: int | None = None  # ← AJOUTER
) -> List[Dict[str, Any]]:
    n = n_candidates or N_RECIPES_CANDIDATES
    if USE_MOCK_DATA:
        # ... code existant ...
    # Dans complex_search, utiliser n au lieu de N_RECIPES_CANDIDATES
    payload = complex_search(query=query, number=n)
    return [normalize(recipe) for recipe in payload.get("results", [])]
```

### 1.3 Nouvelle fonction `archive_old_recipes()`

**Fichier : `app/workflow_recipes.py` (nouveau)**

```python
def archive_old_recipes(
    current_semaine: str,
    dry_run: bool = False
) -> int:
    """
    Archive les recettes qui ne sont pas de la semaine actuelle.
    Marque le champ "Archivée" = true ou déplace vers vue historique.
    """
    from notion_tools.notion_reader import export_database, get_client
    from notion_tools.notion_reader import normalize_id
    from app.config import NOTION_RECIPES_DB
    
    client = get_client()
    db_id = normalize_id(NOTION_RECIPES_DB)
    pages = export_database(client, db_id)
    
    archived = 0
    for page in pages:
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            semaine_value = semaine_prop.get("select", {}).get("name")
        
        # Si pas de semaine ou semaine différente → archiver
        if semaine_value != current_semaine:
            if not dry_run:
                try:
                    # Option 1: Marquer comme archivée (si propriété existe)
                    archived_prop = page.get("Archivée") or page.get("Archived")
                    if archived_prop:
                        client.pages.update(
                            page_id=page.get("id"),
                            properties={"Archivée": {"checkbox": True}}
                        )
                    else:
                        # Option 2: Archiver la page Notion
                        client.pages.update(page_id=page.get("id"), archived=True)
                    archived += 1
                except Exception as e:
                    print(f"   ⚠️ Erreur archivage recette {page.get('id')}: {e}")
            else:
                archived += 1
    
    return archived
```

### 1.4 Nouvelle fonction `transfer_purchased_to_stock()`

**Fichier : `app/workflow_recipes.py` (nouveau)**

```python
def transfer_purchased_to_stock(
    semaine_label: str | None = None,
    dry_run: bool = False
) -> int:
    """
    Transfère les courses achetées (Acheté = true) vers le stock.
    """
    from notion_tools.notion_reader import export_database, get_client
    from notion_tools.notion_reader import normalize_id
    from app.config import NOTION_GROCERIES_DB, NOTION_STOCK_DB
    from app.utils import week_label
    from integrations.notion.upsert import upsert_page
    
    if semaine_label is None:
        semaine_label = week_label()
    
    client = get_client()
    groceries_db_id = normalize_id(NOTION_GROCERIES_DB)
    stock_db_id = normalize_id(NOTION_STOCK_DB)
    
    # Récupérer les courses de la semaine
    pages = export_database(client, groceries_db_id)
    
    transferred = 0
    for page in pages:
        # Vérifier Semaine
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            semaine_value = semaine_prop.get("select", {}).get("name")
        if semaine_value != semaine_label:
            continue
        
        # Vérifier Acheté = true
        acheté_prop = page.get("Acheté") or page.get("Achete") or page.get("Purchased")
        if not (acheté_prop and isinstance(acheté_prop, dict) and acheté_prop.get("checkbox")):
            continue
        
        # Récupérer les infos
        name = page.get("Aliment") or page.get("Article") or page.get("Name") or ""
        qty = page.get("Quantité") or page.get("Quantite") or page.get("Quantity")
        unit = page.get("Unité") or page.get("Unite") or page.get("Unit") or ""
        categorie = page.get("Catégorie") or page.get("Category") or ""
        
        if not name:
            continue
        
        # Ajouter au stock (upsert)
        if not dry_run:
            try:
                # Récupérer le schéma du stock
                from notion_tools.notion_reader import get_database_properties
                schema = get_database_properties(client, stock_db_id)
                
                # Préparer les propriétés
                from integrations.notion.mappers import grocery_to_notion_properties
                stock_item = {
                    "Aliment": name,
                    "Quantité": qty,
                    "Unité": unit,
                    "Categorie": categorie,
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
```

### 1.5 Nouvelle fonction `propose_recipes_to_notion()`

**Fichier : `app/workflow_recipes.py` (nouveau)**

```python
from .spoonacular import get_candidate_recipes
from .utils import week_label, notify_ntfy
from integrations.notion.recipes import push_recipes_to_notion

def propose_recipes_to_notion(
    n_candidates: int = 9,
    n_final: int = 6,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    1. Archive les anciennes recettes
    2. Transfère les courses achetées vers le stock
    3. Récupère n_candidates depuis Spoonacular
    4. Sélectionne les n_final meilleures (ou utilise LLM si activé)
    5. Ajoute Portions=1, Sélectionnée=false, Semaine=week_label()
    6. Push vers Notion
    7. Envoie notif
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
    candidates = get_candidate_recipes(n_candidates=n_candidates)
    selected = candidates[:n_final]  # Ou via LLM
    
    # 5. Ajouter les champs Notion
    for recipe in selected:
        recipe["Portions"] = 1
        recipe["Sélectionnée"] = False
        recipe["Semaine"] = semaine
    
    # 6. Push vers Notion
    result = push_recipes_to_notion(selected, dry_run=dry_run)
    
    # 7. Notif
    if not dry_run:
        notify_ntfy(
            "🍽️ Recettes prêtes — choisis-en 3",
            f"Ouvre ta vue Notion Recettes – Galerie mobile\n{notion_recipes_url}"
        )
    
    return {
        **result,
        "archived_recipes": archived,
        "transferred_to_stock": transferred,
    }
```

### 1.6 Modifier `recipe_to_notion_properties()` pour gérer Portions, Sélectionnée, Semaine, Terminée

**Fichier : `integrations/notion/mappers.py`**

```python
def recipe_to_notion_properties(recipe: Dict[str, Any], schema: Dict[str, Dict]) -> Dict[str, Any]:
    properties = {...}  # Code existant
    
    # AJOUTER : Portions (number)
    portions = pick(recipe, "Portions", "portions")
    if portions is not None:
        portions_num = _to_number(portions)
        if portions_num is not None:
            portions_prop = _find_property_by_name_or_type(schema, ("Portions", "Portion"), "number")
            if portions_prop:
                properties[portions_prop] = {"number": int(portions_num)}
    
    # AJOUTER : Sélectionnée (checkbox)
    selected = pick(recipe, "Sélectionnée", "selected", "Selected")
    if selected is not None:
        selected_prop = _find_property_by_name_or_type(schema, ("Sélectionnée", "Selected"), "checkbox")
        if selected_prop:
            properties[selected_prop] = {"checkbox": bool(selected)}
    
    # AJOUTER : Semaine (select)
    semaine = pick(recipe, "Semaine", "semaine", "Week")
    if semaine:
        semaine_prop = _find_property_by_name_or_type(schema, ("Semaine", "Week"), "select")
        if semaine_prop:
            properties[semaine_prop] = {"select": {"name": str(semaine)}}
    
    # AJOUTER : Terminée (checkbox)
    terminee = pick(recipe, "Terminée", "terminee", "Completed", "Done")
    if terminee is not None:
        terminee_prop = _find_property_by_name_or_type(schema, ("Terminée", "Completed", "Done"), "checkbox")
        if terminee_prop:
            properties[terminee_prop] = {"checkbox": bool(terminee)}
    
    return properties
```

### 1.7 Modifier `push_recipes_to_notion()` pour gérer les nouveaux champs

**Fichier : `integrations/notion/recipes.py`**

Le code existant devrait fonctionner car `recipe_to_notion_properties()` gère déjà les propriétés dynamiquement. Juste s'assurer que les champs sont passés dans le dict `recipe`.

---

## 📖 Phase 2 : Lecture de la sélection & portions (AJUSTÉ)

### 2.1 Nouvelle fonction `get_selected_recipes_this_week()`

**Fichier : `app/workflow_courses.py` (nouveau)**

```python
from notion_tools.notion_reader import export_database, get_client
from notion_tools.notion_reader import normalize_id
from app.config import NOTION_RECIPES_DB
from app.utils import week_label, extract_spoon_id_from_url

def get_selected_recipes_this_week(
    semaine_label: str | None = None
) -> List[Dict[str, Any]]:
    """
    Lit les recettes sélectionnées depuis Notion.
    Filtre : Sélectionnée = true ET Semaine = semaine_label
    """
    if semaine_label is None:
        semaine_label = week_label()
    
    client = get_client()
    db_id = normalize_id(NOTION_RECIPES_DB)
    
    # Récupérer toutes les pages
    pages = export_database(client, db_id)
    
    selected = []
    for page in pages:
        # Vérifier Sélectionnée = true
        selected_prop = page.get("Sélectionnée") or page.get("Selected")
        if not (selected_prop and selected_prop.get("checkbox")):
            continue
        
        # Vérifier Semaine = semaine_label
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            semaine_value = semaine_prop.get("select", {}).get("name")
        if semaine_value != semaine_label:
            continue
        
        # Récupérer Portions (défaut 2 si vide)
        portions_prop = page.get("Portions") or page.get("Portion")
        portions = 2  # défaut
        if portions_prop and isinstance(portions_prop, dict):
            portions_num = portions_prop.get("number")
            if portions_num is not None:
                portions = int(portions_num)
        
        # Récupérer spoon_id
        spoon_id = None
        # 1. Champ dédié "Spoon ID" si existe
        spoon_id_prop = page.get("Spoon ID") or page.get("SpoonID") or page.get("spoon_id")
        if spoon_id_prop and isinstance(spoon_id_prop, dict):
            spoon_id = spoon_id_prop.get("number")
        
        # 2. Extraction depuis Lien
        if not spoon_id:
            link_prop = page.get("Lien") or page.get("link") or page.get("Lien")
            if link_prop and isinstance(link_prop, dict):
                url = link_prop.get("url")
                if url:
                    spoon_id = extract_spoon_id_from_url(url)
        
        selected.append({
            "name": page.get("Name") or page.get("Nom") or "",
            "portions": portions,
            "spoon_id": spoon_id,
            "page_id": page.get("id"),
            "link": url if 'url' in locals() else None,
        })
    
    return selected
```

---

## 🥘 Phase 3 : Ingrédients quantifiés (NOUVEAU)

### 3.1 Nouvelle fonction `get_recipe_ingredients_with_quantities()`

**Fichier : `app/spoonacular.py`**

```python
def get_recipe_ingredients_with_quantities(
    spoon_id: int,
    portions_multiplier: float = 1.0
) -> List[Dict[str, Any]]:
    """
    GET /recipes/{id}/information?includeNutrition=false
    Retourne les ingrédients avec quantités multipliées par portions_multiplier
    """
    if not SPOONACULAR_API_KEY and not SPOONACULAR_API_KEY2:
        raise RuntimeError("Aucune clé API Spoonacular disponible")
    
    key_to_use = SPOONACULAR_API_KEY or SPOONACULAR_API_KEY2
    url = f"{BASE_URL}/recipes/{spoon_id}/information"
    params = {
        "apiKey": key_to_use,
        "includeNutrition": "false",
    }
    
    @retry_http(max_attempts=3, base_delay=1.0)
    def _make_request():
        return requests.get(url, params=params, timeout=30)
    
    response = _make_request()
    response.raise_for_status()
    recipe = response.json()
    
    ingredients = []
    for ing in recipe.get("extendedIngredients", []):
        name = ing.get("nameClean") or ing.get("name") or ""
        measures = ing.get("measures", {}).get("metric") or {}
        amount = measures.get("amount", 0) * portions_multiplier
        unit = measures.get("unitShort") or measures.get("unit") or ""
        aisle = ing.get("aisle", "Divers")
        
        ingredients.append({
            "raw_name": ing.get("originalString", name),
            "name": name,
            "amount": amount,
            "unit": unit,
            "aisle": aisle,
            "recipe_id": spoon_id,
            "recipe_title": recipe.get("title", ""),
        })
    
    return ingredients
```

---

## 🔄 Phase 4 : Normalisation & agrégation (AJUSTÉ)

### 4.1 Créer dictionnaire de normalisation

**Fichier : `data/FOOD_SYNONYMS_ALL.json` (nouveau)**

```json
{
  "poulet": ["chicken", "poulet", "volaille", "chicken breast"],
  "tomate": ["tomate", "tomates", "tomato", "tomatoes"],
  "oignon": ["oignon", "oignons", "onion", "onions"],
  ...
}
```

### 4.2 Étendre les conversions d'unités

**Fichier : `app/shopping.py` (modifier UNIT_CONVERSIONS)**

```python
UNIT_CONVERSIONS = {
    # Conversions existantes
    ("g", "tsp"): lambda qty: qty / 5.0,
    ("tsp", "g"): lambda qty: qty * 5.0,
    ...
    
    # AJOUTER :
    ("tbsp", "ml"): lambda qty: qty * 15.0,
    ("ml", "tbsp"): lambda qty: qty / 15.0,
    ("tsp", "ml"): lambda qty: qty * 5.0,
    ("ml", "tsp"): lambda qty: qty / 5.0,
    ("cup", "ml"): lambda qty: qty * 240.0,
    ("ml", "cup"): lambda qty: qty / 240.0,
    ("oz", "g"): lambda qty: qty * 28.35,
    ("g", "oz"): lambda qty: qty / 28.35,
    ("lb", "g"): lambda qty: qty * 453.59,
    ("g", "lb"): lambda qty: qty / 453.59,
    ("clove", "pc"): lambda qty: qty,
    ("piece", "pc"): lambda qty: qty,
}
```

### 4.3 Nouvelle fonction `normalize_ingredient_line()`

**Fichier : `app/normalization.py` (nouveau)**

```python
from .shopping import normalize_aliment
import json
from pathlib import Path
from .config import DATA_DIR

def load_synonyms() -> Dict[str, str]:
    """Charge FOOD_SYNONYMS_ALL.json + learned_synonyms.json"""
    synonyms = {}
    
    # Charger FOOD_SYNONYMS_ALL.json
    main_file = DATA_DIR / "FOOD_SYNONYMS_ALL.json"
    if main_file.exists():
        data = json.loads(main_file.read_text(encoding="utf-8"))
        for canonical, variants in data.items():
            for variant in variants:
                synonyms[normalize_aliment(variant)] = canonical
    
    # Charger learned_synonyms.json
    learned_file = DATA_DIR / "learned_synonyms.json"
    if learned_file.exists():
        learned = json.loads(learned_file.read_text(encoding="utf-8"))
        for variant, canonical in learned.items():
            synonyms[normalize_aliment(variant)] = canonical
    
    return synonyms

def normalize_ingredient_line(
    item: Dict[str, Any],
    synonyms_dict: Dict[str, str] | None = None
) -> Dict[str, Any]:
    """Normalise un ingrédient avec dictionnaire + conversions unités"""
    if synonyms_dict is None:
        synonyms_dict = load_synonyms()
    
    name = item.get("name") or item.get("raw_name") or ""
    norm_name = normalize_aliment(name)
    canonical_name = synonyms_dict.get(norm_name, norm_name)
    
    # Conversions unités (voir 4.2)
    amount = item.get("amount", 0)
    unit = item.get("unit", "")
    canonical_unit = _normalize_unit(unit)  # Utiliser normalize_unit de mappers.py
    
    return {
        "canonical_name": canonical_name,
        "canonical_unit": canonical_unit,
        "amount": amount,
        "aisle": item.get("aisle", "Divers"),
        "recipe_id": item.get("recipe_id"),
        "recipe_title": item.get("recipe_title"),
    }
```

---

## 📦 Phase 5 : Stock - Durable vs Frais (NOUVEAU)

### 5.1 Modifier `fetch_stock()` pour inclure Catégorie

**Fichier : `notion_tools/fetch/fetch_stock.py`**

Le code existant récupère déjà toutes les propriétés. S'assurer que `Categorie` est bien récupéré.

### 5.2 Nouvelle fonction `subtract_stock_from_groceries()`

**Fichier : `app/shopping.py` (ajouter)**

```python
def subtract_stock_from_groceries(
    groceries: List[Dict[str, Any]],
    stock: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Soustraction intelligente :
    - Si durable et quantité/unité compatibles → max(qty - stock, 0)
    - Si durable mais quantité inconnue → soustraire par défaut (g:200, ml:100, pc:1)
    - Si frais → ne pas soustraire
    """
    stock_lookup = {}
    for item in stock:
        name = item.get("Aliment") or item.get("Name") or ""
        norm_name = normalize_aliment(name)
        categorie = item.get("Categorie") or item.get("Category") or ""
        qty = _to_number(item.get("Quantité") or item.get("Quantity"))
        unit = item.get("Unité") or item.get("Unit") or ""
        
        if norm_name:
            stock_lookup[norm_name] = {
                "categorie": categorie.lower(),
                "qty": qty,
                "unit": unit,
            }
    
    result = []
    for grocery in groceries:
        name = grocery.get("Aliment") or grocery.get("name") or ""
        norm_name = normalize_aliment(name)
        stock_item = stock_lookup.get(norm_name)
        
        if not stock_item:
            result.append(grocery)
            continue
        
        categorie = stock_item["categorie"]
        
        # Si frais → ne pas soustraire
        if "frais" in categorie:
            result.append(grocery)
            continue
        
        # Si durable → soustraire
        grocery_qty = _to_number(grocery.get("Quantité") or grocery.get("Quantite") or 0)
        grocery_unit = grocery.get("Unité") or grocery.get("Unite") or ""
        stock_qty = stock_item["qty"]
        stock_unit = stock_item["unit"]
        
        # Conversion et soustraction
        if stock_qty is not None and stock_unit and grocery_unit:
            # Essayer conversion
            try:
                converted_stock = _convert_unit_for_subtraction(stock_qty, stock_unit, grocery_unit)
                if converted_stock is not None:
                    new_qty = max(grocery_qty - converted_stock, 0)
                    grocery["Quantité"] = new_qty
                    result.append(grocery)
                    continue
            except:
                pass
        
        # Si quantité inconnue → soustraire par défaut
        defaults = {"g": 200, "ml": 100, "pc": 1, "pièce": 1}
        default_subtract = defaults.get(grocery_unit.lower(), 0)
        new_qty = max(grocery_qty - default_subtract, 0)
        grocery["Quantité"] = new_qty
        result.append(grocery)
    
    return result
```

---

## 🛒 Phase 6 : Push Courses (AJUSTÉ)

### 6.1 Implémenter `clear_courses_for_week()`

**Fichier : `integrations/notion/groceries.py` (remplacer TODO ligne 82)**

```python
def clear_courses_for_week(
    semaine_label: str,
    archive: bool = True
) -> int:
    """Archive les lignes de Semaine = semaine_label dans Courses"""
    config = get_config()
    client = get_client()
    db_id = normalize_id(config.groceries_db_id)
    
    # Récupérer toutes les pages
    pages = export_database(client, db_id)
    
    # Filtrer par Semaine
    to_archive = []
    for page in pages:
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            semaine_value = semaine_prop.get("select", {}).get("name")
        if semaine_value == semaine_label:
            to_archive.append(page.get("id"))
    
    # Archiver (ou supprimer)
    archived = 0
    for page_id in to_archive:
        try:
            if archive:
                # Marquer comme archivé (si propriété existe) ou supprimer
                client.pages.update(page_id=page_id, archived=True)
            else:
                client.pages.update(page_id=page_id, archived=True)
            archived += 1
        except Exception as e:
            print(f"   ⚠️ Erreur archivage page {page_id}: {e}")
    
    return archived
```

### 6.2 Modifier `grocery_to_notion_properties()` pour gérer Semaine

**Fichier : `integrations/notion/mappers.py`**

Ajouter mapping pour `Semaine` (select) et `Acheté` (checkbox) comme pour les recettes.

---

## 📊 Phase 7 : Pipeline complet

**Fichier : `app/workflow_courses.py`**

Créer `generate_courses_from_selection()` qui orchestre tout le pipeline.

---

## 🏁 Phase 7.5 : Gestion "Terminée" - Soustraire du stock

### 7.5.1 Nouvelle fonction `subtract_stock_when_recipe_completed()`

**Fichier : `app/workflow_stock.py` (nouveau)**

```python
def subtract_stock_when_recipe_completed(
    recipe_page_id: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Quand une recette est marquée "Terminée" = true :
    1. Récupère les ingrédients de la recette
    2. Soustrait les quantités du stock
    3. Met à jour le stock dans Notion
    """
    from notion_tools.notion_reader import get_client, normalize_id
    from app.config import NOTION_RECIPES_DB, NOTION_STOCK_DB
    from app.spoonacular import get_recipe_ingredients_with_quantities
    from app.utils import extract_spoon_id_from_url
    from app.shopping import subtract_stock_from_groceries
    
    client = get_client()
    recipes_db_id = normalize_id(NOTION_RECIPES_DB)
    stock_db_id = normalize_id(NOTION_STOCK_DB)
    
    # Récupérer la recette
    recipe_page = client.pages.retrieve(page_id=recipe_page_id)
    props = recipe_page.get("properties", {})
    
    # Vérifier que Terminée = true
    terminee_prop = props.get("Terminée") or props.get("Completed") or props.get("Done")
    if not (terminee_prop and terminee_prop.get("checkbox")):
        return {"error": "Recette non terminée"}
    
    # Récupérer spoon_id et portions
    link_prop = props.get("Lien") or props.get("link")
    url = link_prop.get("url") if link_prop else None
    spoon_id = extract_spoon_id_from_url(url) if url else None
    
    portions_prop = props.get("Portions") or props.get("Portion")
    portions = portions_prop.get("number") if portions_prop else 1
    
    if not spoon_id:
        return {"error": "Impossible de récupérer l'ID Spoonacular"}
    
    # Récupérer les ingrédients avec quantités
    ingredients = get_recipe_ingredients_with_quantities(spoon_id, portions_multiplier=portions)
    
    # Récupérer le stock actuel
    from notion_tools.fetch.fetch_stock import fetch_stock
    stock = fetch_stock()
    
    # Soustraire du stock
    groceries = [
        {
            "Aliment": ing.get("name"),
            "Quantité": ing.get("amount"),
            "Unité": ing.get("unit"),
        }
        for ing in ingredients
    ]
    
    updated_groceries = subtract_stock_from_groceries(groceries, stock)
    
    # Mettre à jour le stock dans Notion
    if not dry_run:
        # TODO: Implémenter la mise à jour du stock dans Notion
        # Pour chaque item du stock modifié, faire un upsert
        pass
    
    return {
        "ingredients_processed": len(ingredients),
        "stock_updated": len(updated_groceries),
    }
```

### 7.5.2 Workflow pour détecter les recettes terminées

**Option 1 : Script manuel** `python -m app.workflow_stock --recipe-id <id>`
**Option 2 : Webhook Notion** (si configuré) pour détecter automatiquement
**Option 3 : Vérification périodique** (mais l'utilisateur a dit pas d'auto)

**Recommandation** : Script manuel ou webhook (si disponible)

---

## 🔔 Phase 8 : Notifications

Intégrer `notify_ntfy()` dans les workflows.

---

## 🚀 Phase 9 : Workflows GitHub Actions

Créer les 2 workflows comme prévu dans le plan original.

---

## ✅ Points d'attention

1. **ID Spoonacular** : S'assurer que `normalize()` préserve l'`id` (CRITIQUE)
2. **Semaine Select** : Notion select doit avoir les options créées au préalable
3. **Stock durable/frais** : Vérifier que la catégorie dans Notion Stock est bien "durable" ou "frais"
4. **Conversions unités** : Tester toutes les conversions
5. **Dictionnaire synonymes** : Commencer avec un dictionnaire minimal, enrichir progressivement
6. **Archivage recettes** : Décider si on archive via propriété "Archivée" ou via `archived=True` (suppression Notion)
7. **Transfert vers stock** : Gérer les doublons (si l'aliment existe déjà, additionner les quantités)
8. **Recette terminée** : Décider comment déclencher la soustraction (manuel, webhook, ou vérification périodique)

