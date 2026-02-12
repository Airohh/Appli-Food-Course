# 📱 Configuration des Notifications ntfy.sh

## 🎯 Objectif

Recevoir des notifications push sur votre téléphone quand :
- ✅ Des recettes sont proposées dans Notion
- ✅ La liste de courses est générée

## 📋 Étapes de Configuration

### Étape 1 : Générer un Topic Sécurisé

Un topic aléatoire a été généré pour vous : **`v8-vK551qEV_Fj4mjgYIAA`**

*(Vous pouvez aussi en générer un nouveau avec : `python -c "import secrets; print(secrets.token_urlsafe(16))"`)*

### Étape 2 : Configurer le .env Local

1. Créez ou modifiez le fichier `.env` dans `Appli-Food-Course/`

2. Ajoutez la ligne suivante :
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

### Étape 3 : Configurer les Secrets GitHub

1. Allez sur votre repository GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Cliquez sur **New repository secret**
4. Nom : `NTFY_TOPIC`
5. Valeur : `v8-vK551qEV_Fj4mjgYIAA`
6. Cliquez sur **Add secret**

### Étape 4 : Installer l'App ntfy.sh sur votre Téléphone

**Android :**
- Téléchargez depuis [Google Play](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
- Ou depuis [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/)

**iOS :**
- Téléchargez depuis [App Store](https://apps.apple.com/app/ntfy/id1625396347)

### Étape 5 : S'abonner au Topic

1. Ouvrez l'app ntfy.sh
2. Cliquez sur **"+"** ou **"Subscribe to topic"**
3. Entrez le nom du topic : `v8-vK551qEV_Fj4mjgYIAA`
4. Cliquez sur **"Subscribe"**

**Important :** Le topic est **public** mais avec un nom aléatoire, il est très difficile à deviner.

### Étape 6 : Tester les Notifications

**Test local :**
```bash
cd Appli-Food-Course
python -c "from app.utils import notify_ntfy; notify_ntfy('Test', 'Si vous recevez ce message, les notifications fonctionnent !')"
```

**Test avec le workflow :**
```bash
# Proposer des recettes (envoie une notif)
python -m app.workflow_recipes --n-candidates 3 --n-final 2

# Générer les courses (envoie une notif)
python -m app.workflow_courses
```

## ✅ Vérification

Vous devriez recevoir :
- 📱 Une notification sur votre téléphone
- 📝 Avec le titre et le message
- 🔗 Un lien cliquable vers Notion (si vous avez fourni l'URL)

## 🔒 Sécurité

### Topic Public (Recommandé pour commencer)

- ✅ Simple à configurer
- ✅ Pas besoin de compte
- ⚠️ Techniquement, quelqu'un pourrait s'abonner s'il devine le nom (très improbable avec un nom aléatoire)

### Topic Privé (Optionnel, plus sécurisé)

Si vous voulez une sécurité maximale :

1. Créez un compte sur https://ntfy.sh
2. Créez un topic privé
3. Configurez l'authentification
4. Ajoutez dans `.env` :
   ```bash
   NTFY_TOPIC=votre_topic_aleatoire
   NTFY_USER=votre_username
   NTFY_PASS=votre_password
   ```

Voir `docs/SECURITY.md` pour plus de détails.

## ❓ Dépannage

### Je ne reçois pas de notifications

1. **Vérifiez que le topic est correct** dans `.env`
2. **Vérifiez que vous êtes abonné** au topic dans l'app
3. **Testez avec la commande de test** ci-dessus
4. **Vérifiez les logs** : s'il y a une erreur, elle sera affichée dans la console

### Erreur "Topic not found"

- Vérifiez l'orthographe du topic dans `.env`
- Les topics sont créés automatiquement au premier message, pas besoin de les créer manuellement

### Les notifications fonctionnent localement mais pas sur GitHub Actions

- Vérifiez que `NTFY_TOPIC` est bien configuré dans les secrets GitHub
- Vérifiez que le secret a exactement le même nom : `NTFY_TOPIC`

## 📝 Exemple de Notifications

**Quand des recettes sont proposées :**
```
Titre: Recettes pretes - choisis-en 3
Message: Ouvre ta vue Notion Recettes
         https://notion.so/votre-vue-recettes
```

**Quand la liste de courses est générée :**
```
Titre: Liste prete - ouvre ta vue Courses
Message: Ouvre ta vue Courses
         https://notion.so/votre-vue-courses
```

## 🎉 C'est tout !

Une fois configuré, vous recevrez automatiquement des notifications à chaque exécution des workflows.

