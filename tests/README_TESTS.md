# Suite de Tests Unitaires Complète

## 📋 Vue d'ensemble

Cette suite de tests couvre tous les nouveaux modules et fonctionnalités implémentés pour le workflow mobile avec Notion.

## 🧪 Tests disponibles

### 1. `test_utils.py` - Fonctions utilitaires
- ✅ `week_label()` - Génération des labels de semaine
- ✅ `notify_ntfy()` - Envoi de notifications
- ✅ `extract_spoon_id_from_url()` - Extraction d'ID Spoonacular

**Couverture :**
- Format des labels de semaine
- Gestion des erreurs de notification
- Extraction d'ID depuis différentes URL

### 2. `test_workflow_recipes.py` - Workflow des recettes
- ✅ `archive_old_recipes()` - Archivage des anciennes recettes
- ✅ `transfer_purchased_to_stock()` - Transfert des courses achetées
- ✅ `propose_recipes_to_notion()` - Proposition de recettes

**Couverture :**
- Archivage en mode normal et dry_run
- Transfert des courses achetées vers le stock
- Pipeline complet de proposition de recettes
- Gestion des notifications

### 3. `test_workflow_courses.py` - Workflow des courses
- ✅ `get_selected_recipes_this_week()` - Lecture des recettes sélectionnées
- ✅ `generate_courses_from_selection()` - Génération de la liste de courses

**Couverture :**
- Filtrage par semaine et sélection
- Récupération des portions et spoon_id
- Génération complète avec agrégation
- Gestion des recettes sans spoon_id

### 4. `test_workflow_stock.py` - Workflow du stock
- ✅ `subtract_stock_when_recipe_completed()` - Soustraction du stock

**Couverture :**
- Soustraction quand recette terminée
- Gestion des recettes non terminées
- Gestion des recettes sans spoon_id
- Gestion des erreurs API

### 5. `test_shopping.py` (mis à jour) - Fonctions shopping
- ✅ `normalize_aliment()` - Normalisation des noms
- ✅ `consolidate_groceries()` - Consolidation
- ✅ `merge_courses()` - Fusion et déduplication
- ✅ `subtract_stock_from_groceries()` - Soustraction du stock
- ✅ `_convert_unit_for_subtraction()` - Conversion d'unités

**Couverture :**
- Soustraction avec stock durable/frais
- Conversions d'unités (g/kg, ml/l, etc.)
- Gestion des cas limites (quantités négatives, unités incompatibles)

### 6. `test_spoonacular.py` (mis à jour) - API Spoonacular
- ✅ `normalize()` - Normalisation des recettes
- ✅ `get_recipe_ingredients_with_quantities()` - Récupération des ingrédients

**Couverture :**
- Préservation de l'ID Spoonacular
- Multiplication des quantités par portions
- Gestion des erreurs API

### 7. `test_mappers.py` (nouveau) - Mappers Notion
- ✅ `recipe_to_notion_properties()` - Mapping des recettes
- ✅ `grocery_to_notion_properties()` - Mapping des courses

**Couverture :**
- Nouveaux champs : Portions, Sélectionnée, Semaine, Terminée
- Nouveaux champs courses : Semaine, Acheté
- Gestion des valeurs booléennes et select

## 🚀 Exécution des tests

### Tous les tests
```bash
pytest tests/ -v
```

### Tests spécifiques
```bash
# Tests utilitaires
pytest tests/test_utils.py -v

# Tests workflows
pytest tests/test_workflow_recipes.py -v
pytest tests/test_workflow_courses.py -v
pytest tests/test_workflow_stock.py -v

# Tests shopping
pytest tests/test_shopping.py -v

# Tests Spoonacular
pytest tests/test_spoonacular.py -v

# Tests mappers
pytest tests/test_mappers.py -v
```

### Avec couverture
```bash
pytest tests/ --cov=app --cov=integrations --cov-report=html
```

### Tests en mode verbose
```bash
pytest tests/ -v -s
```

## 📊 Statistiques

- **Nombre total de fichiers de tests** : 7 nouveaux/mis à jour
- **Nombre total de tests** : ~50+ tests unitaires
- **Couverture** : Tous les nouveaux modules principaux

## 🔍 Détails des tests

### Tests avec mocks
Tous les tests utilisent des mocks pour :
- Les appels API Notion
- Les appels API Spoonacular
- Les appels HTTP (ntfy.sh)
- Les opérations de fichiers

### Tests d'intégration
Les tests couvrent :
- Les workflows complets de bout en bout
- Les interactions entre modules
- La gestion d'erreurs

### Cas limites testés
- Données manquantes
- Valeurs par défaut
- Erreurs API
- Unités incompatibles
- Quantités négatives
- Recettes sans ID

## ✅ Critères de succès

Tous les tests doivent passer avant de merger :
```bash
pytest tests/ -v --tb=short
```

Si un test échoue, vérifier :
1. Les mocks sont correctement configurés
2. Les imports sont corrects
3. Les dépendances sont installées

