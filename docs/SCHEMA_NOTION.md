# Schéma des Bases de Données Notion

## 📋 Base Recettes

### Colonnes Requises
- **Name** (Title) : Nom de la recette
- **Lien** (URL) : Lien vers la recette Spoonacular
- **Temps** (Number) : Temps de préparation en minutes
- **Photo** (URL ou Files) : URL de l'image de la recette (le code détecte automatiquement le type)
- **Semaine** (Select ou Multi-select) : Label de la semaine (ex: "Semaine 46 – 2025") (le code détecte automatiquement le type)

### Colonnes Optionnelles
- **Calories** (Number) : Nombre de calories
- **Proteines** (Number) : Quantité de protéines en grammes
- **Ingredients** (Rich Text) : Liste des ingrédients
- **Portions** (Number) : Nombre de portions (optionnel, défaut: 2 si la colonne n'existe pas)
  - Si la colonne n'existe pas, le code utilisera toujours 2 portions par défaut
- **Sélectionnée** (Checkbox) : Si la recette est sélectionnée pour la semaine (optionnel)
  - Si la colonne n'existe pas, toutes les recettes de la semaine seront considérées comme sélectionnées
- **État** (Select) : Statut de la recette (ex: "Pas commencé", "Terminée")
  - Le code détecte automatiquement si "État" contient "termine" ou "completed"
- **Terminée** (Checkbox) : Alternative à "État" pour marquer une recette comme terminée

## 🛒 Base Courses

### Colonnes Requises
- **Aliment** (Title) : Nom de l'aliment
- **Quantité** (Number) : Quantité nécessaire
- **Unité** (Rich Text) : Unité de mesure (g, ml, pièce, etc.)
- **Semaine** (Select ou Multi-select) : Label de la semaine (ex: "Semaine 46 – 2025") (le code détecte automatiquement le type)

### Colonnes Optionnelles
- **Recettes** (Rich Text) : Noms des recettes qui nécessitent cet aliment
- **Statut** (Select) : Statut de la course (ex: "Pas commencé")
- **Catégorie** (Select) : Catégorie de l'aliment (ex: "Viande", "Légumes")
- **Acheté** (Checkbox) : Si l'article a été acheté

## 📦 Base Stock

### Colonnes Requises
- **Aliment** (Title) : Nom de l'aliment
- **Quantite** ou **Quantité** (Number) : Quantité en stock
- **Unité** (Rich Text) : Unité de mesure (g, ml, pièce, etc.)
- **Categorie** ou **Catégorie** (Select) : Catégorie de l'aliment
  - **Important** : Doit contenir "durable" ou "frais" pour la soustraction automatique
  - Exemples : "durable", "frais", "Épicerie durable", "Fruits frais"

### Colonnes Optionnelles
- **Expiration** (Date) : Date d'expiration
- **Place** (Rich Text) : Emplacement de stockage

## 🔧 Notes Importantes

### Gestion Flexible des Noms
Le code gère automatiquement les variations de noms :
- `Quantite` ou `Quantité`
- `Categorie` ou `Catégorie`
- `Terminée` (checkbox) ou `État` (select avec valeur "Terminée")

### Valeurs de "Categorie" pour la Soustraction
- **Durable** : Les aliments avec "durable" dans la catégorie sont soustraits du stock
- **Frais** : Les aliments avec "frais" dans la catégorie ne sont **jamais** soustraits

Exemples de catégories qui fonctionnent :
- ✅ "durable"
- ✅ "Épicerie durable"
- ✅ "Conserves durable"
- ✅ "frais"
- ✅ "Fruits frais"
- ✅ "Légumes frais"

### Valeurs de "État" pour les Recettes
Le code détecte automatiquement si une recette est terminée en cherchant :
- Checkbox `Terminée` = true
- Select `État` avec valeur contenant "termine", "completed", ou "done"

Exemples de valeurs qui fonctionnent :
- ✅ "Terminée"
- ✅ "Recette terminée"
- ✅ "Completed"
- ✅ "Done"

