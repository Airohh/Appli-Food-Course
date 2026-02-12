# Exemples d'Utilisation - Appli Food Course

## 📝 Exemples pratiques

### Exemple 1 : Générer un menu pour la semaine

**Objectif** : Obtenir 6 recettes pour la semaine avec liste de courses

**Étapes** :
1. Déclencher le workflow "Run Pipeline" via GitHub Actions
2. Attendre ~2-5 minutes
3. Consulter les fichiers générés dans `data/`

**Résultat attendu** :
- `menu.json` : 6 recettes avec ingrédients
- `achats_filtres.json` : Liste de courses optimisée

### Exemple 2 : Synchroniser le stock depuis Notion

**Objectif** : Mettre à jour le stock local depuis Notion

**Étapes** :
1. Mettre à jour le stock dans Notion
2. Déclencher le workflow "Sync Notion"
3. Attendre ~30 secondes à 2 minutes
4. Vérifier `data/notion_dump.json` ou `data/stock.json`

**Résultat attendu** :
- Stock synchronisé localement
- Prêt pour le prochain pipeline

### Exemple 3 : Utiliser le pipeline en local

**Objectif** : Tester le pipeline localement sans GitHub Actions

**Prérequis** :
- Python 3.9+
- Variables d'environnement configurées (`.env`)

**Commandes** :
```bash
# Mode mock (sans API)
python -m app.main --mode mock --no-llm

# Mode production (avec vraies API)
python -m app.main --mode prod --refresh-stock

# Avec recherche spécifique
python -m app.main --mode prod --query "poulet"
```

**Résultat attendu** :
- Fichiers générés dans `data/`
- Logs dans la console

## 🔧 Exemples de configuration

### Exemple 1 : Modifier le nombre de recettes

**Fichier** : `app/config.py`

```python
# Par défaut : 6 recettes
N_RECIPES_FINAL = 6

# Pour 8 recettes
N_RECIPES_FINAL = 8
```

**Ou via variable d'environnement** :
```bash
export N_RECIPES_FINAL=8
python -m app.main --mode prod
```

### Exemple 2 : Changer le type de régime

**Fichier** : `app/config.py`

```python
# Par défaut : high-protein
DIET = "high-protein"

# Options disponibles :
# - "high-protein"
# - "vegetarian"
# - "vegan"
# - "ketogenic"
# - etc.
```

### Exemple 3 : Ajuster les calories cibles

**Fichier** : `app/config.py`

```python
# Par défaut : 2100 calories
TARGET_CALORIES = 2100

# Pour 2500 calories
TARGET_CALORIES = 2500
```

## 📊 Exemples de données

### Exemple de recette (menu.json)

```json
{
  "Nom": "Poulet grillé aux légumes",
  "Temps": 30,
  "Calories (~)": 450,
  "Protéines (g)": 45,
  "Lien": "https://spoonacular.com/recipe/12345",
  "ingredients": [
    {
      "name": "chicken breast",
      "amount": 500,
      "unit": "g"
    },
    {
      "name": "tomatoes",
      "amount": 2,
      "unit": "piece"
    },
    {
      "name": "olive oil",
      "amount": 2,
      "unit": "tbsp"
    }
  ]
}
```

### Exemple de liste de courses (achats_filtres.json)

```json
[
  {
    "Aliment": "Poulet",
    "Quantité": 500,
    "Unité": "g",
    "Recettes": "Poulet grillé, Salade de quinoa",
    "Categorie": "",
    "Notes": ""
  },
  {
    "Aliment": "Tomates",
    "Quantité": 4,
    "Unité": "pièces",
    "Recettes": "Poulet grillé, Salade de tomates",
    "Categorie": "",
    "Notes": ""
  }
]
```

### Exemple de stock (stock.json)

```json
{
  "__schema__": {
    "Aliment": "title",
    "Quantité": "number",
    "Unité": "rich_text",
    "Categorie": "select",
    "Expiration": "date"
  },
  "items": [
    {
      "Aliment": "Riz",
      "Quantité": 1000,
      "Unité": "g",
      "Categorie": "Céréales",
      "Expiration": "2024-12-31"
    }
  ]
}
```

## 🎯 Cas d'usage avancés

### Cas 1 : Menu végétarien

**Configuration** :
```python
DIET = "vegetarian"
N_RECIPES_FINAL = 6
```

**Résultat** : 6 recettes végétariennes sélectionnées

### Cas 2 : Menu rapide (< 30 min)

**Configuration** :
```python
MAX_READY_MIN = 30
N_RECIPES_FINAL = 6
```

**Résultat** : 6 recettes rapides (< 30 min)

### Cas 3 : Menu haute protéine

**Configuration** :
```python
DIET = "high-protein"
TARGET_CALORIES = 2500
N_RECIPES_FINAL = 8
```

**Résultat** : 8 recettes haute protéine pour 2500 calories

## 🔄 Workflows automatisés

### Workflow 1 : Sync quotidien

**Objectif** : Synchroniser Notion tous les jours

**Configuration GitHub Actions** :
```yaml
on:
  schedule:
    - cron: "0 8 * * *"  # Tous les jours à 8h UTC
```

### Workflow 2 : Pipeline hebdomadaire

**Objectif** : Générer un nouveau menu chaque semaine

**Configuration GitHub Actions** :
```yaml
on:
  schedule:
    - cron: "0 9 * * 1"  # Tous les lundis à 9h UTC
```

## 📱 Exemples de raccourcis

### Raccourci iOS (Shortcuts)

**Action** : Déclencher le pipeline

**Configuration** :
- URL : `https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches`
- Method : POST
- Headers :
  - `Authorization: Bearer TOKEN`
  - `Accept: application/vnd.github+json`
- Body : `{"ref":"main"}`

### Raccourci Android (HTTP Shortcuts)

**Action** : Déclencher le pipeline

**Configuration** :
- URL : `https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches`
- Method : POST
- Headers :
  - `Authorization: Bearer TOKEN`
  - `Accept: application/vnd.github+json`
- Body : `{"ref":"main"}`

## 🧪 Exemples de tests

### Test 1 : Validation des courses

```python
from app.validators import validate_courses_list

courses = [
    {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
]

is_valid, errors = validate_courses_list(courses)
print(f"Valid: {is_valid}, Errors: {errors}")
```

### Test 2 : Normalisation des aliments

```python
from app.shopping import normalize_aliment

assert normalize_aliment("Poulet") == "poulet"
assert normalize_aliment("  Tomates  ") == "tomates"
assert normalize_aliment("Épinards") == "epinards"
```

### Test 3 : Consolidation des ingrédients

```python
from app.shopping import consolidate_groceries

recipes = [
    {
        "Nom": "Recette 1",
        "ingredients": [
            {"name": "poulet", "amount": 200, "unit": "g"},
            {"name": "tomates", "amount": 2, "unit": "pièces"},
        ],
    },
    {
        "Nom": "Recette 2",
        "ingredients": [
            {"name": "poulet", "amount": 300, "unit": "g"},
        ],
    },
]

groceries = consolidate_groceries(recipes)
# Résultat : poulet = 500g (200 + 300), tomates = 2 pièces
```

## 💡 Conseils et bonnes pratiques

### Conseil 1 : Mettre à jour le stock régulièrement

**Pourquoi** : Le pipeline exclut automatiquement les ingrédients en stock

**Comment** :
- Mettre à jour le stock dans Notion
- Lancer "Sync Notion" avant le pipeline

### Conseil 2 : Utiliser les raccourcis mobiles

**Pourquoi** : Plus rapide et pratique

**Comment** : Voir section "Raccourcis" ci-dessus

### Conseil 3 : Vérifier les logs en cas d'erreur

**Pourquoi** : Les logs contiennent des informations utiles pour le dépannage

**Comment** :
- GitHub Actions : Onglet "Actions" → Workflow → Logs
- Localement : `data/logs/app.log`

### Conseil 4 : Tester en mode mock d'abord

**Pourquoi** : Évite les coûts API pendant le développement

**Comment** :
```bash
python -m app.main --mode mock --no-llm
```

