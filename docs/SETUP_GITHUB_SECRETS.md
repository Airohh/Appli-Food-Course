# Guide : Configuration des Secrets GitHub

Ce guide t'explique étape par étape comment configurer tous les secrets nécessaires pour que le pipeline fonctionne avec GitHub Actions.

## 📋 Prérequis

- Un compte GitHub
- Un repository GitHub (ton repo Appli-Food-Course)
- Les clés API nécessaires (voir ci-dessous)

## 🔑 Secrets à configurer

### Secrets obligatoires

1. **NOTION_TOKEN** : Token d'API Notion
2. **NOTION_RECIPES_DB** : ID de la base Recettes
3. **NOTION_GROCERIES_DB** : ID de la base Courses
4. **OPENAI_API_KEY** : Clé API OpenAI
5. **SPOONACULAR_API_KEY** : Clé API Spoonacular

### Secrets optionnels

6. **NOTION_STOCK_DB** : ID de la base Stock (si tu utilises le stock)
7. **NOTION_MEALPLAN_DB** : ID de la base Meal Plan (pour la sync automatique)
8. **NOTION_SYNC_ENABLED** : `true` ou `false` (défaut: `false`)
9. **SPOONACULAR_API_KEY2** : Clé API Spoonacular de secours

---

## 📝 Étape 1 : Obtenir le Token Notion

### 1.1 Créer une intégration Notion

1. Va sur https://www.notion.so/my-integrations
2. Clique sur **"+ New integration"**
3. Donne un nom (ex: "Appli Food Course")
4. Sélectionne ton workspace
5. Clique sur **"Submit"**

### 1.2 Copier le token

1. Sur la page de l'intégration, tu verras **"Internal Integration Token"**
2. Clique sur **"Show"** puis **"Copy"**
3. Le token commence par `secret_...`
4. **⚠️ Garde-le précieusement**, tu ne pourras plus le voir après !

### 1.3 Partager les bases avec l'intégration

Pour chaque base Notion (Recettes, Courses, Stock, Meal Plan) :

1. Ouvre la base dans Notion
2. Clique sur les **"..."** en haut à droite
3. Va dans **"Connections"** ou **"Add connections"**
4. Sélectionne ton intégration "Appli Food Course"
5. Répète pour toutes les bases

---

## 📝 Étape 2 : Récupérer les IDs des bases Notion

### Méthode 1 : Depuis l'URL

1. Ouvre ta base Notion dans le navigateur
2. L'URL ressemble à :
   ```
   https://www.notion.so/workspace/2a29b6cbc7g480kab4ede102de3b2984?v=...
   ```
3. L'ID est la partie `2a29b6ccc7e480eab4ede002ce3b2984` (32 caractères)
4. Copie cet ID

### Méthode 2 : Via l'outil de diagnostic

1. Clone ton repo localement
2. Crée un fichier `.env` avec :
   ```
   NOTION_TOKEN=secret_ton_token_ici
   ```
3. Lance :
   ```bash
   python -m notion_tools.diagnostics.check_notion
   ```
4. L'outil va afficher les IDs des bases configurées

### Méthode 3 : Depuis databases.json

Si tu as déjà un fichier `databases.json`, les IDs sont dedans :
```json
[
  "2a29b6ccc7e480eab4ede002ce3b2984",  // Recettes
  "2a29b6ccc7e48080b7e7ec94e052e98f",  // Courses
  "2a29b6ccc7e480949befe46134ebf834"   // Stock
]
```

---

## 📝 Étape 3 : Obtenir la clé API OpenAI

1. Va sur https://platform.openai.com/api-keys
2. Connecte-toi avec ton compte OpenAI
3. Clique sur **"+ Create new secret key"**
4. Donne un nom (ex: "Appli Food Course")
5. Clique sur **"Create secret key"**
6. **⚠️ Copie la clé immédiatement**, elle commence par `sk-...`
7. Tu ne pourras plus la voir après !

---

## 📝 Étape 4 : Obtenir la clé API Spoonacular

1. Va sur https://spoonacular.com/food-api
2. Clique sur **"Get your API key"** ou **"Sign up"**
3. Crée un compte (gratuit jusqu'à 150 requêtes/jour)
4. Une fois connecté, va dans **"Profile"** → **"API Key"**
5. Copie ta clé API
6. (Optionnel) Si tu as un plan payant, tu peux créer une 2ème clé pour `SPOONACULAR_API_KEY2`

---

## 📝 Étape 5 : Configurer les secrets dans GitHub

### 5.1 Accéder aux secrets

1. Va sur ton repository GitHub
2. Clique sur **"Settings"** (en haut du repo)
3. Dans le menu de gauche, clique sur **"Secrets and variables"**
4. Clique sur **"Actions"**

### 5.2 Ajouter chaque secret

Pour chaque secret, clique sur **"New repository secret"** :

#### Secret 1 : NOTION_TOKEN
- **Name** : `NOTION_TOKEN`
- **Secret** : `secret_ton_token_notion_ici`
- Clique sur **"Add secret"**

#### Secret 2 : NOTION_RECIPES_DB
- **Name** : `NOTION_RECIPES_DB`
- **Secret** : `2a29b6ccc7e480eab4ede002ce3b2984` (ton ID de base Recettes)
- Clique sur **"Add secret"**

#### Secret 3 : NOTION_GROCERIES_DB
- **Name** : `NOTION_GROCERIES_DB`
- **Secret** : `2a29b6ccc7e48080b7e7ec94e052e98f` (ton ID de base Courses)
- Clique sur **"Add secret"**

#### Secret 4 : NOTION_STOCK_DB (optionnel)
- **Name** : `NOTION_STOCK_DB`
- **Secret** : `2a29b6ccc7e480949befe46134ebf834` (ton ID de base Stock)
- Clique sur **"Add secret"**

#### Secret 5 : NOTION_MEALPLAN_DB (optionnel)
- **Name** : `NOTION_MEALPLAN_DB`
- **Secret** : `ton_id_base_mealplan_ici` (si tu as créé la base Meal Plan)
- Clique sur **"Add secret"**

#### Secret 6 : NOTION_SYNC_ENABLED (optionnel)
- **Name** : `NOTION_SYNC_ENABLED`
- **Secret** : `true` (pour activer la sync automatique) ou `false` (défaut)
- Clique sur **"Add secret"**

#### Secret 7 : OPENAI_API_KEY
- **Name** : `OPENAI_API_KEY`
- **Secret** : `sk-ton_token_openai_ici`
- Clique sur **"Add secret"**

#### Secret 8 : SPOONACULAR_API_KEY
- **Name** : `SPOONACULAR_API_KEY`
- **Secret** : `ton_token_spoonacular_ici`
- Clique sur **"Add secret"**

#### Secret 9 : SPOONACULAR_API_KEY2 (optionnel)
- **Name** : `SPOONACULAR_API_KEY2`
- **Secret** : `ton_token_spoonacular_2_ici` (clé de secours)
- Clique sur **"Add secret"**

### 5.3 Vérifier les secrets

Une fois tous les secrets ajoutés, tu devrais voir une liste comme ça :

```
NOTION_TOKEN                    ●●●●●●●●●●●●●●●●●●●
NOTION_RECIPES_DB               ●●●●●●●●●●●●●●●●●●●
NOTION_GROCERIES_DB             ●●●●●●●●●●●●●●●●●●●
NOTION_STOCK_DB                 ●●●●●●●●●●●●●●●●●●●
NOTION_MEALPLAN_DB              ●●●●●●●●●●●●●●●●●●●
NOTION_SYNC_ENABLED             ●●●●●●●●●●●●●●●●●●●
OPENAI_API_KEY                  ●●●●●●●●●●●●●●●●●●●
SPOONACULAR_API_KEY             ●●●●●●●●●●●●●●●●●●●
SPOONACULAR_API_KEY2            ●●●●●●●●●●●●●●●●●●●
```

---

## ✅ Étape 6 : Tester la configuration

### 6.1 Tester via GitHub Actions

1. Va sur ton repo → **"Actions"**
2. Sélectionne le workflow **"Run Pipeline (Production)"**
3. Clique sur **"Run workflow"**
4. Coche **"Synchroniser vers Notion"** si tu veux tester la sync
5. Clique sur **"Run workflow"**
6. Suis l'exécution dans les logs

### 6.2 Vérifier les erreurs

Si le workflow échoue, regarde les logs :
- **"NOTION_TOKEN manquant"** → Vérifie que le secret est bien configuré
- **"NOTION_RECIPES_DB manquant"** → Vérifie l'ID de la base
- **"Permission denied"** → Vérifie que l'intégration Notion a accès à la base
- **"Invalid API key"** → Vérifie que les tokens sont corrects

---

## 🔧 Configuration locale (pour tester)

Si tu veux tester localement avant de push sur GitHub :

1. Crée un fichier `.env` à la racine du projet :
   ```bash
   NOTION_TOKEN=secret_ton_token_ici
   NOTION_API_KEY=secret_ton_token_ici
   NOTION_RECIPES_DB=2a29b6ccc7e480eab4ede002ce3b2984
   NOTION_GROCERIES_DB=2a29b6ccc7e48080b7e7ec94e052e98f
   NOTION_STOCK_DB=2a29b6ccc7e480949befe46134ebf834
   NOTION_MEALPLAN_DB=ton_id_mealplan_ici
   NOTION_SYNC_ENABLED=true
   OPENAI_API_KEY=sk-ton_token_ici
   SPOONACULAR_API_KEY=ton_token_ici
   SPOONACULAR_API_KEY2=ton_token_2_ici
   ```

2. Teste en local :
   ```bash
   # Test dry-run (ne fait rien)
   python -m integrations.notion.recipes --dry-run
   
   # Test réel
   python -m app.main --mode prod
   ```

3. **⚠️ Important** : Ne commite JAMAIS le fichier `.env` ! Il est dans `.gitignore`

---

## 🆘 Dépannage

### Erreur : "NOTION_TOKEN manquant"

**Solution** :
1. Vérifie que le secret est bien nommé `NOTION_TOKEN` (pas `NOTION_API_KEY`)
2. Vérifie que tu as bien cliqué sur "Add secret" après avoir entré la valeur
3. Vérifie que tu es dans le bon repository

### Erreur : "Permission denied" sur Notion

**Solution** :
1. Vérifie que l'intégration Notion a accès à toutes les bases
2. Va sur chaque base → "..." → "Connections" → Vérifie que l'intégration est listée
3. Si elle n'y est pas, ajoute-la

### Erreur : "Invalid database ID"

**Solution** :
1. Vérifie que l'ID fait bien 32 caractères
2. Vérifie qu'il n'y a pas d'espaces avant/après
3. Utilise l'outil de diagnostic pour vérifier : `python -m notion_tools.diagnostics.check_notion`

### Erreur : "Rate limit exceeded" (Spoonacular)

**Solution** :
1. Vérifie ton quota sur https://spoonacular.com/food-api/console
2. Si tu as un plan payant, configure `SPOONACULAR_API_KEY2` comme clé de secours
3. Le pipeline basculera automatiquement sur la 2ème clé si la première est épuisée

---

## 📚 Ressources

- [Documentation Notion API](https://developers.notion.com/)
- [Documentation OpenAI API](https://platform.openai.com/docs)
- [Documentation Spoonacular API](https://spoonacular.com/food-api/docs)
- [Documentation GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## ✅ Checklist finale

Avant de lancer le pipeline, vérifie que tu as :

- [ ] Créé l'intégration Notion
- [ ] Partagé toutes les bases avec l'intégration
- [ ] Récupéré tous les IDs des bases
- [ ] Configuré `NOTION_TOKEN` dans GitHub Secrets
- [ ] Configuré `NOTION_RECIPES_DB` dans GitHub Secrets
- [ ] Configuré `NOTION_GROCERIES_DB` dans GitHub Secrets
- [ ] Configuré `OPENAI_API_KEY` dans GitHub Secrets
- [ ] Configuré `SPOONACULAR_API_KEY` dans GitHub Secrets
- [ ] (Optionnel) Configuré `NOTION_MEALPLAN_DB` si tu veux la sync automatique
- [ ] (Optionnel) Configuré `NOTION_SYNC_ENABLED=true` pour activer la sync
- [ ] Testé le workflow GitHub Actions

Une fois tout configuré, tu peux lancer le pipeline ! 🚀

