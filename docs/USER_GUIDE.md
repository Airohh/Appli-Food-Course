# Guide d'Utilisation - Appli Food Course

## 📖 Introduction

**Appli Food Course** est un système automatisé de planification de repas qui :
- Récupère des recettes depuis l'API Spoonacular
- Utilise l'IA (OpenAI) pour sélectionner les meilleures recettes
- Consolide les ingrédients et génère une liste de courses
- Synchronise avec Notion pour gérer le stock

## 🚀 Démarrage rapide

### Prérequis

1. **Compte GitHub** avec le repository configuré
2. **Secrets GitHub** configurés :
   - `NOTION_TOKEN` : Token d'API Notion
   - `OPENAI_API_KEY` : Clé API OpenAI
   - `SPOONACULAR_API_KEY` : Clé API Spoonacular
   - `SPOONACULAR_API_KEY2` : Clé API Spoonacular de secours (optionnel)

### Première utilisation

1. **Configurer les secrets GitHub** :
   - Va sur ton repository → Settings → Secrets and variables → Actions
   - Ajoute tous les secrets nécessaires

2. **Déclencher le pipeline** :
   - Via GitHub Actions (interface web)
   - Via raccourci mobile (voir section dédiée)
   - Via HTTP (curl ou script)

3. **Consulter les résultats** :
   - Va sur GitHub → ton repo → dossier `data/`
   - Consulte les fichiers générés :
     - `menu.json` : Recettes sélectionnées
     - `groceries.json` : Liste de courses consolidée
     - `achats_filtres.json` : Liste finale optimisée

## 📱 Utilisation via GitHub Actions

### Méthode 1 : Interface web

1. Va sur ton repository GitHub
2. Clique sur l'onglet **Actions**
3. Sélectionne le workflow dans la barre latérale :
   - **Run Notion Sync** : Exporte les bases Notion
   - **Run Pipeline** : Exécute le pipeline complet
4. Clique sur **Run workflow** (bouton en haut à droite)
5. Sélectionne la branche (généralement `main`)
6. Clique sur **Run workflow**

### Méthode 2 : Raccourci mobile

Voir le guide détaillé dans le [README.md](../README.md) pour :
- iOS (app Shortcuts)
- Android (app HTTP Shortcuts)

## 🔄 Workflows disponibles

### 1. Sync Notion

**Objectif** : Exporter toutes les bases Notion vers `data/notion_dump.json`

**Quand l'utiliser** :
- Pour sauvegarder les données Notion
- Pour synchroniser les données localement
- Automatiquement tous les 3 jours (workflow planifié)

**Résultat** :
- Fichier `data/notion_dump.json` mis à jour
- Contient : Recettes, Courses, Stock

**Temps d'exécution** : ~30 secondes à 2 minutes

### 2. Run Pipeline

**Objectif** : Générer un menu de recettes et une liste de courses

**Quand l'utiliser** :
- Pour planifier les repas de la semaine
- Pour générer une nouvelle liste de courses
- Quand le stock a changé

**Résultat** :
- `data/menu.json` : 6 recettes sélectionnées (par défaut)
- `data/groceries.json` : Liste de courses consolidée
- `data/achats_filtres.json` : Liste finale optimisée

**Temps d'exécution** : ~2 à 5 minutes

## 📊 Comprendre les fichiers générés

### `menu.json`

Contient les recettes sélectionnées avec tous leurs détails :

```json
[
  {
    "Nom": "Poulet grillé aux légumes",
    "Temps": 30,
    "Calories (~)": 450,
    "Protéines (g)": 45,
    "Lien": "https://example.com/recipe",
    "ingredients": [
      {
        "name": "poulet",
        "amount": 500,
        "unit": "g"
      },
      ...
    ]
  },
  ...
]
```

**Champs importants** :
- `Nom` : Nom de la recette
- `Temps` : Temps de préparation en minutes
- `Calories (~)` : Calories approximatives
- `Protéines (g)` : Protéines en grammes
- `Lien` : URL de la recette
- `ingredients` : Liste des ingrédients avec quantités

### `groceries.json`

Liste de courses consolidée (avant fusion finale) :

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

**Champs importants** :
- `Aliment` : Nom de l'aliment
- `Quantité` : Quantité nécessaire
- `Unité` : Unité de mesure (g, ml, pièces, etc.)
- `Recettes` : Recettes qui utilisent cet ingrédient

### `achats_filtres.json`

Liste finale optimisée pour les courses :

```json
[
  {
    "Aliment": "Poulet",
    "Quantité": 500,
    "Unité": "g",
    "Recettes": "Poulet grillé, Salade de quinoa",
    "Categorie": "",
    "Notes": ""
  },
  ...
]
```

**Différences avec `groceries.json`** :
- Doublons fusionnés avec matching flou
- Tri alphabétique
- Exclut les ingrédients déjà en stock
- Prêt à être utilisé pour faire les courses

## 🔧 Configuration avancée

### Variables d'environnement

Le pipeline utilise plusieurs variables d'environnement (configurées via GitHub Secrets) :

| Variable | Description | Requis |
|----------|-------------|--------|
| `NOTION_TOKEN` | Token d'API Notion | Oui (pour sync) |
| `OPENAI_API_KEY` | Clé API OpenAI | Oui (pour LLM) |
| `SPOONACULAR_API_KEY` | Clé API Spoonacular | Oui |
| `SPOONACULAR_API_KEY2` | Clé API Spoonacular de secours | Non |

### Paramètres du pipeline

Les paramètres peuvent être modifiés dans `app/config.py` ou via variables d'environnement :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `N_RECIPES_FINAL` | 6 | Nombre de recettes à sélectionner |
| `N_RECIPES_CANDIDATES` | 70 | Nombre de recettes candidates |
| `TARGET_CALORIES` | 2100 | Calories cibles par jour |
| `MAX_READY_MIN` | 45 | Temps max de préparation (minutes) |
| `DIET` | high-protein | Type de régime |

## ❓ FAQ

### Comment changer le nombre de recettes ?

Modifie la variable `N_RECIPES_FINAL` dans `app/config.py` ou via variable d'environnement.

### Comment exclure certains ingrédients ?

Ajoute-les à ton stock Notion. Le pipeline les exclura automatiquement de la liste de courses.

### Le pipeline prend trop de temps

C'est normal ! Le pipeline fait plusieurs appels API :
- Spoonacular : ~1-2 minutes
- OpenAI : ~30 secondes à 1 minute
- Notion : ~30 secondes

Total : ~2 à 5 minutes

### Les recettes ne correspondent pas à mes préférences

Le LLM sélectionne les recettes en fonction de :
- Ton stock actuel
- Les calories cibles
- Le temps de préparation max
- Le type de régime (high-protein par défaut)

Tu peux modifier ces paramètres dans `app/config.py`.

### Comment voir les logs ?

Les logs sont disponibles dans :
- GitHub Actions : Onglet "Actions" → Sélectionne un workflow → Voir les logs
- Localement : `data/logs/app.log` (si exécuté localement)

## 🆘 Dépannage

### Erreur : "OPENAI_API_KEY manquant"

**Solution** : Vérifie que le secret `OPENAI_API_KEY` est bien configuré dans GitHub Secrets.

### Erreur : "SPOONACULAR_API_KEY requis"

**Solution** : Vérifie que le secret `SPOONACULAR_API_KEY` est bien configuré dans GitHub Secrets.

### Erreur : "Quota exceeded" (Spoonacular)

**Solution** : 
- Vérifie ton quota Spoonacular
- Le pipeline utilise automatiquement `SPOONACULAR_API_KEY2` si disponible

### Les fichiers ne sont pas générés

**Vérifications** :
1. Le workflow s'est bien exécuté (pas d'erreurs)
2. Les secrets sont bien configurés
3. Les permissions GitHub Actions sont activées

### Le stock n'est pas pris en compte

**Solution** :
1. Vérifie que `data/stock.json` existe
2. Lance le workflow "Sync Notion" pour rafraîchir le stock
3. Vérifie que le format du stock est correct

## 📚 Ressources supplémentaires

- [Guide développeur](DEVELOPER_GUIDE.md)
- [Exemples d'utilisation](EXAMPLES.md)
- [Architecture du projet](ARCHITECTURE.md)
- [Guide de test](../tests/README.md)

