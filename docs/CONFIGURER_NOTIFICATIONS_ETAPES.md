# 📱 Configuration Complète : Notifications + Liens Notion

## 🎯 Objectif

Configurer les notifications push sur votre téléphone avec des liens cliquables vers vos vues Notion.

## 📋 Étape 1 : Configurer ntfy.sh (Notifications)

### 1.1 Générer un Topic Sécurisé

Un topic aléatoire a été généré : **`v8-vK551qEV_Fj4mjgYIAA`**

*(Vous pouvez en générer un nouveau si vous voulez : `python -c "import secrets; print(secrets.token_urlsafe(16))"`)*

### 1.2 Ajouter dans le fichier `.env`

1. Ouvrez ou créez le fichier `.env` dans `Appli-Food-Course/`
2. Ajoutez cette ligne :

```bash
NTFY_TOPIC=v8-vK551qEV_Fj4mjgYIAA
```

**Exemple de `.env` complet :**
```bash
# Notion
NOTION_TOKEN=secret_xxx
NOTION_API_KEY=secret_xxx
NOTION_RECIPES_DB=xxx
NOTION_GROCERIES_DB=xxx
NOTION_STOCK_DB=xxx

# Spoonacular
SPOONACULAR_API_KEY=xxx
SPOONACULAR_API_KEY2=yyy

# Notifications
NTFY_TOPIC=v8-vK551qEV_Fj4mjgYIAA
```

### 1.3 Installer l'App ntfy.sh

**Android :**
- [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
- [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/)

**iOS :**
- [App Store](https://apps.apple.com/app/ntfy/id1625396347)

### 1.4 S'abonner au Topic

1. Ouvrez l'app ntfy.sh
2. Cliquez sur **"+"** ou **"Subscribe to topic"**
3. Entrez : `v8-vK551qEV_Fj4mjgYIAA`
4. Cliquez sur **"Subscribe"**

### 1.5 Tester les Notifications

```bash
cd Appli-Food-Course
python -c "from app.utils import notify_ntfy; notify_ntfy('Test', 'Si vous recevez ce message, les notifications fonctionnent !')"
```

✅ Vous devriez recevoir une notification sur votre téléphone.

---

## 📋 Étape 2 : Obtenir les URLs des Vues Notion

### 2.1 URL de la Vue Recettes

1. Ouvrez votre base **Recettes** dans Notion
2. Créez ou sélectionnez une vue (ex: "Galerie mobile", "Table", etc.)
3. Cliquez sur **"Share"** (Partager) en haut à droite
4. Cliquez sur **"Copy link"** (Copier le lien)
5. Copiez l'URL complète

**Exemple d'URL :**
```
https://www.notion.so/your-workspace/Recettes-abc123def456?view=xyz789
```

### 2.2 URL de la Vue Courses

1. Ouvrez votre base **Courses** dans Notion
2. Créez ou sélectionnez une vue (ex: "A acheter", "Mobile", etc.)
3. Cliquez sur **"Share"** (Partager) en haut à droite
4. Cliquez sur **"Copy link"** (Copier le lien)
5. Copiez l'URL complète

**Exemple d'URL :**
```
https://www.notion.so/your-workspace/Courses-abc123def456?view=xyz789
```

---

## 📋 Étape 3 : Utiliser les URLs dans les Commandes

### 3.1 Proposer des Recettes (avec URL)

```bash
python -m app.workflow_recipes --n-candidates 6 --n-final 3 --notion-url "VOTRE_URL_RECETTES"
```

**Exemple :**
```bash
python -m app.workflow_recipes --n-candidates 6 --n-final 3 --notion-url "https://www.notion.so/your-workspace/Recettes-abc123def456?view=xyz789"
```

### 3.2 Générer les Courses (avec URL)

```bash
python -m app.workflow_courses --notion-url "VOTRE_URL_COURSES"
```

**Exemple :**
```bash
python -m app.workflow_courses --notion-url "https://www.notion.so/your-workspace/Courses-abc123def456?view=xyz789"
```

---

## 📋 Étape 4 : Configurer GitHub Actions (Optionnel)

Si vous utilisez les workflows GitHub Actions :

1. Allez sur votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Ajoutez :
   - **Nom** : `NTFY_TOPIC`
   - **Valeur** : `v8-vK551qEV_Fj4mjgYIAA`
5. Cliquez sur **Add secret**

**Note :** Les URLs Notion peuvent être passées directement dans les workflows GitHub Actions via les inputs.

---

## ✅ Résultat Attendu

### Notification "Recettes prêtes"

Quand vous lancez `workflow_recipes` :
```
Titre: Recettes pretes - choisis-en 3
Message: Ouvre ta vue Notion Recettes
         https://www.notion.so/your-workspace/Recettes-abc123def456?view=xyz789
```

✅ Cliquez sur la notification → Ouvre directement votre vue Recettes dans Notion

### Notification "Liste prête"

Quand vous lancez `workflow_courses` :
```
Titre: Liste prete - ouvre ta vue Courses
Message: Ouvre ta vue Courses
         https://www.notion.so/your-workspace/Courses-abc123def456?view=xyz789
```

✅ Cliquez sur la notification → Ouvre directement votre vue Courses dans Notion

---

## 🔧 Utilisation Sans URL (Optionnel)

Si vous ne voulez pas d'URL dans les notifications :

```bash
# Sans URL (notification simple)
python -m app.workflow_recipes --n-candidates 6 --n-final 3

# Sans URL (notification simple)
python -m app.workflow_courses
```

Les notifications fonctionneront mais sans lien cliquable.

---

## ❓ Dépannage

### Je ne reçois pas de notifications

1. ✅ Vérifiez que `NTFY_TOPIC` est dans votre `.env`
2. ✅ Vérifiez que vous êtes abonné au topic dans l'app
3. ✅ Testez avec la commande de test ci-dessus
4. ✅ Vérifiez les logs : s'il y a une erreur, elle sera affichée

### Les URLs ne fonctionnent pas

1. ✅ Vérifiez que l'URL est complète (commence par `https://`)
2. ✅ Vérifiez que la vue est partagée (Share → Copy link)
3. ✅ Testez l'URL dans un navigateur pour vérifier qu'elle fonctionne

### Les notifications fonctionnent localement mais pas sur GitHub Actions

1. ✅ Vérifiez que `NTFY_TOPIC` est dans les secrets GitHub
2. ✅ Vérifiez que le secret a exactement le même nom : `NTFY_TOPIC`

---

## 🎉 C'est tout !

Une fois configuré, vous recevrez automatiquement des notifications avec des liens cliquables vers vos vues Notion à chaque exécution des workflows.

