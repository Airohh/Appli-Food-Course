# 📱 Guide Complet : Créer les 2 Widgets iOS

Ce guide vous explique comment créer **deux widgets iOS** pour votre workflow complet :
1. **Widget 1** : "📝 Proposer Recettes" → Propose 6 recettes dans Notion
2. **Widget 2** : "🛒 Générer Courses" → Génère la liste de courses depuis les recettes sélectionnées

---

## 🎯 Workflow Complet

1. **Appuyez sur Widget 1** → Le script propose 6 recettes dans Notion → **Vous recevez une notification** 📱
2. **Dans la notification** → Cliquez pour ouvrir Notion → Cochez "Sélectionnée" pour 3 recettes ✅
3. **Appuyez sur Widget 2** → Le script génère la liste de courses → **Vous recevez une notification** 📱 → Liste prête ! 🛒

---

## 📋 Prérequis

Avant de commencer, vous devez avoir :

1. ✅ Un **token GitHub** avec la permission `workflow`
2. ✅ Votre **nom d'utilisateur GitHub** (ex: `Airohh`)
3. ✅ L'app **"Raccourcis"** installée sur votre iPhone/iPad

---

## 🔑 Étape 0 : Créer un Token GitHub

Si vous n'avez pas encore de token GitHub :

1. Allez sur **GitHub.com** → Connectez-vous
2. Cliquez sur votre **photo de profil** (en haut à droite) → **Settings**
3. Dans le menu de gauche, allez dans **Developer settings**
4. Cliquez sur **Personal access tokens** → **Tokens (classic)**
5. Cliquez sur **"Generate new token (classic)"**
6. Donnez-lui un nom : **"Raccourcis iOS Appli Food"**
7. Cochez la permission **`workflow`** (dans la section "repo")
8. Cliquez sur **"Generate token"** (tout en bas)
9. **⚠️ COPIEZ LE TOKEN IMMÉDIATEMENT** (vous ne pourrez plus le voir après !)
   - Le token commence par `ghp_...`

**Note** : Vous pouvez utiliser le même token pour les deux widgets.

---

## 📝 Widget 1 : Proposer Recettes

### Étape 1 : Créer le Raccourci

1. **Ouvrez l'app "Raccourcis"** sur votre iPhone/iPad
   - Si vous ne l'avez pas, téléchargez-la depuis l'App Store
2. Cliquez sur le **"+"** en haut à droite
3. Cliquez sur **"Créer un raccourci"** ou **"Create Shortcut"**

### Étape 2 : Nommer le Raccourci

1. Cliquez sur **"Nouveau raccourci"** ou **"New Shortcut"** en haut
2. Donnez-lui un nom : **"📝 Proposer Recettes"**
3. Cliquez sur **"OK"** ou **"Done"**

### Étape 3 : Ajouter l'Action HTTP

1. Cliquez sur **"Ajouter une action"** ou **"Add Action"**
2. Dans la barre de recherche, tapez : **"Obtenir le contenu de l'URL"** ou **"Get Contents of URL"**
3. Sélectionnez cette action

### Étape 4 : Configurer l'URL

1. Dans le champ **"URL"**, collez :
   ```
   https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/propose-recipes.yml/dispatches
   ```
   ⚠️ **Remplacez `Airohh` par votre nom d'utilisateur GitHub si différent**

### Étape 5 : Changer la Méthode en POST

1. Cliquez sur **"Afficher plus"** ou **"Show More"** sous l'URL
2. Changez **"Méthode"** ou **"Method"** de **"GET"** à **"POST"**

### Étape 6 : Ajouter les En-têtes (Headers)

1. Cliquez sur **"En-têtes"** ou **"Headers"**
2. Cliquez sur **"Ajouter un champ"** ou **"Add Field"**

   **Premier header** :
   - **Clé** ou **Key** : `Authorization`
   - **Valeur** ou **Value** : `Bearer VOTRE_TOKEN_GITHUB`
     (Remplacez `VOTRE_TOKEN_GITHUB` par votre vrai token GitHub)

3. Cliquez sur **"Ajouter un champ"** à nouveau

   **Deuxième header** :
   - **Clé** ou **Key** : `Accept`
   - **Valeur** ou **Value** : `application/vnd.github+json`

### Étape 7 : Ajouter le Corps (Body)

1. Cliquez sur **"Corps de la requête"** ou **"Request Body"**
2. Sélectionnez **"JSON"** (pas "Texte" ni "Fichier")
3. Dans le champ JSON, collez exactement :
   ```json
   {"ref":"main"}
   ```

### Étape 8 : Ajouter une Notification Locale (Optionnel)

> **Note** : Le workflow GitHub Actions enverra déjà une notification via ntfy.sh quand les recettes seront proposées. Cette étape ajoute une notification locale supplémentaire sur votre iPhone.

1. Cliquez sur **"+"** en bas pour ajouter une nouvelle action
2. Recherchez **"Afficher une notification"** ou **"Show Notification"**
3. Sélectionnez cette action
4. Configurez :
   - **Titre** : `✅ Recettes proposées !`
   - **Corps** : `6 recettes ajoutées dans Notion`

### Étape 9 : Tester le Raccourci

1. Cliquez sur le bouton **"Play"** (▶️) en bas pour tester
2. Vous devriez voir :
   - Une notification locale (si vous avez ajouté l'étape 8)
   - Sur GitHub : Un nouveau workflow "Proposer Recettes" en cours d'exécution
   - **Après quelques secondes** : Une notification ntfy.sh "Recettes pretes - choisis-en 3" avec un lien vers Notion
3. Si ça ne fonctionne pas, vérifiez :
   - L'URL est correcte
   - Le token GitHub est correct
   - Les headers sont bien configurés
   - Votre configuration ntfy.sh dans les secrets GitHub (NTFY_TOPIC, etc.)

### Étape 10 : Ajouter au Widget

1. Dans l'app Raccourcis, appuyez sur **"..."** (trois points) en haut à droite du raccourci
2. Cliquez sur **"Ajouter à l'écran d'accueil"** ou **"Add to Home Screen"**
3. Personnalisez l'icône si vous voulez
4. Cliquez sur **"Ajouter"** ou **"Add"**

**OU** pour créer un widget :

1. Appuyez **longuement** sur l'écran d'accueil de votre iPhone
2. Cliquez sur le **"+"** en haut à gauche
3. Recherchez **"Raccourcis"** ou **"Shortcuts"**
4. Sélectionnez la taille de widget que vous voulez
5. Cliquez sur **"Ajouter un widget"**
6. Appuyez sur le widget pour le configurer
7. Sélectionnez votre raccourci **"📝 Proposer Recettes"**

---

## 🛒 Widget 2 : Générer Courses

### Étape 1 : Créer le Raccourci

1. **Ouvrez l'app "Raccourcis"** sur votre iPhone/iPad
2. Cliquez sur le **"+"** en haut à droite
3. Cliquez sur **"Créer un raccourci"** ou **"Create Shortcut"**

### Étape 2 : Nommer le Raccourci

1. Cliquez sur **"Nouveau raccourci"** ou **"New Shortcut"** en haut
2. Donnez-lui un nom : **"🛒 Générer Courses"**
3. Cliquez sur **"OK"** ou **"Done"**

### Étape 3 : Ajouter l'Action HTTP

1. Cliquez sur **"Ajouter une action"** ou **"Add Action"**
2. Dans la barre de recherche, tapez : **"Obtenir le contenu de l'URL"** ou **"Get Contents of URL"**
3. Sélectionnez cette action

### Étape 4 : Configurer l'URL

1. Dans le champ **"URL"**, collez :
   ```
   https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/generate-courses.yml/dispatches
   ```
   ⚠️ **Remplacez `Airohh` par votre nom d'utilisateur GitHub si différent**

### Étape 5 : Changer la Méthode en POST

1. Cliquez sur **"Afficher plus"** ou **"Show More"** sous l'URL
2. Changez **"Méthode"** ou **"Method"** de **"GET"** à **"POST"**

### Étape 6 : Ajouter les En-têtes (Headers)

1. Cliquez sur **"En-têtes"** ou **"Headers"**
2. Cliquez sur **"Ajouter un champ"** ou **"Add Field"**

   **Premier header** :
   - **Clé** ou **Key** : `Authorization`
   - **Valeur** ou **Value** : `Bearer VOTRE_TOKEN_GITHUB`
     (Remplacez `VOTRE_TOKEN_GITHUB` par votre vrai token GitHub - le même que pour le Widget 1)

3. Cliquez sur **"Ajouter un champ"** à nouveau

   **Deuxième header** :
   - **Clé** ou **Key** : `Accept`
   - **Valeur** ou **Value** : `application/vnd.github+json`

### Étape 7 : Ajouter le Corps (Body)

1. Cliquez sur **"Corps de la requête"** ou **"Request Body"**
2. Sélectionnez **"JSON"** (pas "Texte" ni "Fichier")
3. Dans le champ JSON, collez exactement :
   ```json
   {"ref":"main"}
   ```

### Étape 8 : Ajouter une Notification Locale (Optionnel)

> **Note** : Le workflow GitHub Actions enverra déjà une notification via ntfy.sh quand la liste sera générée. Cette étape ajoute une notification locale supplémentaire sur votre iPhone.

1. Cliquez sur **"+"** en bas pour ajouter une nouvelle action
2. Recherchez **"Afficher une notification"** ou **"Show Notification"**
3. Sélectionnez cette action
4. Configurez :
   - **Titre** : `✅ Liste de courses générée !`
   - **Corps** : `Vérifiez votre base Notion Courses`

### Étape 9 : Tester le Raccourci

1. Cliquez sur le bouton **"Play"** (▶️) en bas pour tester
2. Vous devriez voir :
   - Une notification locale (si vous avez ajouté l'étape 8)
   - Sur GitHub : Un nouveau workflow "Générer Courses" en cours d'exécution
   - **Après quelques secondes** : Une notification ntfy.sh "Liste prete - ouvre ta vue Courses" avec un lien vers Notion
3. Si ça ne fonctionne pas, vérifiez :
   - L'URL est correcte
   - Le token GitHub est correct
   - Les headers sont bien configurés
   - Votre configuration ntfy.sh dans les secrets GitHub (NTFY_TOPIC, etc.)

### Étape 10 : Ajouter au Widget

1. Dans l'app Raccourcis, appuyez sur **"..."** (trois points) en haut à droite du raccourci
2. Cliquez sur **"Ajouter à l'écran d'accueil"** ou **"Add to Home Screen"**
3. Personnalisez l'icône si vous voulez
4. Cliquez sur **"Ajouter"** ou **"Add"**

**OU** pour créer un widget :

1. Appuyez **longuement** sur l'écran d'accueil de votre iPhone
2. Cliquez sur le **"+"** en haut à gauche
3. Recherchez **"Raccourcis"** ou **"Shortcuts"**
4. Sélectionnez la taille de widget que vous voulez
5. Cliquez sur **"Ajouter un widget"**
6. Appuyez sur le widget pour le configurer
7. Sélectionnez votre raccourci **"🛒 Générer Courses"**

---

## ✅ Vérification Finale

### Checklist

- [ ] Token GitHub créé avec la permission `workflow`
- [ ] Widget 1 "📝 Proposer Recettes" créé et testé
- [ ] Widget 2 "🛒 Générer Courses" créé et testé
- [ ] Les deux widgets sont ajoutés à l'écran d'accueil
- [ ] Les deux workflows GitHub Actions fonctionnent

### Test Complet

1. **Appuyez sur Widget 1** :
   - ✅ Workflow "Proposer Recettes" déclenché sur GitHub
   - ✅ **Notification ntfy.sh reçue** : "Recettes pretes - choisis-en 3" avec lien vers Notion
   - ✅ 6 recettes ajoutées dans Notion

2. **Dans la notification** :
   - ✅ Cliquez sur le lien pour ouvrir Notion
   - ✅ Ouvrez la base "Recettes"
   - ✅ Cochez "Sélectionnée" pour 3 recettes

3. **Appuyez sur Widget 2** :
   - ✅ Workflow "Générer Courses" déclenché sur GitHub
   - ✅ **Notification ntfy.sh reçue** : "Liste prete - ouvre ta vue Courses" avec lien vers Notion
   - ✅ Liste de courses générée dans Notion

---

## 🐛 Dépannage

### Le raccourci ne fonctionne pas

**Erreur : "Impossible d'obtenir le contenu de l'URL"**
- Vérifiez votre connexion Internet
- Vérifiez que l'URL est correcte
- Vérifiez que le token GitHub est correct

**Erreur : "401 Unauthorized"**
- Votre token GitHub est invalide ou expiré
- Créez un nouveau token avec la permission `workflow`

**Erreur : "404 Not Found"**
- L'URL du workflow est incorrecte
- Vérifiez le nom du repository : `Appli-Food-Course`
- Vérifiez le nom du fichier workflow : `propose-recipes.yml` ou `generate-courses.yml`

### Le workflow GitHub ne se déclenche pas

1. Allez sur GitHub → Votre repository → **Actions**
2. Vérifiez que les workflows existent bien
3. Vérifiez que le token a la permission `workflow`
4. Vérifiez les logs du workflow pour voir l'erreur

### Le widget ne s'affiche pas

1. Vérifiez que le raccourci est bien créé dans l'app Raccourcis
2. Réessayez d'ajouter le widget à l'écran d'accueil
3. Redémarrez votre iPhone si nécessaire

---

## 🎨 Personnalisation

### Changer les Icônes

1. Dans l'app Raccourcis, ouvrez votre raccourci
2. Cliquez sur l'icône en haut à gauche
3. Choisissez une nouvelle icône et couleur

### Ajouter Plus d'Actions

Vous pouvez ajouter d'autres actions aux raccourcis :
- **Ouvrir Notion** : Après la génération, ouvrir automatiquement Notion
- **Envoyer un SMS** : Notifier quelqu'un d'autre
- **Ajouter au calendrier** : Planifier les courses

---

## 📊 Résumé des URLs

### Widget 1 : Proposer Recettes
```
URL: https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/propose-recipes.yml/dispatches
Méthode: POST
Headers:
  Authorization: Bearer VOTRE_TOKEN_GITHUB
  Accept: application/vnd.github+json
Body: {"ref":"main"}
```

### Widget 2 : Générer Courses
```
URL: https://api.github.com/repos/Airohh/Appli-Food-Course/actions/workflows/generate-courses.yml/dispatches
Méthode: POST
Headers:
  Authorization: Bearer VOTRE_TOKEN_GITHUB
  Accept: application/vnd.github+json
Body: {"ref":"main"}
```

⚠️ **N'oubliez pas de remplacer `Airohh` par votre nom d'utilisateur GitHub !**

---

## 🎉 C'est Tout !

Vous avez maintenant deux widgets iOS fonctionnels ! 

**Workflow final** :
1. 📝 **Widget 1** → Lance le script → **Notification reçue** → 6 recettes proposées dans Notion
2. ✅ **Dans la notification** → Cliquez pour ouvrir Notion → Sélectionner 3 recettes
3. 🛒 **Widget 2** → Lance le script → **Notification reçue** → Liste de courses générée !

**Les notifications ntfy.sh sont automatiques** : elles sont envoyées par les workflows GitHub Actions quand les scripts se terminent. Vous n'avez rien à configurer de plus ! 📱

Bon appétit ! 🍽️

