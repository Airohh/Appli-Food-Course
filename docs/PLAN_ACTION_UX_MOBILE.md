# Plan d'Action - Flux UX Mobile avec Notion

## 📋 Vue d'ensemble

Ce document décrit le plan d'action pour implémenter le nouveau flux UX mobile avec Notion, où l'utilisateur sélectionne manuellement les recettes dans Notion avant génération de la liste de courses.

## 🎯 Objectif

**Flux en 2 étapes :**
1. **Étape 1** : Générer 6 recettes proposées → Push dans Notion → Notif "Recettes prêtes"
2. **Étape 2** : Lire sélection + portions → Multiplier quantités → Soustraire stock → Push courses → Notif "Liste prête"

---

## 📦 Phase 0 : Configuration & Helpers

### 0.1 Variables d'environnement

**Fichier : `app/config.py`**

Ajouter :
```python
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "courses-ia")
HAS_NOTION = os.getenv("HAS_NOTION", "1").lower() in {"1", "true", "yes"}
```

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
import os
import requests
from .config import NTFY_TOPIC

def notify_ntfy(title: str, body: str) -> None:
    """Envoie une notification via ntfy.sh"""
    topic = NTFY_TOPIC
    try:
        requests.post(
            f"https://ntfy.sh/{topic}",
            data=body.encode("utf-8"),
            headers={"Title": title},
            timeout=5
        )
    except Exception as e:
        print(f"⚠️ Erreur notification ntfy: {e}")
```

---

## 🍽️ Phase 1 : Étape "Proposer 6 recettes"

### 1.1 Modifier `get_candidate_recipes()` pour retourner 6-9 candidates

**Fichier : `app/spoonacular.py`**

- Modifier `get_candidate_recipes()` pour prendre un paramètre `n_candidates: int = 9`
- S'assurer que les recettes incluent `id` (spoon_id) dans la réponse

### 1.2 Nouvelle fonction `propose_recipes_to_notion()`

**Fichier : `app/workflow_recipes.py` (nouveau)**

```python
def propose_recipes_to_notion(
    n_candidates: int = 9,
    n_final: int = 6,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    1. Récupère 6-9 candidates depuis Spoonacular
    2. Upsert dans Notion avec :
       - Name, Lien, Temps, Photo
       - Portions=1 (number)
       - Sélectionnée=false (checkbox)
       - Semaine=week_label() (select)
    3. Envoie notif ntfy
    """
```

**Dépendances :**
- `app/spoonacular.py` : `get_candidate_recipes()`
- `integrations/notion/recipes.py` : `push_recipes_to_notion()` (à modifier)
- `app/utils.py` : `week_label()`, `notify_ntfy()`

### 1.3 Modifier `recipe_to_notion_properties()` pour gérer les nouveaux champs

**Fichier : `integrations/notion/mappers.py`**

Ajouter mapping pour :
- `Portions` (number, défaut 1)
- `Sélectionnée` (checkbox, défaut false)
- `Semaine` (select, valeur = week_label())

### 1.4 Modifier `push_recipes_to_notion()` pour accepter les propriétés supplémentaires

**Fichier : `integrations/notion/recipes.py`**

- Permettre de passer des propriétés supplémentaires (Portions, Sélectionnée, Semaine)
- S'assurer que le champ `Semaine` est un select avec la bonne valeur

### 1.5 Nouveau script CLI : `python -m app.workflow_recipes`

**Fichier : `app/workflow_recipes.py`**

```python
def main():
    """CLI pour proposer les recettes"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    result = propose_recipes_to_notion(dry_run=args.dry_run)
    # Envoie notif avec URL de la vue Notion
```

---

## 📖 Phase 2 : Lecture de la sélection & portions

### 2.1 Nouvelle fonction `get_selected_recipes_this_week()`

**Fichier : `app/workflow_courses.py` (nouveau)**

```python
def get_selected_recipes_this_week(
    semaine_label: str | None = None
) -> List[Dict[str, Any]]:
    """
    Lit les recettes sélectionnées depuis Notion :
    - Filtre : Sélectionnée = true ET Semaine = semaine_label
    - Pour chaque recette : récupère Portions (défaut 2 si vide)
    - Récupère spoon_id depuis :
      1. Champ dédié "Spoon ID" (number) si existe
      2. Extraction depuis Lien (URL Spoonacular)
    """
```

**Dépendances :**
- `notion_tools/notion_reader.py` : `export_database()`, `get_client()`
- `app/config.py` : `NOTION_RECIPES_DB`
- `app/utils.py` : `week_label()`

### 2.2 Helper `extract_spoon_id_from_url()`

**Fichier : `app/utils.py`**

```python
import re

def extract_spoon_id_from_url(url: str) -> int | None:
    """
    Extrait l'ID Spoonacular depuis une URL.
    Ex: https://spoonacular.com/recipes/123456 -> 123456
    """
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

## 🥘 Phase 3 : Ingrédients quantifiés

### 3.1 Nouvelle fonction `get_recipe_ingredients_with_quantities()`

**Fichier : `app/spoonacular.py`**

```python
def get_recipe_ingredients_with_quantities(
    spoon_id: int,
    portions_multiplier: float = 1.0
) -> List[Dict[str, Any]]:
    """
    GET /recipes/{id}/information?includeNutrition=false
    Retourne :
    [
      {
        "raw_name": "2 cups flour",
        "amount": 2.0,
        "unit": "cup",
        "aisle": "Baking",
        "recipe_id": spoon_id,
        "recipe_title": "..."
      },
      ...
    ]
    Multiplie amount par portions_multiplier
    """
```

### 3.2 Modifier `normalize()` pour inclure les infos nécessaires

**Fichier : `app/spoonacular.py`**

S'assurer que `normalize()` préserve `id` (spoon_id) et les ingrédients avec quantités.

---

## 🔄 Phase 4 : Normalisation & agrégation

### 4.1 Créer dictionnaire de normalisation

**Fichier : `data/FOOD_SYNONYMS_ALL.json` (nouveau)**

```json
{
  "poulet": ["chicken", "poulet", "volaille"],
  "tomate": ["tomate", "tomates", "tomato"],
  ...
}
```

**Fichier : `data/learned_synonyms.json` (nouveau, vide au départ)**

```json
{}
```

### 4.2 Nouvelle fonction `normalize_ingredient_line()`

**Fichier : `app/normalization.py` (nouveau)**

```python
def normalize_ingredient_line(
    item: Dict[str, Any],
    synonyms_dict: Dict[str, str],
    learned_synonyms: Dict[str, str]
) -> Dict[str, Any]:
    """
    Normalise un ingrédient :
    1. Nom canon via dico (FOOD_SYNONYMS_ALL.json + learned_synonyms.json)
    2. Conversions unités :
       - tbsp → ml (15)
       - tsp → ml (5)
       - cup → ml (240)
       - oz → g (28.35)
       - lb → g (453.59)
       - clove/piece → pc
    3. Aisle fallback "Divers"
    """
```

### 4.3 Nouvelle fonction `aggregate_ingredients()`

**Fichier : `app/normalization.py`**

```python
def aggregate_ingredients(
    ingredients: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Agrège par (canonical_name, canonical_unit) → somme des quantités
    """
```

### 4.4 Option IA (fallback) pour résidus ambigus

**Fichier : `app/normalization.py`**

```python
def cluster_ambiguous_ingredients(
    ambiguous: List[Dict[str, Any]],
    use_llm: bool = False
) -> Dict[str, str]:
    """
    Si activée et restes ambigus :
    - Cluster minimal via LLM
    - Persist mapping dans learned_synonyms.json
    """
```

---

## 📦 Phase 5 : Stock - Durable vs Frais

### 5.1 Modifier `fetch_stock()` pour inclure Catégorie

**Fichier : `notion_tools/fetch/fetch_stock.py`**

S'assurer que le champ `Categorie` (ou `Category`) est récupéré avec valeurs possibles : `durable`, `frais`.

### 5.2 Nouvelle fonction `subtract_stock_from_groceries()`

**Fichier : `app/shopping.py`**

```python
def subtract_stock_from_groceries(
    groceries: List[Dict[str, Any]],
    stock: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Soustraction intelligente :
    - Si durable et quantité/unité compatibles → max(qty - stock, 0)
    - Si durable mais quantité inconnue → soustraire par défaut :
      - g: 200
      - ml: 100
      - pc: 1
    - Si frais → ne pas soustraire
    """
```

### 5.3 Helper `convert_units_for_subtraction()`

**Fichier : `app/shopping.py`**

```python
def convert_units_for_subtraction(
    qty: float,
    unit: str,
    stock_qty: float,
    stock_unit: str
) -> float | None:
    """
    Convertit les unités pour permettre la soustraction.
    Retourne None si conversion impossible.
    """
```

### 5.4 Option : Arrondis packaging

**Fichier : `app/shopping.py`**

```python
def apply_packaging_rounding(
    groceries: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Arrondis packaging :
    - Pâtes/riz → 500g
    - Lait → 1L
    - Œufs → x6
    """
```

---

## 🛒 Phase 6 : Push Courses (idempotent/semaine)

### 6.1 Nouvelle fonction `clear_courses_for_week()`

**Fichier : `integrations/notion/groceries.py`**

```python
def clear_courses_for_week(
    semaine_label: str,
    archive: bool = True
) -> int:
    """
    Avant insertion : vider (archiver) les lignes de Semaine = semaine_label
    dans Courses.
    Retourne le nombre de lignes archivées.
    """
```

### 6.2 Modifier `grocery_to_notion_properties()` pour gérer Semaine

**Fichier : `integrations/notion/mappers.py`**

Ajouter mapping pour :
- `Semaine` (select, valeur = week_label())
- `Acheté` (checkbox, défaut false)
- `Recettes` (relation, optionnel)

### 6.3 Modifier `push_groceries_to_notion()` pour utiliser `clear_courses_for_week()`

**Fichier : `integrations/notion/groceries.py`**

- Remplacer le TODO ligne 82 par l'appel à `clear_courses_for_week()`
- S'assurer que `clear_week=True` fonctionne correctement

---

## 📊 Phase 7 : Exports & logs

### 7.1 Modifier `build_pipeline()` pour générer les fichiers

**Fichier : `app/workflow_courses.py`**

```python
def generate_courses_from_selection(
    semaine_label: str | None = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Pipeline complet :
    1. get_selected_recipes_this_week()
    2. get_recipe_ingredients_with_quantities() × portions
    3. normalize_ingredient_line()
    4. aggregate_ingredients()
    5. subtract_stock_from_groceries()
    6. apply_packaging_rounding() (optionnel)
    7. push_groceries_to_notion()
    8. Sauvegarder :
       - menu.json (recettes sélectionnées + portions)
       - groceries.json (après agrégation)
       - achats_filtres.json (après stock)
    9. Logs synthétiques
    """
```

### 7.2 Logs synthétiques

**Fichier : `app/workflow_courses.py`**

```python
def log_summary(
    n_candidates: int,
    n_selected: int,
    n_items: int,
    n_subtracted: int,
    semaine_label: str
) -> None:
    """Affiche un résumé dans les logs"""
```

---

## 🔔 Phase 8 : Notifications

### 8.1 Notif "Recettes prêtes"

**Fichier : `app/workflow_recipes.py`**

```python
# Après push_recipes_to_notion()
notify_ntfy(
    "🍽️ Recettes prêtes — choisis-en 3",
    f"Ouvre ta vue Notion Recettes – Galerie mobile\n{notion_recipes_url}"
)
```

### 8.2 Notif "Liste prête"

**Fichier : `app/workflow_courses.py`**

```python
# Après push_groceries_to_notion()
notify_ntfy(
    "🛒 Liste prête — ouvre ta vue Courses",
    f"Ouvre ta vue Courses – Mobile\n{notion_courses_url}"
)
```

---

## 🚀 Phase 9 : Workflows GitHub Actions

### 9.1 Workflow "Proposer Recettes"

**Fichier : `.github/workflows/propose-recipes.yml` (nouveau)**

```yaml
name: Proposer Recettes

on:
  workflow_dispatch:

jobs:
  propose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python -m app.workflow_recipes
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          SPOONACULAR_API_KEY: ${{ secrets.SPOONACULAR_API_KEY }}
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_RECIPES_DB: ${{ secrets.NOTION_RECIPES_DB }}
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
```

### 9.2 Workflow "Générer Courses"

**Fichier : `.github/workflows/generate-courses.yml` (nouveau)**

```yaml
name: Générer Courses

on:
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python -m app.workflow_courses
        env:
          SPOONACULAR_API_KEY: ${{ secrets.SPOONACULAR_API_KEY }}
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
          NOTION_RECIPES_DB: ${{ secrets.NOTION_RECIPES_DB }}
          NOTION_GROCERIES_DB: ${{ secrets.NOTION_GROCERIES_DB }}
          NOTION_STOCK_DB: ${{ secrets.NOTION_STOCK_DB }}
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
```

---

## ✅ Critères d'acceptation

### Test 1 : Proposer Recettes
- [ ] Après `python -m app.workflow_recipes`, 6 entrées apparaissent dans Recettes
- [ ] Chaque recette a : `Semaine = "Semaine XX – YYYY"`, `Sélectionnée = false`, `Portions = 1`
- [ ] Notif ntfy reçue avec lien vers vue Notion

### Test 2 : Générer Courses
- [ ] Après avoir coché 3 recettes et réglé Portions dans Notion
- [ ] Après `python -m app.workflow_courses` :
  - [ ] Lit les 3 recettes sélectionnées
  - [ ] Multiplie correctement les quantités par Portions
  - [ ] Soustrait les durables (pas les frais)
  - [ ] Remplace les lignes Courses de la même Semaine (pas de doublons)
  - [ ] Notif reçue avec lien vers vue Courses

### Test 3 : Vue Mobile
- [ ] Vue mobile Courses – "A acheter" n'affiche que `Acheté = false`
- [ ] Triée par Rayon
- [ ] Unités cohérentes (g/ml/pc)

---

## 📝 Fichiers à créer/modifier

### Nouveaux fichiers
- `app/utils.py` (helpers : week_label, notify_ntfy, extract_spoon_id)
- `app/workflow_recipes.py` (étape 1 : proposer recettes)
- `app/workflow_courses.py` (étape 2 : générer courses)
- `app/normalization.py` (normalisation ingrédients)
- `data/FOOD_SYNONYMS_ALL.json` (dictionnaire synonymes)
- `data/learned_synonyms.json` (synonymes appris)
- `.github/workflows/propose-recipes.yml`
- `.github/workflows/generate-courses.yml`

### Fichiers à modifier
- `app/config.py` (ajouter NTFY_TOPIC, HAS_NOTION)
- `app/spoonacular.py` (get_recipe_ingredients_with_quantities, extract_spoon_id)
- `app/shopping.py` (subtract_stock_from_groceries, convert_units, packaging)
- `integrations/notion/recipes.py` (gérer Portions, Sélectionnée, Semaine)
- `integrations/notion/groceries.py` (clear_courses_for_week, Semaine)
- `integrations/notion/mappers.py` (recipe_to_notion_properties, grocery_to_notion_properties)

---

## 🎯 Ordre d'implémentation recommandé

1. **Phase 0** : Config & Helpers (week_label, notify_ntfy)
2. **Phase 1** : Proposer recettes (workflow_recipes.py)
3. **Phase 2** : Lecture sélection (get_selected_recipes_this_week)
4. **Phase 3** : Ingrédients quantifiés (get_recipe_ingredients_with_quantities)
5. **Phase 4** : Normalisation (normalization.py)
6. **Phase 5** : Stock durable/frais (subtract_stock_from_groceries)
7. **Phase 6** : Push courses (clear_courses_for_week)
8. **Phase 7** : Pipeline complet (workflow_courses.py)
9. **Phase 8** : Notifications (intégrer dans workflows)
10. **Phase 9** : GitHub Actions (workflows)

---

## 📚 Notes importantes

- **Semaine = Select** : Toujours utiliser `week_label()` pour générer la valeur
- **Déclenchement manuel** : Pas d'auto périodique
- **Durable vs Frais** : Durable = soustrait, Frais = jamais soustrait
- **IA = fallback** : Uniquement sur résidus ambigus après normalisation
- **Idempotence** : `clear_courses_for_week()` avant insertion pour éviter doublons

