# Tests

## Installation

```bash
pip install -r requirements.txt
```

## Exécution des tests

### Tous les tests
```bash
pytest tests/ -v
```

### Tests spécifiques
```bash
pytest tests/test_validators.py -v
pytest tests/test_retry.py -v
pytest tests/test_shopping.py -v
pytest tests/test_batch_processor.py -v
pytest tests/test_prompts.py -v
```

### Avec couverture
```bash
pytest tests/ --cov=app --cov-report=html
```

## Tests disponibles

### 1. `test_validators.py` - Validation des données
- ✅ Validation d'items de courses valides/invalides
- ✅ Validation de listes de courses
- ✅ Nettoyage et normalisation des items
- ✅ Validation de recettes

### 2. `test_retry.py` - Logique de retry
- ✅ Retry en cas de succès (pas de retry)
- ✅ Retry en cas d'échec puis succès
- ✅ Retry jusqu'à max_attempts
- ✅ Backoff exponentiel

### 3. `test_shopping.py` - Consolidation et fusion
- ✅ Normalisation des noms d'aliments
- ✅ Consolidation des ingrédients
- ✅ Déduplication dans merge_courses
- ✅ Filtrage du stock
- ✅ Préparation de l'index de stock

### 4. `test_batch_processor.py` - Traitement par batch
- ✅ Estimation des tokens
- ✅ Traitement de petites listes
- ✅ Traitement de grandes listes (batches)
- ✅ Gestion d'erreurs dans les batches

### 5. `test_prompts.py` - Prompts et versioning
- ✅ Chargement des prompts
- ✅ Gestion des prompts inexistants
- ✅ Récupération des versions
- ✅ Vérification que tous les prompts sont versionnés

## Tests manuels recommandés

### Test du pipeline complet (mode mock)
```bash
python -m app.main --mode mock --no-llm
```

### Test avec LLM (nécessite OPENAI_API_KEY)
```bash
python -m app.main --mode mock
```

### Test avec vraies APIs (nécessite toutes les clés)
```bash
python -m app.main --mode prod --refresh-stock
```

### Test de validation
```python
from app.validators import validate_courses_list
courses = [{"Aliment": "Poulet", "Quantité": 500, "Unité": "g"}]
is_valid, errors = validate_courses_list(courses)
print(f"Valid: {is_valid}, Errors: {errors}")
```

### Test de retry
```python
from app.retry import retry_openai

@retry_openai(max_attempts=3)
def test_function():
    # Votre fonction qui peut échouer
    pass
```

