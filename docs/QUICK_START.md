# Guide de Démarrage Rapide

## 🚀 Première Utilisation

### 1. Configuration de base

Vérifiez votre fichier `.env` dans `Appli-Food-Course/` :

```bash
# Obligatoires
NOTION_TOKEN=secret_votre_token
NOTION_API_KEY=secret_votre_token  # Même valeur que NOTION_TOKEN
NOTION_RECIPES_DB=votre_id_base_recettes
NOTION_GROCERIES_DB=votre_id_base_courses
NOTION_STOCK_DB=votre_id_base_stock
SPOONACULAR_API_KEY=votre_cle_spoonacular

# Optionnel (pour les notifications)
NTFY_TOPIC=courses-ia  # Laissez vide si vous ne voulez pas de notifications
```

### 2. Notifications ntfy.sh (Optionnel)

**C'est quoi ?** Un service gratuit pour recevoir des notifications push sur votre téléphone.

**Comment l'utiliser ?**

**Option A : Topic public simple (moins sécurisé)**
1. Allez sur https://ntfy.sh
2. Créez un topic (ex: `courses-ia`)
3. Ajoutez dans `.env` : `NTFY_TOPIC=courses-ia`
4. Installez l'app ntfy.sh sur votre téléphone et abonnez-vous au topic

**Option B : Topic sécurisé (recommandé)**
1. Générez un nom de topic aléatoire (ex: `a1b2c3d4e5f6g7h8`)
   - Vous pouvez utiliser : https://www.random.org/strings/ (16 caractères alphanumériques)
   - Ou en ligne de commande : `python -c "import secrets; print(secrets.token_urlsafe(12))"`
2. Ajoutez dans `.env` : `NTFY_TOPIC=votre_topic_aleatoire`
3. Ajoutez `NTFY_TOPIC` dans les secrets GitHub (Settings → Secrets and variables → Actions)
4. Installez l'app ntfy.sh sur votre téléphone et abonnez-vous au topic

**Option C : Topic privé avec authentification (très sécurisé)**
1. Créez un compte sur https://ntfy.sh
2. Créez un topic privé avec un nom aléatoire
3. Configurez l'authentification (voir documentation ntfy.sh)
4. Ajoutez dans `.env` : `NTFY_TOPIC=votre_topic_aleatoire` et `NTFY_USER=votre_user` et `NTFY_PASS=votre_pass`

**Si vous ne voulez pas de notifications :**
- Laissez `NTFY_TOPIC` vide ou ne l'ajoutez pas
- Les notifications seront ignorées (un avertissement peut apparaître, mais ça ne bloque pas)

### 3. URLs Notion (Optionnel mais recommandé)

**C'est quoi ?** L'URL de la vue Notion que vous voulez ouvrir depuis la notification.

**Comment l'obtenir ?**
1. Ouvrez votre base Notion (Recettes ou Courses)
2. Créez ou ouvrez une vue (ex: "Galerie mobile" pour Recettes, "A acheter" pour Courses)
3. Cliquez sur **"Share"** (Partager) en haut à droite
4. Cliquez sur **"Copy link"** (Copier le lien)
5. Utilisez cette URL dans les commandes

**Exemple d'URL :**
```
https://www.notion.so/your-workspace/Recettes-abc123def456?view=abc789
```

**Si vous ne voulez pas d'URL :**
- Ne mettez pas `--notion-url` dans la commande
- Les notifications fonctionneront sans lien

## 📝 Commandes de Base

### Test en mode dry-run (sans modifier Notion)

```bash
cd Appli-Food-Course

# Test proposition de recettes
python -m app.workflow_recipes --dry-run --n-candidates 3 --n-final 2

# Test génération de courses
python -m app.workflow_courses --dry-run
```

### Utilisation réelle

**1. Proposer des recettes :**
```bash
# Sans URL (notifications sans lien)
python -m app.workflow_recipes --n-candidates 6 --n-final 3

# Avec URL (notifications avec lien cliquable)
python -m app.workflow_recipes --n-candidates 6 --n-final 3 --notion-url "https://notion.so/votre-vue-recettes"
```

**2. Générer la liste de courses :**
```bash
# Sans URL
python -m app.workflow_courses

# Avec URL
python -m app.workflow_courses --notion-url "https://notion.so/votre-vue-courses"
```

## ❓ Questions Fréquentes

### Q: Je n'ai pas configuré ntfy, est-ce grave ?
**R:** Non, c'est optionnel. Les notifications seront ignorées, mais tout le reste fonctionnera.

### Q: Je n'ai pas d'URL Notion, est-ce grave ?
**R:** Non, c'est optionnel. Les notifications fonctionneront sans lien cliquable.

### Q: Comment obtenir les IDs des bases Notion ?
**R:** 
1. Ouvrez votre base Notion
2. L'URL ressemble à : `https://www.notion.so/workspace/abc123def456`
3. L'ID est la partie après le dernier `/` : `abc123def456`
4. Copiez cet ID dans votre `.env`

### Q: Comment obtenir le token Notion ?
**R:**
1. Allez sur https://www.notion.so/my-integrations
2. Créez une nouvelle intégration
3. Copiez le "Internal Integration Token"
4. Partagez les bases avec cette intégration (Settings → Connections)

### Q: Les tests unitaires passent mais le workflow échoue ?
**R:** Vérifiez :
- Les IDs des bases dans `.env`
- Les permissions de l'intégration Notion
- Que les colonnes existent dans vos bases (voir `docs/SCHEMA_NOTION.md`)

### Q: J'ai une erreur "Photo is expected to be files" ?
**R:** Vérifiez que la colonne Photo est bien de type **URL** dans Notion (pas Files).

### Q: J'ai une erreur "Semaine is expected to be multi_select" ?
**R:** Le code gère maintenant automatiquement select et multi_select. Si l'erreur persiste, vérifiez que la colonne Semaine existe bien.

## 🔧 Dépannage

### Erreur : "Base Recettes non configurée"
→ Vérifiez `NOTION_RECIPES_DB` dans `.env`

### Erreur : "Clé API Notion manquante"
→ Vérifiez `NOTION_TOKEN` ou `NOTION_API_KEY` dans `.env`

### Erreur : "Aucune clé API Spoonacular"
→ Vérifiez `SPOONACULAR_API_KEY` dans `.env`

### Erreur : "Photo is expected to be files"
→ Changez la colonne Photo en type **URL** dans Notion

### Erreur : "Semaine is expected to be multi_select"
→ Le code devrait gérer automatiquement. Si l'erreur persiste, vérifiez que la colonne existe.

## 📚 Documentation Complète

- `docs/TESTING_GUIDE.md` : Guide de test complet
- `docs/SCHEMA_NOTION.md` : Schéma des bases Notion
- `docs/PLAN_ACTION_UX_MOBILE_REVISE.md` : Plan d'action détaillé

