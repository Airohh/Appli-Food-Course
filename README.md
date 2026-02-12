# Appli Food/Course

Recettes pour 3 jours et courses en fonction du stock.

## 📋 Utilisation

### Workflows disponibles

Le projet contient 3 workflows GitHub Actions :

1. **Run Notion Sync** (`run-notion-sync.yml`) : Exporte toutes les bases Notion vers `data/notion_dump.json`
2. **Scheduled Notion Sync** (`scheduled-notion-sync.yml`) : Exécute automatiquement le sync Notion tous les 3 jours à 08:00 UTC
3. **Run Pipeline** (`run-pipeline.yml`) : Exécute le pipeline complet avec les vraies API (OpenAI + Spoonacular)

### Méthode 1 : Via l'interface GitHub

1. Va sur ton repository GitHub
2. Clique sur l'onglet **Actions**
3. Sélectionne le workflow que tu veux exécuter dans la barre latérale
4. Clique sur **Run workflow** (bouton en haut à droite)
5. Sélectionne la branche (généralement `main`)
6. Clique sur **Run workflow**

### Méthode 2 : Via HTTP (raccourci mobile)

Tu peux créer un raccourci sur ton téléphone pour déclencher les workflows à distance.

#### Prérequis

1. Crée un **Personal Access Token** GitHub :
   - Va sur GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Clique sur **Generate new token (classic)**
   - Donne-lui un nom (ex: "Workflow Trigger")
   - Coche la permission `workflow`
   - Clique sur **Generate token**
   - **Copie le token** (tu ne pourras plus le voir après)

2. Utilise ce token dans les commandes ci-dessous

#### Sync Notion (export des bases)

```bash
curl -X POST \
  -H "Authorization: Bearer TON_TOKEN_ICI" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-notion-sync.yml/dispatches \
  -d '{"ref":"main"}'
```

#### Pipeline complet (recettes + courses)

```bash
curl -X POST \
  -H "Authorization: Bearer TON_TOKEN_ICI" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches \
  -d '{"ref":"main"}'
```

#### Créer un raccourci iOS (app Shortcuts) - Guide détaillé

**Étape 1 : Ouvrir l'app Shortcuts**
- Ouvre l'app **Shortcuts** (icône bleue avec des carrés)
- Si tu ne l'as pas, télécharge-la depuis l'App Store

**Étape 2 : Créer un nouveau raccourci**
- Clique sur le **+** en haut à droite
- Ou clique sur "Créer un raccourci"

**Étape 3 : Ajouter l'action HTTP**
- Clique sur "Ajouter une action"
- Recherche "**Get Contents of URL**" ou "**Obtenir le contenu de l'URL**"
- Sélectionne cette action

**Étape 4 : Configurer l'URL**
- Dans le champ **URL**, colle :
  ```
  https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches
  ```

**Étape 5 : Changer la méthode en POST**
- Clique sur "**Afficher plus**" ou "**Show More**"
- Change **Method** de "GET" à "**POST**"

**Étape 6 : Ajouter les Headers**
- Clique sur "**Headers**" ou "**En-têtes**"
- Clique sur "**Ajouter un champ**" ou "**Add Field**"
- **Premier header** :
  - Clé : `Authorization`
  - Valeur : `Bearer TON_TOKEN_ICI` (remplace TON_TOKEN_ICI par ton vrai token)
- **Deuxième header** :
  - Clé : `Accept`
  - Valeur : `application/vnd.github+json`

**Étape 7 : Ajouter le Body**
- Clique sur "**Request Body**" ou "**Corps de la requête**"
- Sélectionne "**Texte**" ou "**Text**"
- Colle exactement :
  ```
  {"ref":"main"}
  ```

**Étape 8 : Tester le raccourci**
- Clique sur le bouton **Play** (▶️) en bas pour tester
- Tu devrais voir "Succès" ou "Success"

**Étape 9 : Nommer et ajouter à l'écran d'accueil**
- Clique sur "**Suivant**" en haut à droite
- Donne un nom (ex: "Pipeline Recettes")
- Clique sur "**Ajouter à l'écran d'accueil**"
- Personnalise l'icône si tu veux
- Clique sur "**Ajouter**"

**Résultat** : Tu auras maintenant un raccourci sur ton écran d'accueil. Un simple tap déclenchera le workflow !

---

#### Créer un raccourci Android (app HTTP Shortcuts) - Guide détaillé

**Étape 1 : Installer l'app**
- Va sur le Play Store
- Recherche "**HTTP Shortcuts**" (icône bleue avec une flèche)
- Installe l'app

**Étape 2 : Créer un nouveau raccourci**
- Ouvre l'app HTTP Shortcuts
- Clique sur le **+** en bas à droite
- Donne un nom (ex: "Pipeline Recettes")

**Étape 3 : Configurer l'URL**
- Dans le champ "**URL**", colle :
  ```
  https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches
  ```

**Étape 4 : Changer la méthode**
- Dans "**Method**", sélectionne "**POST**"

**Étape 5 : Ajouter les Headers**
- Clique sur "**Headers**" ou "**En-têtes**"
- Clique sur "**+ Ajouter**"
- **Premier header** :
  - Nom : `Authorization`
  - Valeur : `Bearer TON_TOKEN_ICI` (remplace TON_TOKEN_ICI par ton vrai token)
- Clique sur "**+ Ajouter**" à nouveau
- **Deuxième header** :
  - Nom : `Accept`
  - Valeur : `application/vnd.github+json`

**Étape 6 : Ajouter le Body**
- Clique sur "**Body**" ou "**Corps**"
- Sélectionne "**Text**" ou "**Texte**"
- Dans le champ texte, colle exactement :
  ```
  {"ref":"main"}
  ```

**Étape 7 : Tester le raccourci**
- Clique sur le bouton **Play** (▶️) en haut
- Tu devrais voir "200 OK" ou un message de succès

**Étape 8 : Créer un widget**
- Appuie longuement sur l'écran d'accueil
- Sélectionne "**Widgets**" ou "**Widgets**"
- Trouve "**HTTP Shortcuts**"
- Glisse le widget sur ton écran
- Sélectionne ton raccourci "Pipeline Recettes"

**Résultat** : Tu auras maintenant un widget sur ton écran d'accueil. Un simple tap déclenchera le workflow !

### Résultats après l'exécution

#### Workflow "Sync Notion"

**Ce qui se passe :**
1. Le workflow se connecte à Notion avec ton token
2. Il exporte toutes les bases (Recettes, Courses, Stock)
3. Il crée le fichier `data/notion_dump.json` avec toutes les données

**Où voir les résultats :**
- Va sur GitHub → ton repo → dossier `data/`
- Tu verras le fichier `notion_dump.json` mis à jour
- Le commit apparaît dans l'historique avec le message "update via dispatch"

**Temps d'exécution :** ~30 secondes à 2 minutes selon la taille des bases

---

#### Workflow "Run Pipeline" (Pipeline complet)

**Ce qui se passe :**
1. Le workflow rafraîchit le stock depuis Notion
2. Il appelle l'API Spoonacular pour récupérer des recettes candidates
3. Il utilise OpenAI (GPT) pour sélectionner les meilleures recettes
4. Il consolide les ingrédients et filtre ceux déjà en stock
5. Il génère 3 fichiers JSON

**Fichiers générés :**

1. **`data/menu.json`** 
   - Contient les recettes sélectionnées (6 par défaut)
   - Avec leurs ingrédients, temps de préparation, calories, protéines
   - Format : liste de recettes avec tous les détails

2. **`data/groceries.json`**
   - Liste de courses consolidée (avant fusion finale)
   - Ingrédients groupés par nom
   - Quantités sommées
   - Exclut les ingrédients déjà en stock

3. **`data/achats_filtres.json`**
   - Liste finale optimisée pour les courses
   - Fusion des doublons avec matching flou
   - Tri alphabétique
   - Prêt à être utilisé pour faire les courses

**Où voir les résultats :**
- Va sur GitHub → ton repo → dossier `data/`
- Tu verras les 3 fichiers mis à jour
- Le commit apparaît avec le message "update pipeline results [auto]"

**Temps d'exécution :** ~2 à 5 minutes (appels API OpenAI + Spoonacular)

**Exemple de contenu de `menu.json` :**
```json
[
  {
    "Nom": "Poulet grillé aux légumes",
    "Temps": 30,
    "Calories (~)": 450,
    "Protéines (g)": 45,
    "ingredients": [...]
  },
  ...
]
```

**Exemple de contenu de `achats_filtres.json` :**
```json
[
  {
    "Aliment": "Poulet",
    "Quantité": 500,
    "Unité": "g",
    "Recettes": "Poulet grillé, Salade de quinoa"
  },
  ...
]
```

**Les fichiers sont automatiquement commités et poussés sur GitHub**, donc tu peux les consulter directement depuis ton téléphone ou ton ordinateur !

### Configuration requise

Les secrets suivants doivent être configurés dans GitHub (Settings → Secrets and variables → Actions) :

- `NOTION_TOKEN` ou `NOTION_API_KEY` : Token d'API Notion
- `NOTION_RECIPES_DB` : ID de la base Recettes Notion
- `NOTION_GROCERIES_DB` : ID de la base Courses Notion
- `NOTION_STOCK_DB` : ID de la base Stock Notion (optionnel)
- `NOTION_MEALPLAN_DB` : ID de la base Meal Plan Notion (optionnel, pour la sync automatique)
- `NOTION_SYNC_ENABLED` : `true` pour activer la synchronisation automatique (défaut: `false`)
- `OPENAI_API_KEY` : Clé API OpenAI (pour le pipeline)
- `SPOONACULAR_API_KEY` : Clé API Spoonacular (pour le pipeline)
- `SPOONACULAR_API_KEY2` : Clé API Spoonacular de secours (optionnel, utilisée automatiquement si la première est épuisée)

## 🔄 Synchronisation Notion (Nouveau)

Le pipeline peut maintenant synchroniser automatiquement les résultats vers Notion :

> 📖 **Guide complet** : Voir [SETUP_GITHUB_SECRETS.md](docs/SETUP_GITHUB_SECRETS.md) pour un guide pas à pas détaillé sur la configuration des secrets GitHub.

### Setup Notion

#### 1. Créer la base Meal Plan (optionnel)

Si tu veux utiliser la synchronisation du plan de repas, crée une nouvelle base dans Notion avec les propriétés suivantes :

- **Date** (type: `date`) : Date du repas
- **Type** (type: `select`) : Options : "Petit-déjeuner", "Déjeuner", "Dîner"
- **Recette** (type: `relation`) : Relation vers la base Recettes
- **Portions** (type: `number`, optionnel) : Nombre de portions

#### 2. Récupérer les IDs des bases

1. Ouvre ta base Notion dans le navigateur
2. L'URL ressemble à : `https://www.notion.so/workspace/XXXXXXXXXXXXXX?v=...`
3. L'ID est la partie `XXXXXXXXXXXXXX` (32 caractères)
4. Tu peux aussi utiliser l'outil de diagnostic : `python -m notion_tools.diagnostics.check_notion`

#### 3. Configurer les variables d'environnement

Ajoute dans ton `.env` ou dans GitHub Secrets :

```bash
NOTION_API_KEY=secret_...
NOTION_RECIPES_DB=<ID_TA_BASE_RECETTES>
NOTION_GROCERIES_DB=<ID_TA_BASE_COURSES>
NOTION_MEALPLAN_DB=<ID_TA_BASE_MEALPLAN>  # Optionnel
NOTION_SYNC_ENABLED=true  # Active la sync automatique
```

Pour une configuration locale avec fichier, copie `databases.json.example` en `databases.json` et remplace les IDs par les tiens.

### Utilisation

#### Via le pipeline (automatique)

Si `NOTION_SYNC_ENABLED=true`, le pipeline synchronise automatiquement après génération des JSON :

```bash
python -m app.main --mode prod
```

Le pipeline va :
1. Générer `menu.json` et `achats_filtres.json`
2. Synchroniser les recettes vers Notion
3. Créer le plan de repas (si `NOTION_MEALPLAN_DB` configuré)
4. Synchroniser la liste de courses vers Notion

#### Via CLI (manuel)

Tu peux aussi synchroniser manuellement :

```bash
# Synchroniser les recettes
python -m integrations.notion.recipes --file data/menu.json

# Créer le plan de repas
python -m integrations.notion.mealplan --file data/menu.json --start-date 2024-01-15

# Synchroniser les courses
python -m integrations.notion.groceries --file data/achats_filtres.json
```

Tous les CLIs supportent `--dry-run` pour tester sans rien modifier :

```bash
python -m integrations.notion.recipes --dry-run
```

### Schémas Notion

#### Base Recettes

Propriétés recommandées :
- **Name** (title) : Nom de la recette
- **Lien** (url) : URL de la recette
- **Temps** (number) : Temps de préparation en minutes
- **Calories (~)** (number) : Calories
- **Protéines (g)** (number) : Protéines en grammes
- **Tags** (multi_select) : Tags de la recette
- **Image** (url) : URL de l'image
- **Ingrédients** (rich_text) : Liste des ingrédients

#### Base Courses

Propriétés recommandées :
- **Article** (title) : Nom de l'article
- **Catégorie** (select) : Catégorie (Viande, Légumes, etc.)
- **Quantité** (number) : Quantité nécessaire
- **Unité** (rich_text) : Unité (g, ml, pièce, etc.)
- **À acheter ?** (checkbox) : À acheter ou non
- **Recettes** (rich_text, optionnel) : Recettes qui utilisent cet ingrédient

#### Base Meal Plan

Propriétés recommandées :
- **Date** (date) : Date du repas
- **Type** (select) : Petit-déjeuner / Déjeuner / Dîner
- **Recette** (relation) : Relation vers la base Recettes
- **Portions** (number, optionnel) : Nombre de portions

## 🔗 Déclenchement HTTP (référence rapide)

### Sync Notion (export des bases)

Endpoint dispatch:

```
POST https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-notion-sync.yml/dispatches
Authorization: Bearer <GITHUB_TOKEN>
Accept: application/vnd.github+json
Body: {"ref":"main"}
```

Exemple `curl` :

```bash
curl -X POST \
  -H "Authorization: Bearer <GITHUB_TOKEN>" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-notion-sync.yml/dispatches \
  -d '{"ref":"main"}'
```

### Pipeline complet (recettes + courses)

Endpoint dispatch:

```
POST https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches
Authorization: Bearer <GITHUB_TOKEN>
Accept: application/vnd.github+json
Body: {"ref":"main"}
```

Exemple `curl` :

```bash
curl -X POST \
  -H "Authorization: Bearer <GITHUB_TOKEN>" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/run-pipeline.yml/dispatches \
  -d '{"ref":"main"}'
```

**Note** : Le pipeline utilise les vraies API (OpenAI et Spoonacular) et nécessite les secrets `OPENAI_API_KEY` et `SPOONACULAR_API_KEY`.

### Activer la synchronisation Notion dans GitHub Actions

Pour activer la synchronisation automatique vers Notion dans le workflow :

1. **Option 1** : Configurer le secret `NOTION_SYNC_ENABLED=true` dans GitHub Secrets
2. **Option 2** : Cocher la case "Synchroniser vers Notion" lors du déclenchement manuel du workflow

Si activée, la synchronisation se fait automatiquement après la génération des JSON (pas besoin d'étape supplémentaire).
