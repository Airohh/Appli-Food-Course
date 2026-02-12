# Architecture - Appli Food Course

## Vue d'ensemble

Le projet est organisé en plusieurs modules qui travaillent ensemble pour générer un menu et une liste de courses.

## Structure du projet

```
Appli-Food-Course/
├── app/                    # Code principal
│   ├── main.py            # Pipeline principal
│   ├── config.py          # Configuration (env vars, IDs Notion)
│   ├── spoonacular.py     # Client API Spoonacular
│   ├── llm.py             # Appels LLM (OpenAI)
│   ├── shopping.py        # Consolidation et fusion des courses
│   ├── validators.py      # Validation des données
│   ├── retry.py           # Retry avec backoff
│   ├── logger.py          # Logging structuré
│   ├── batch_processor.py # Traitement par batch
│   ├── validator.py       # Validation post-normalisation
│   ├── prompts/           # Prompts pour le LLM
│   └── ...
├── notion_tools/          # Outils Notion (lecture/export)
│   ├── fetch/            # Récupération depuis Notion
│   ├── diagnostics/      # Outils de diagnostic
│   └── notion_reader.py  # Client Notion générique
├── integrations/         # Intégrations externes
│   └── notion/          # Synchronisation vers Notion (écriture)
├── scripts/              # Scripts utilitaires
├── data/                 # Données générées
├── tests/                # Tests unitaires
└── docs/                 # Documentation
```

## Flux de données

### Pipeline principal (`app/main.py`)

```
1. Récupération recettes (Spoonacular)
   ↓
2. Sélection recettes (LLM ou heuristique)
   ↓
3. Enrichissement avec ingrédients
   ↓
4. Consolidation ingrédients
   ↓
5. Filtrage stock
   ↓
6. Fusion et déduplication
   ↓
7. Nettoyage LLM (optionnel)
   ↓
8. Complétion quantités LLM (optionnel)
   ↓
9. Génération fichiers JSON
```

### Fichiers générés

- `data/menu.json` : Recettes sélectionnées
- `data/groceries.json` : Liste de courses consolidée
- `data/achats_filtres.json` : Liste finale optimisée

## Modules principaux

### `app/main.py`

**Responsabilité** : Orchestre le pipeline complet

**Fonctions clés** :
- `build_pipeline()` : Fonction principale qui exécute tout
- `_enrich_with_ingredients()` : Ajoute les ingrédients aux recettes
- `_stock_names()` : Extrait les noms du stock
- `_has_quantities()` : Vérifie si des quantités sont présentes

**Dépendances** :
- `spoonacular.py` : Pour récupérer les recettes
- `llm.py` : Pour sélectionner et nettoyer
- `shopping.py` : Pour consolider et fusionner

### `app/spoonacular.py`

**Responsabilité** : Interagit avec l'API Spoonacular

**Fonctions clés** :
- `complex_search()` : Recherche de recettes
- `normalize()` : Simplifie une recette Spoonacular
- `get_candidate_recipes()` : Récupère les recettes (ou mock)

**Gestion d'erreurs** :
- Retry automatique avec `retry_http`
- Bascule vers clé de secours si quota atteint (402)
- Mode mock si pas de clé API

### `app/llm.py`

**Responsabilité** : Appels LLM pour sélection et nettoyage

**Fonctions clés** :
- `choose_recipes()` : Sélectionne les meilleures recettes
- `deduplicate_courses_llm()` : Nettoie les doublons
- `complete_quantities_llm()` : Remplit les quantités manquantes
- `consolidate_groceries_llm()` : Consolidation via LLM (fallback)

**Gestion d'erreurs** :
- Retry automatique avec `retry_openai`
- Validation avant/après chaque appel
- Fallback vers consolidation locale si erreur

### `app/shopping.py`

**Responsabilité** : Consolidation et fusion des ingrédients

**Fonctions clés** :
- `consolidate_groceries()` : Regroupe les ingrédients par nom
- `merge_courses()` : Fusionne les doublons avec matching flou
- `normalize_aliment()` : Normalise les noms d'aliments
- `prepare_stock_lookup()` : Charge le stock depuis JSON

**Algorithme de matching** :
- Normalisation : minuscules, sans accents
- Matching flou : `SequenceMatcher` avec seuil 0.88
- Filtrage stock : exclut ce qui est déjà disponible

### `app/validators.py`

**Responsabilité** : Validation des structures de données

**Fonctions clés** :
- `validate_course_item()` : Valide un item de course
- `validate_courses_list()` : Valide une liste de courses
- `sanitize_course_item()` : Nettoie un item invalide

**Utilisation** :
- Avant chaque appel LLM
- Après chaque réponse LLM
- Nettoyage automatique si validation échoue

### `app/retry.py`

**Responsabilité** : Retry automatique avec backoff exponentiel

**Décorateurs** :
- `retry_with_backoff()` : Générique
- `retry_openai()` : Spécialisé pour OpenAI
- `retry_http()` : Spécialisé pour HTTP

**Stratégie** :
- Délai initial : 1s
- Backoff : double à chaque tentative (1s, 2s, 4s...)
- Max attempts : 3 par défaut

### `app/config.py`

**Responsabilité** : Configuration centralisée

**Sources** :
1. Variables d'environnement (`.env`)
2. Fichier `databases.json` (IDs Notion)
3. Valeurs par défaut

**Variables importantes** :
- `OPENAI_API_KEY` : Clé OpenAI
- `SPOONACULAR_API_KEY` : Clé Spoonacular
- `NOTION_TOKEN` : Token Notion
- `N_RECIPES_FINAL` : Nombre de recettes (défaut: 6)

### `app/logger.py`

**Responsabilité** : Logging structuré

**Fonctions** :
- `log_llm_call()` : Log des appels LLM
- `log_api_call()` : Log des appels API
- `log_validation_error()` : Log des erreurs de validation
- `log_retry()` : Log des tentatives de retry

**Sorties** :
- Fichier : `data/logs/app.log`
- Console : stdout

## Notion Integration

### `notion_tools/`

**Structure** :
- `fetch/` : Récupération depuis Notion
  - `fetch_stock.py` : Stock
  - `fetch_recipes.py` : Recettes
  - `fetch_courses.py` : Courses
  - `export_json.py` : Export des bases en fichiers JSON séparés
- `diagnostics/` : Outils de diagnostic
  - `check_notion.py` : Vérification de l'accès aux bases
  - `debug_stock_schema.py` : Inspection du schéma Stock

**Client générique** : `notion_reader.py`
- Détection automatique du schéma
- Mapping dynamique des propriétés

### `integrations/notion/`

**Structure** :
- Synchronisation vers Notion (écriture/upsert)
  - `recipes.py` : Synchronisation des recettes
  - `groceries.py` : Synchronisation des courses
  - `mealplan.py` : Synchronisation du plan de repas
  - `client.py` : Client Notion avec gestion d'erreurs
  - `config.py` : Configuration validée (Pydantic)
  - `mappers.py` : Mapping des données vers les propriétés Notion
  - `upsert.py` : Logique d'upsert (création/mise à jour)
  - `models.py` : Modèles de données

## Gestion des erreurs

### Stratégie générale

1. **Retry automatique** : Pour les erreurs temporaires (réseau, rate limits)
2. **Validation** : Vérification avant/après chaque transformation
3. **Fallback** : Solutions de secours si une étape échoue
4. **Logging** : Toutes les erreurs sont loggées

### Exemples

- **Spoonacular 402** : Bascule vers clé de secours
- **OpenAI rate limit** : Retry avec backoff
- **LLM réponse invalide** : Fallback vers consolidation locale
- **Validation échouée** : Nettoyage automatique

## Configuration

### Variables d'environnement

Toutes les variables sont dans `.env` ou GitHub Secrets :

```
OPENAI_API_KEY=sk-...
SPOONACULAR_API_KEY=...
SPOONACULAR_API_KEY2=... (optionnel)
NOTION_TOKEN=secret_...
NOTION_RECIPES_DB=...
NOTION_GROCERIES_DB=...
NOTION_STOCK_DB=...
```

### Paramètres

Modifiables dans `app/config.py` ou via env vars :

- `N_RECIPES_FINAL` : Nombre de recettes (défaut: 6)
- `N_RECIPES_CANDIDATES` : Nombre de candidates (défaut: 70)
- `TARGET_CALORIES` : Calories cibles (défaut: 2100)
- `MAX_READY_MIN` : Temps max préparation (défaut: 45)
- `DIET` : Type de régime (défaut: "high-protein")

## Tests

### Structure

- `tests/test_*.py` : Tests unitaires
- `tests/run_manual_tests.py` : Tests manuels rapides

### Couverture

- 52 tests unitaires
- 10 modules testés
- ~75% de couverture

## Extensibilité

### Ajouter une nouvelle source de recettes

1. Créer un module similaire à `spoonacular.py`
2. Implémenter `get_candidate_recipes()`
3. Adapter `normalize()` pour le format
4. Intégrer dans `main.py`

### Ajouter une nouvelle étape de traitement

1. Créer la fonction dans le module approprié
2. L'appeler dans `build_pipeline()`
3. Ajouter la validation si nécessaire
4. Tester

### Modifier les prompts LLM

1. Modifier le fichier dans `app/prompts/`
2. Mettre à jour `PROMPT_VERSIONS` dans `llm.py`
3. Tester avec des données réelles

## Performance

### Optimisations actuelles

- Retry avec backoff pour éviter les appels inutiles
- Validation précoce pour détecter les erreurs rapidement
- Mode mock pour développement sans coûts API
- Batch processing disponible (pas encore intégré)

### Améliorations possibles

- Cache LLM normalizer (module existe mais pas intégré)
- Batch processing pour grandes listes
- Parallélisation des appels API
- Cache des réponses Spoonacular

## Sécurité

### Secrets

- Tous les secrets dans `.env` (non commité)
- GitHub Secrets pour les workflows
- Pas de secrets hardcodés

### Validation

- Validation stricte des entrées
- Sanitization des données
- Gestion des erreurs sans exposer d'infos sensibles

