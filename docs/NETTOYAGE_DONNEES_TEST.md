# 🧹 Nettoyage des Données de Test

## Objectif

Supprimer toutes les données de test de vos bases Notion pour repartir proprement avec le système.

## ⚠️ Important

**Ne supprimez PAS la structure des bases** (les colonnes). Supprimez seulement les **pages** (les lignes de données).

## 📋 Étapes de Nettoyage

### 1. Base Recettes

**Dans Notion :**
1. Ouvrez votre base **Recettes**
2. Sélectionnez **toutes les pages** (Ctrl+A ou Cmd+A)
3. Cliquez sur **"..."** (trois points) → **"Delete"** ou **"Supprimer"**
4. Confirmez la suppression

**Résultat :** La base est vide mais garde toutes ses colonnes (Name, Lien, Temps, Photo, Semaine, etc.)

### 2. Base Courses

**Dans Notion :**
1. Ouvrez votre base **Courses**
2. Sélectionnez **toutes les pages** (Ctrl+A ou Cmd+A)
3. Cliquez sur **"..."** (trois points) → **"Delete"** ou **"Supprimer"**
4. Confirmez la suppression

**Résultat :** La base est vide mais garde toutes ses colonnes (Aliment, Quantité, Unité, Semaine, etc.)

### 3. Base Stock

**Option A : Vider complètement (repartir à zéro)**

Si vous voulez repartir avec un stock vide :
1. Ouvrez votre base **Stock**
2. Sélectionnez **toutes les pages** (Ctrl+A ou Cmd+A)
3. Cliquez sur **"..."** (trois points) → **"Delete"** ou **"Supprimer"**
4. Confirmez la suppression

**Option B : Garder quelques items de test (recommandé pour tester)**

Si vous voulez tester la soustraction automatique :
1. Gardez quelques items de test dans le stock
2. Assurez-vous qu'ils ont une **Categorie** avec "durable" ou "frais"
   - Exemple : "Épicerie durable", "Fruits frais"
3. Mettez des quantités réalistes (ex: 500g de pâtes, 1L de lait)

**Résultat :** Vous pouvez tester la soustraction automatique du stock

## ✅ Vérification Après Nettoyage

Vérifiez que vos bases ont toujours leurs colonnes :

### Base Recettes - Colonnes requises :
- ✅ Name (Title)
- ✅ Lien (URL)
- ✅ Temps (Number)
- ✅ Photo (URL ou Files)
- ✅ Semaine (Select ou Multi-select)

### Base Courses - Colonnes requises :
- ✅ Aliment (Title)
- ✅ Quantité (Number)
- ✅ Unité (Rich Text)
- ✅ Semaine (Select ou Multi-select)

### Base Stock - Colonnes requises :
- ✅ Aliment (Title)
- ✅ Quantite ou Quantité (Number)
- ✅ Unité (Rich Text)
- ✅ Categorie ou Catégorie (Select) - **Important : doit contenir "durable" ou "frais"**

## 🚀 Après le Nettoyage

Une fois nettoyé, vous pouvez commencer à utiliser le système :

### 1. Test en mode dry-run (sans modifier Notion)

```bash
cd Appli-Food-Course

# Test proposition de recettes
python -m app.workflow_recipes --dry-run --n-candidates 3 --n-final 2
```

### 2. Première utilisation réelle

```bash
# Proposer des recettes
python -m app.workflow_recipes --n-candidates 6 --n-final 3

# Puis dans Notion, cochez 3 recettes et ajustez les portions

# Générer la liste de courses
python -m app.workflow_courses
```

## 💡 Astuce

Si vous voulez garder quelques données de test dans le stock pour tester la soustraction :

**Exemple de stock de test :**
- Pâtes : 500g, Unité: g, Categorie: "Épicerie durable"
- Riz : 1kg, Unité: g, Categorie: "Épicerie durable"
- Lait : 1L, Unité: ml, Categorie: "Frais"

Quand vous générerez les courses, les items "durable" seront automatiquement soustraits du stock, mais pas les "frais".

## ⚠️ Attention

- **Ne supprimez pas les bases elles-mêmes**, seulement les pages
- **Ne supprimez pas les colonnes**, gardez la structure
- Si vous supprimez accidentellement une colonne, recréez-la avec le même nom et type

