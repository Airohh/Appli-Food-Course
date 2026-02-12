# Guide de Test

## 🧪 Tests Disponibles

### Tests Unitaires (avec pytest)

#### Installation
```bash
pip install -r requirements.txt
```

#### Exécution
```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_validators.py -v
pytest tests/test_retry.py -v
pytest tests/test_shopping.py -v
pytest tests/test_batch_processor.py -v
pytest tests/test_prompts.py -v

# Avec couverture
pytest tests/ --cov=app --cov-report=html
```

### Tests Manuels Rapides

```bash
python tests/run_manual_tests.py
```

Ce script teste :
- ✅ Validation des courses
- ✅ Normalisation des aliments
- ✅ Nettoyage des items
- ✅ Versions des prompts

## 📋 Tests Fonctionnels

### 1. Test du Pipeline Complet (Mode Mock)

```bash
# Sans LLM (rapide)
python -m app.main --mode mock --no-llm

# Avec LLM (nécessite OPENAI_API_KEY)
python -m app.main --mode mock
```

**Vérifier :**
- ✅ Génération de `data/menu.json`
- ✅ Génération de `data/groceries.json`
- ✅ Génération de `data/achats_filtres.json`
- ✅ Pas d'erreurs dans la console

### 2. Test avec Vraies APIs (Mode Prod)

```bash
python -m app.main --mode prod --refresh-stock
```

**Vérifier :**
- ✅ Récupération des recettes depuis Spoonacular
- ✅ Sélection via LLM
- ✅ Consolidation et déduplication
- ✅ Complétion des quantités
- ✅ Synchronisation avec Notion (si configuré)

### 3. Test de Validation

```python
from app.validators import validate_courses_list

courses = [
    {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
]

is_valid, errors = validate_courses_list(courses)
print(f"Valid: {is_valid}, Errors: {errors}")
```

### 4. Test de Retry Logic

```python
from app.retry import retry_openai

@retry_openai(max_attempts=3)
def test_function():
    # Votre fonction qui peut échouer
    pass
```

### 5. Test de Normalisation

```python
from app.shopping import normalize_aliment

assert normalize_aliment("Poulet") == "poulet"
assert normalize_aliment("Épinards") == "epinards"
```

### 6. Test de Batch Processing

```python
from app.batch_processor import process_in_batches

items = [{"id": i} for i in range(100)]

def processor(batch):
    return [{"processed": item["id"]} for item in batch]

result = process_in_batches(items, processor, max_batch_size=30)
```

## 🔍 Tests d'Intégration

### Test Notion Sync

```bash
# Export des bases
python -m notion_tools.fetch.fetch_stock
python -m notion_tools.fetch.fetch_recipes
python -m notion_tools.fetch.fetch_courses

# Sync vers Notion
# Note: La synchronisation vers Notion se fait automatiquement via le pipeline principal
# python -m app.main --mode prod
# ou via les modules dans integrations/notion/
```

### Test GitHub Actions

1. **Workflow Notion Sync** :
   - Aller sur GitHub → Actions
   - Sélectionner "Run Notion Sync"
   - Cliquer sur "Run workflow"
   - Vérifier que `data/notion_dump.json` est créé/mis à jour

2. **Workflow Pipeline** :
   - Aller sur GitHub → Actions
   - Sélectionner "Run Pipeline"
   - Cliquer sur "Run workflow"
   - Vérifier que les fichiers JSON sont générés et commités

## ✅ Checklist de Tests

### Avant chaque commit
- [ ] `pytest tests/ -v` passe
- [ ] `python tests/run_manual_tests.py` passe
- [ ] Pipeline mock fonctionne : `python -m app.main --mode mock --no-llm`

### Avant chaque release
- [ ] Tous les tests unitaires passent
- [ ] Pipeline prod fonctionne (si APIs disponibles)
- [ ] Validation des données fonctionne
- [ ] Retry logic testé avec erreurs simulées
- [ ] Logs générés correctement

## 🐛 Debugging

### Activer les logs détaillés

```python
import logging
from app.logger import logger

logger.setLevel(logging.DEBUG)
```

### Vérifier les logs

```bash
# Logs de l'application
cat data/logs/app.log

# Logs du normalizer (si utilisé)
cat data/audit/normalizer_log.jsonl
```

## 📊 Métriques à Vérifier

- **Taux de succès des appels LLM** : vérifier `data/logs/app.log`
- **Coûts LLM** : vérifier les logs pour les estimations de coût
- **Temps d'exécution** : mesurer le temps du pipeline complet
- **Qualité des données** : vérifier que les quantités sont complétées

