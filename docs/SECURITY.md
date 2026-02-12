# Guide de Sécurité

## 🔒 Sécurisation des Notifications ntfy.sh

### Pourquoi sécuriser ?

Par défaut, les topics ntfy.sh sont **publics** : n'importe qui peut s'abonner à votre topic s'il devine le nom. Pour éviter cela, utilisez un topic avec un nom aléatoire.

### Méthode 1 : Topic avec nom aléatoire (Recommandé)

**Générer un nom de topic aléatoire :**

```bash
# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})

# Linux/Mac
python3 -c "import secrets; print(secrets.token_urlsafe(12))"

# Ou en ligne : https://www.random.org/strings/
# - Longueur : 16
# - Caractères : Alphanumériques
```

**Exemple de topic sécurisé :** `a1B2c3D4e5F6g7H8`

**Configuration :**
1. Générez un topic aléatoire (16+ caractères)
2. Ajoutez dans `.env` : `NTFY_TOPIC=votre_topic_aleatoire`
3. Ajoutez `NTFY_TOPIC` dans les secrets GitHub
4. Abonnez-vous au topic sur votre téléphone

### Méthode 2 : Topic privé avec authentification (Très sécurisé)

**Configuration :**
1. Créez un compte sur https://ntfy.sh
2. Créez un topic privé avec un nom aléatoire
3. Configurez l'authentification (voir documentation ntfy.sh)
4. Ajoutez dans `.env` :
   ```
   NTFY_TOPIC=votre_topic_aleatoire
   NTFY_USER=votre_username
   NTFY_PASS=votre_password
   ```
5. Ajoutez ces 3 variables dans les secrets GitHub

## 🔐 Secrets GitHub

### Configuration des secrets

1. Allez sur votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Ajoutez chaque variable :

**Secrets obligatoires :**
- `NOTION_TOKEN` : Token d'intégration Notion
- `NOTION_API_KEY` : Même valeur que NOTION_TOKEN
- `NOTION_RECIPES_DB` : ID de la base Recettes
- `NOTION_GROCERIES_DB` : ID de la base Courses
- `NOTION_STOCK_DB` : ID de la base Stock
- `SPOONACULAR_API_KEY` : Clé API Spoonacular

**Secrets optionnels :**
- `SPOONACULAR_API_KEY2` : Clé API Spoonacular de secours
- `OPENAI_API_KEY` : Clé API OpenAI (si vous utilisez le LLM)
- `NTFY_TOPIC` : Topic ntfy.sh (si vous utilisez les notifications)
- `NTFY_USER` : Username ntfy.sh (si topic privé)
- `NTFY_PASS` : Password ntfy.sh (si topic privé)

### Vérification

Les workflows GitHub Actions utilisent automatiquement ces secrets. Vérifiez que tous les secrets sont configurés avant d'exécuter les workflows.

## 🛡️ Bonnes Pratiques

1. **Ne jamais commiter `.env`** : Vérifiez que `.env` est dans `.gitignore`
2. **Utiliser des topics aléatoires** : Au moins 16 caractères alphanumériques
3. **Rotater les secrets régulièrement** : Changez les tokens tous les 6-12 mois
4. **Limiter les permissions** : Donnez seulement les permissions nécessaires aux intégrations Notion
5. **Utiliser des topics privés** : Pour une sécurité maximale, utilisez l'authentification ntfy.sh

## 📝 Exemple de `.env` local

```bash
# Notion
NOTION_TOKEN=secret_xxx
NOTION_API_KEY=secret_xxx
NOTION_RECIPES_DB=abc123def456
NOTION_GROCERIES_DB=def456ghi789
NOTION_STOCK_DB=ghi789jkl012

# Spoonacular
SPOONACULAR_API_KEY=xxx
SPOONACULAR_API_KEY2=yyy

# Notifications (optionnel)
NTFY_TOPIC=a1B2c3D4e5F6g7H8  # Topic aléatoire sécurisé
# NTFY_USER=username  # Uniquement si topic privé
# NTFY_PASS=password  # Uniquement si topic privé
```

## ⚠️ Important

- **Ne partagez jamais vos secrets** publiquement
- **Ne commitez jamais `.env`** dans Git
- **Utilisez des topics aléatoires** pour ntfy.sh
- **Vérifiez les permissions** des intégrations Notion

