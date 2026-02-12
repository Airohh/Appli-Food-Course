## Plats Final

Projet reconstruit étape par étape pour automatiser la planification des repas.

### Structure

- `app/` : cœur applicatif (pipeline `main.py`, clients Spoonacular & LLM, utilitaires de consolidation, prompts, configuration).
- `integrations/notion/` : synchronisation avec Notion (recipes, groceries, mealplan).
- `notion_tools/` : outils de lecture/écriture Notion.
  - `fetch/` : exports (`python -m notion_tools.fetch.fetch_stock`, etc.).
  - `diagnostics/` : vérifications et inspections (`python -m notion_tools.diagnostics.check_notion`).
- `data/` : instantanés JSON (`menu.json`, `groceries.json`, `achats_filtres.json`, `stock.json`, etc.) et exports d’archives.
- `scripts/` : utilitaires ponctuels (`python -m scripts.process_courses`).
- `docs/` : documentation (ce fichier).

### Scripts disponibles

- `python main.py [--refresh-stock] [--query ...]` : pipeline Spoonacular ➜ LLM ➜ consolidation locale (`data/menu.json`, `data/groceries.json`, `data/achats_filtres.json`).
- `python -m notion_tools.diagnostics.check_notion` : vérifie que les bases référencées dans `databases.json` sont accessibles.
- `python -m notion_tools.diagnostics.debug_stock_schema` : affiche le schéma complet de la base Stock (utile pour diagnostiquer les colonnes).
- `python -m notion_tools.fetch.fetch_stock` : exporte la base Stock vers `data/stock.json` (inclut toutes les colonnes + schéma Notion).
- `python -m notion_tools.fetch.export_json` : exporte les trois bases listées dans `databases.json` au format JSON (`data/exports/*.json`).
- `python -m notion_tools.fetch.fetch_recipes` : exporte la base Recettes vers `data/recipes.json`.
- `python -m notion_tools.fetch.fetch_courses` : exporte la base Courses vers `data/courses.json`.
- `python -m scripts.sync_notion` : exporte toutes les bases Notion vers `data/notion_dump.json`.
- `python -m app.main --mode prod` : pipeline complet avec synchronisation automatique vers Notion (via `integrations/notion/`).

### Workflow principal

Le pipeline principal (`python -m app.main --mode prod`) :
1. Récupère les recettes candidates depuis Spoonacular
2. Sélectionne les meilleures recettes via LLM
3. Génère la liste de courses consolidée
4. **Synchronise automatiquement** vers Notion (recettes, meal plan, courses) via `integrations/notion/`

### Workflows manuels (optionnels)

**Export des données Notion :**
- `python -m notion_tools.fetch.fetch_stock` : exporte le stock
- `python -m notion_tools.fetch.fetch_recipes` : exporte les recettes
- `python -m notion_tools.fetch.fetch_courses` : exporte les courses
- `python -m scripts.sync_notion` : exporte toutes les bases vers `data/notion_dump.json`

### Prérequis

- renseigner `NOTION_API_KEY`/`NOTION_TOKEN` et les identifiants des bases dans `databases.json` ou `.env`.
- ajouter `OPENAI_API_KEY` et `SPOONACULAR_API_KEY` dans `.env` pour activer le pipeline `main.py` (sinon bascule en mode mock ou erreur LLM).
- partager les bases (Stock, Recettes, Courses) avec l’intégration Notion correspondante.

Ce dépôt démarre minimal et sera enrichi progressivement.
