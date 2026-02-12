# 🔧 Configurer Make.com pour le Bouton Notion

Ce guide vous explique comment créer un bouton dans Notion qui déclenche la génération des courses via Make.com.

## 📋 Prérequis

1. ✅ Un compte Make.com (gratuit : https://www.make.com)
2. ✅ Un token GitHub avec la permission `workflow` (voir `docs/RACCOURCI_IOS.md`)
3. ✅ Votre repository GitHub : `VOTRE_USERNAME/Appli-Food-Course`

---

## 🚀 Étape 1 : Créer le Scénario Make.com

### 1.1 Créer un Nouveau Scénario

1. Connectez-vous à Make.com
2. Cliquez sur **"Create a new scenario"** ou **"Créer un scénario"**
3. Nommez-le : **"Générer Courses depuis Notion"**

### 1.2 Ajouter le Déclencheur Webhook

1. Cliquez sur **"Add a module"** ou **"Ajouter un module"**
2. Recherchez **"Webhooks"** → Sélectionnez **"Custom webhook"**
3. Cliquez sur **"Add"** ou **"Ajouter"**
4. Cliquez sur **"Save"** ou **"Enregistrer"**
5. **Copiez l'URL du webhook** (ex: `https://hook.make.com/xxxxxxxxxxxxx`)
   - ⚠️ **IMPORTANT** : Gardez cette URL, vous en aurez besoin pour Notion !

### 1.3 Ajouter l'Action HTTP (Appel GitHub)

1. Cliquez sur **"Add a module"** après le webhook
2. Recherchez **"HTTP"** → Sélectionnez **"Make an HTTP request"**
3. Configurez la requête :
   - **Method** : `POST`
   - **URL** : 
     ```
     https://api.github.com/repos/VOTRE_USERNAME/Appli-Food-Course/actions/workflows/generate-courses.yml/dispatches
     ```
     (Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur GitHub)
   - **Headers** :
     - Cliquez sur **"Add header"**
     - **Name** : `Authorization`
     - **Value** : `Bearer VOTRE_TOKEN_GITHUB`
       (Remplacez `VOTRE_TOKEN_GITHUB` par votre token GitHub)
     - Cliquez sur **"Add header"** à nouveau
     - **Name** : `Accept`
     - **Value** : `application/vnd.github+json`
   - **Body type** : `Raw`
   - **Content type** : `application/json`
   - **Request content** :
     ```json
     {
       "ref": "main"
     }
     ```

### 1.4 Tester le Scénario

1. Cliquez sur **"Run once"** ou **"Exécuter une fois"** en bas
2. Make.com va :
   - Générer une URL de webhook
   - Attendre que vous appeliez cette URL
3. **Testez manuellement** :
   - Ouvrez un nouvel onglet
   - Collez l'URL du webhook dans la barre d'adresse
   - Appuyez sur Entrée
   - Revenez à Make.com
   - Vous devriez voir que le webhook a été déclenché et que l'appel GitHub a été fait
4. Vérifiez sur GitHub :
   - Allez sur votre repository → **Actions**
   - Vous devriez voir un nouveau workflow "Générer Courses" en cours d'exécution

### 1.5 Activer le Scénario

1. Cliquez sur le bouton **"OFF"** en haut à droite pour l'activer
2. Le scénario est maintenant actif et attend les appels du bouton Notion

---

## 🔘 Étape 2 : Créer le Bouton dans Notion

### 2.1 Ajouter une Colonne Button

1. Ouvrez votre base **"Recettes"** dans Notion
2. Cliquez sur **"+"** à droite de la dernière colonne
3. Sélectionnez **"Button"** ou **"Bouton"**
4. Nommez-la : **"🛒 Générer Courses"**

### 2.2 Configurer l'Action du Bouton

1. Cliquez sur le bouton dans une ligne (ou créez une ligne de test)
2. Dans la configuration du bouton :
   - **Action type** : Sélectionnez **"Webhook"** ou **"Hook web"**
   - **URL** : Collez l'URL du webhook Make.com que vous avez copiée à l'étape 1.2
   - **Method** : `POST`
   - **Body** : (laissez vide ou ajoutez `{}`)

### 2.3 Tester le Bouton

1. Cliquez sur le bouton dans Notion
2. Vérifiez sur Make.com :
   - Allez sur votre scénario
   - Vous devriez voir une nouvelle exécution dans l'historique
3. Vérifiez sur GitHub :
   - Allez sur **Actions**
   - Le workflow "Générer Courses" devrait être déclenché

---

## 🎨 Étape 3 : Améliorer l'UX (Optionnel)

### 3.1 Ajouter une Notification dans Make.com

Vous pouvez ajouter une notification après l'appel GitHub :

1. Dans Make.com, ajoutez un module après l'appel HTTP
2. Recherchez **"Notifications"** → **"Send a notification"**
3. Configurez :
   - **Message** : "✅ Liste de courses générée !"
   - **Type** : Push notification (si vous avez l'app Make.com)

### 3.2 Personnaliser le Message

Vous pouvez personnaliser le message en fonction du résultat de l'appel GitHub.

---

## ✅ Vérification Finale

### Checklist

- [ ] Le scénario Make.com est créé et activé
- [ ] Le webhook Make.com est configuré
- [ ] L'appel HTTP vers GitHub est configuré avec le bon token
- [ ] Le bouton Notion est créé et configuré avec l'URL du webhook
- [ ] Le test fonctionne : clic sur le bouton → workflow GitHub déclenché

### Test Complet

1. **Dans Notion** :
   - Cochez "Sélectionnée" pour 3 recettes
   - Cliquez sur le bouton "🛒 Générer Courses"
2. **Vérifiez** :
   - Make.com : Nouvelle exécution visible
   - GitHub Actions : Workflow "Générer Courses" en cours
   - Notion : Base "Courses" mise à jour avec la liste

---

## 🐛 Dépannage

### Le bouton ne déclenche rien

1. **Vérifiez que le scénario Make.com est activé** (bouton "ON" en haut à droite)
2. **Vérifiez l'URL du webhook** dans le bouton Notion
3. **Testez le webhook directement** : Collez l'URL dans un navigateur et appuyez sur Entrée

### Le workflow GitHub ne se déclenche pas

1. **Vérifiez le token GitHub** dans Make.com
2. **Vérifiez l'URL** : Elle doit être exactement :
   ```
   https://api.github.com/repos/VOTRE_USERNAME/Appli-Food-Course/actions/workflows/generate-courses.yml/dispatches
   ```
3. **Vérifiez les headers** : `Authorization` et `Accept` doivent être corrects

### Erreur 401 (Unauthorized)

- Votre token GitHub est invalide ou expiré
- Créez un nouveau token avec la permission `workflow`

### Erreur 404 (Not Found)

- L'URL du workflow est incorrecte
- Vérifiez le nom du fichier : `generate-courses.yml`
- Vérifiez le nom du repository : `Appli-Food-Course`

---

## 📊 Limites Make.com Gratuit

- **1000 opérations/mois** (gratuit)
- **2 scénarios actifs** simultanément
- Si vous générez les courses 2-3 fois par semaine, c'est largement suffisant (~100-150 opérations/mois)

---

## 🎉 C'est Tout !

Votre bouton Notion est maintenant configuré et fonctionnel ! 

**Workflow final** :
1. Widget iOS → Proposer 6 recettes
2. Notion → Cocher 3 recettes
3. Bouton Notion → Générer les courses ! 🛒

---

## 📝 Notes

- Le bouton Notion peut être placé **au-dessus de la galerie** en créant une ligne d'en-tête
- Vous pouvez créer plusieurs boutons pour différents workflows
- Make.com conserve un historique de toutes les exécutions

