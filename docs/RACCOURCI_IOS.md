# 📱 Raccourci iOS pour Générer les Courses

Sur iOS, vous pouvez créer un raccourci qui lance automatiquement la génération de la liste de courses.

> 📖 **Pour un guide complet avec les 2 widgets (Proposer Recettes + Générer Courses)**, consultez **[GUIDE_WIDGETS_IOS.md](GUIDE_WIDGETS_IOS.md)**

## 🎯 Solution 1 : Raccourci iOS (Recommandé)

### Étape 1 : Créer un Raccourci iOS

1. **Ouvrez l'app "Raccourcis"** sur votre iPhone/iPad
2. **Créez un nouveau raccourci** (bouton "+" en haut à droite)
3. **Nommez-le** : "🛒 Générer Courses"

### Étape 2 : Ajouter l'Action

Ajoutez ces actions dans l'ordre :

#### Action 1 : Obtenir le contenu de l'URL
- **Action** : "Obtenir le contenu de l'URL"
- **URL** : `https://api.github.com/repos/VOTRE_USERNAME/Appli-Food-Course/actions/workflows/generate-courses.yml/dispatches`
- **Méthode** : POST
- **En-têtes** :
  - `Authorization`: `Bearer VOTRE_TOKEN_GITHUB`
  - `Accept`: `application/vnd.github+json`
- **Corps** : JSON
  ```json
  {"ref":"main"}
  ```

#### Action 2 : Afficher une notification
- **Action** : "Afficher une notification"
- **Titre** : "✅ Liste de courses générée !"
- **Corps** : "Vérifiez votre base Notion Courses"

### Étape 3 : Créer un Token GitHub

1. Allez sur **GitHub.com** → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Cliquez sur **"Generate new token (classic)"**
3. Donnez-lui un nom : "Raccourci iOS Courses"
4. Cochez la permission **`workflow`**
5. Cliquez sur **"Generate token"**
6. **Copiez le token** (vous ne pourrez plus le voir après)

### Étape 4 : Configurer le Raccourci

1. Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur GitHub
2. Remplacez `VOTRE_TOKEN_GITHUB` par le token que vous venez de créer
3. Testez le raccourci !

### Étape 5 : Ajouter au Widget ou à l'Écran d'Accueil

1. **Widget** : Appuyez longuement sur l'écran d'accueil → "+" → Raccourcis → Sélectionnez votre raccourci
2. **Écran d'accueil** : Dans l'app Raccourcis, appuyez sur "..." → "Ajouter à l'écran d'accueil"

## 🎯 Solution 2 : Raccourci iOS avec Script Python (Avancé)

Si vous avez un serveur ou un Mac qui tourne en permanence :

### Étape 1 : Créer un Endpoint Webhook

Créez un endpoint qui lance le script Python (sur un serveur, Mac, etc.)

### Étape 2 : Créer le Raccourci

1. **Action** : "Obtenir le contenu de l'URL"
2. **URL** : Votre endpoint webhook
3. **Méthode** : POST

## 🎯 Solution 3 : Utiliser l'App GitHub (Simple)

1. **Installez l'app GitHub** sur iOS
2. Allez sur votre repository
3. **Actions** → **Générer Courses** → **Run workflow**
4. Cliquez sur **"Run workflow"**

C'est plus simple mais nécessite quelques clics.

## 🎯 Solution 4 : Bouton Notion avec Webhook (Le Plus Intégré)

### Étape 1 : Créer un Webhook GitHub

1. Allez sur votre repository GitHub
2. **Settings** → **Webhooks** → **Add webhook**
3. **Payload URL** : `https://api.github.com/repos/VOTRE_USERNAME/Appli-Food-Course/dispatches`
4. **Content type** : `application/json`
5. **Secret** : (optionnel, mais recommandé)

### Étape 2 : Créer un Bouton dans Notion

1. Dans votre base **Recettes**, ajoutez une colonne de type **Button**
2. Nommez-la "🛒 Générer Courses"
3. Configurez l'action :
   - **Type** : Webhook
   - **URL** : Votre endpoint webhook
   - **Méthode** : POST

**Note** : Cette solution nécessite un service intermédiaire (Zapier, Make, etc.) car Notion ne peut pas appeler directement GitHub.

## ✅ Solution Recommandée pour iOS

**Utilisez la Solution 1 (Raccourci iOS)** :
- ✅ Simple à configurer
- ✅ Un seul clic pour générer
- ✅ Peut être ajouté au widget
- ✅ Fonctionne partout (même sans Notion ouvert)

## 📋 Workflow Complet

1. **Lundi** : Lancez `workflow_recipes` (depuis votre Mac/PC ou GitHub Actions)
2. **Sélection** : Dans Notion sur iOS, cochez "Sélectionnée" pour 3 recettes
3. **Génération** : Appuyez sur le raccourci iOS "🛒 Générer Courses"
4. **Résultat** : La liste de courses est générée dans Notion !

## 🔧 Personnalisation

Vous pouvez personnaliser le raccourci pour :
- Afficher le nombre de recettes sélectionnées
- Envoyer une notification différente
- Ouvrir automatiquement Notion après génération

## ❓ Questions

### Q: Le raccourci fonctionne-t-il sans connexion Internet ?
**R:** Non, il nécessite une connexion Internet pour appeler l'API GitHub.

### Q: Puis-je utiliser plusieurs tokens GitHub ?
**R:** Oui, vous pouvez créer un token spécifique pour le raccourci iOS.

### Q: Le raccourci fonctionne-t-il sur iPad ?
**R:** Oui, les raccourcis iOS fonctionnent sur iPhone et iPad.

