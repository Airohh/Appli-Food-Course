# 🔘 Ajouter un Bouton Notion pour Générer les Courses

Vous pouvez ajouter un bouton dans votre vue Galerie Notion qui lance automatiquement la génération de la liste de courses.

## 🎯 Solution Recommandée : Script Simple + Raccourci

### Option 1 : Script Python Simple (Le Plus Simple)

1. **Créez un fichier `generate_courses.py`** à la racine du projet (déjà créé ✅)

2. **Testez le script** :
   ```bash
   cd Appli-Food-Course
   python generate_courses.py
   ```

3. **Créez un raccourci** :
   - **Windows** : Créez un fichier `.bat` ou `.cmd` :
     ```batch
     @echo off
     cd /d "C:\Users\Utilisateur\Desktop\Plats Tot\Appli-Food-Course"
     python generate_courses.py
     pause
     ```
   - **Mac/Linux** : Créez un fichier `.sh` :
     ```bash
     #!/bin/bash
     cd "/path/to/Appli-Food-Course"
     python3 generate_courses.py
     ```

4. **Double-cliquez sur le raccourci** pour générer les courses !

### Option 2 : Bouton Notion avec Webhook (Avancé)

Notion permet d'ajouter des boutons qui déclenchent des webhooks. Voici comment :

#### Étape 1 : Créer un Endpoint Webhook

Vous pouvez utiliser :
- **GitHub Actions** avec un webhook
- **Un serveur local** (ngrok pour exposer)
- **Un service cloud** (Vercel, Railway, etc.)

#### Étape 2 : Créer un Bouton dans Notion

1. Dans votre base **Recettes**, ajoutez une colonne de type **Button**
2. Nommez-la "Générer Courses" ou "🛒 Générer"
3. Configurez l'action du bouton :
   - **Type** : Webhook
   - **URL** : Votre endpoint webhook
   - **Méthode** : POST

#### Étape 3 : Créer le Webhook Handler

Le webhook doit :
1. Lire les recettes sélectionnées dans Notion
2. Appeler `generate_courses_from_selection()`
3. Retourner un résultat

**Exemple avec GitHub Actions** :

```yaml
# .github/workflows/generate-courses-webhook.yml
name: Generate Courses (Webhook)

on:
  repository_dispatch:
    types: [generate-courses]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate courses
        env:
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          SPOONACULAR_API_KEY: ${{ secrets.SPOONACULAR_API_KEY }}
          # ... autres variables
        run: python generate_courses.py
```

### Option 3 : Automatisation Notion (Si Disponible)

Si vous avez accès aux **Automatisations Notion** :

1. Créez une automatisation
2. **Déclencheur** : Quand un bouton est cliqué
3. **Action** : Appeler un webhook ou une intégration

## 🚀 Solution la Plus Simple : Raccourci Desktop

### Windows

1. Créez un fichier `Générer Courses.bat` sur votre bureau :
   ```batch
   @echo off
   cd /d "C:\Users\Utilisateur\Desktop\Plats Tot\Appli-Food-Course"
   python generate_courses.py
   pause
   ```

2. Double-cliquez pour lancer !

### Mac

1. Créez un fichier `Générer Courses.command` :
   ```bash
   #!/bin/bash
   cd "/Users/VotreNom/Desktop/Plats Tot/Appli-Food-Course"
   python3 generate_courses.py
   ```

2. Rendez-le exécutable :
   ```bash
   chmod +x "Générer Courses.command"
   ```

3. Double-cliquez pour lancer !

### iOS

Voir le guide dédié : **[Raccourci iOS](RACCOURCI_IOS.md)**

## 📱 Alternative : Raccourci Mobile

Si vous utilisez Notion sur mobile, vous pouvez :

1. **Créer un raccourci iOS/Android** qui lance le script
2. **Utiliser un service cloud** (IFTTT, Zapier) pour déclencher le script
3. **Utiliser GitHub Actions** avec un bouton dans Notion

## ✅ Workflow Recommandé

1. **Lundi** : Lancez `workflow_recipes` → 6 recettes proposées
2. **Sélection** : Cochez "Sélectionnée" pour 3 recettes dans Notion
3. **Génération** : Double-cliquez sur le raccourci `Générer Courses.bat` → Liste générée !

## 🔧 Personnalisation

Vous pouvez modifier `generate_courses.py` pour :
- Ajouter des paramètres (semaine, dry-run, etc.)
- Afficher plus d'informations
- Envoyer des notifications personnalisées

## ❓ Questions

### Q: Le bouton Notion peut-il lancer directement le script ?
**R:** Non, Notion ne peut pas exécuter directement des scripts locaux. Il faut passer par un webhook ou utiliser un raccourci.

### Q: Puis-je utiliser un service cloud gratuit ?
**R:** Oui ! Vous pouvez utiliser :
- **GitHub Actions** (gratuit pour les repos publics)
- **Vercel** (gratuit)
- **Railway** (gratuit avec limites)
- **ngrok** (pour exposer un serveur local)

### Q: Le script fonctionne-t-il si je ne suis pas sur mon ordinateur ?
**R:** Non, le script doit être exécuté sur votre machine. Pour un accès distant, utilisez un service cloud (GitHub Actions, etc.).

