# 📊 Analyse de l'Utilisation des Tokens Spoonacular

## 🔍 Situation Actuelle

### Widget 1 : "📝 Proposer Recettes"

**Appels API Spoonacular** :
- ✅ **1 appel** : `complex_search()` pour récupérer 9 recettes candidates
  - Paramètre `fillIngredients: "true"` → Les ingrédients sont déjà inclus dans la réponse
  - Les ingrédients sont stockés dans Notion (colonne "Ingredients" en texte brut)

**Coût** : **1 point API** (pour 9 recettes)

### Widget 2 : "🛒 Générer Courses"

**Appels API Spoonacular** :
- ❌ **3 appels** : `get_recipe_ingredients_with_quantities(spoon_id)` pour chaque recette sélectionnée
  - Un appel par recette sélectionnée (généralement 3 recettes)
  - Récupère les ingrédients avec quantités précises

**Coût** : **3 points API** (pour 3 recettes)

---

## 📈 Total par Workflow Complet

**Total** : **1 + 3 = 4 points API Spoonacular** par semaine

- Widget 1 : 1 point
- Widget 2 : 3 points (1 par recette sélectionnée)

---

## ⚠️ Problème : Duplication

**Oui, il y a une duplication** :

1. **Widget 1** : Les ingrédients sont déjà récupérés via `complex_search` avec `fillIngredients: "true"`
2. **Widget 2** : On refait des appels API pour récupérer les mêmes ingrédients

**Pourquoi cette duplication ?**

- Les ingrédients du Widget 1 sont stockés dans Notion en **format texte brut** (ex: "500g poulet, 2 cuillères à soupe d'huile")
- Le Widget 2 a besoin d'ingrédients en **format structuré** avec quantités précises (ex: `{"name": "chicken breast", "amount": 500, "unit": "g"}`)
- Le format texte ne permet pas de multiplier les quantités par le nombre de portions

---

## ✅ Solutions Possibles

### Solution 1 : Stocker les Ingrédients Structurés (Recommandé)

**Principe** : Stocker les ingrédients en format JSON dans Notion ou dans un fichier local lors du Widget 1, puis les lire lors du Widget 2.

**Avantages** :
- ✅ Économise 3 points API par semaine (75% de réduction)
- ✅ Plus rapide (pas d'appels API lors du Widget 2)
- ✅ Fonctionne même si Spoonacular est en panne

**Inconvénients** :
- ⚠️ Nécessite de modifier le code
- ⚠️ Les quantités sont fixes (pas de mise à jour si la recette change sur Spoonacular)

**Implémentation** :
1. Lors du Widget 1, sauvegarder les ingrédients structurés dans un fichier JSON local (`data/recipes_ingredients.json`)
2. Lors du Widget 2, lire les ingrédients depuis ce fichier au lieu de faire des appels API
3. Si le fichier n'existe pas ou si la recette n'est pas trouvée, fallback sur l'API

**Économie** : **3 points API par semaine** (de 4 à 1 point)

---

### Solution 2 : Stocker dans Notion (Plus Complexe)

**Principe** : Créer une colonne "Ingrédients JSON" dans Notion pour stocker les ingrédients structurés.

**Avantages** :
- ✅ Données centralisées dans Notion
- ✅ Accessibles depuis n'importe où

**Inconvénients** :
- ⚠️ Notion limite la taille des colonnes (pas idéal pour du JSON)
- ⚠️ Plus complexe à implémenter
- ⚠️ Nécessite de parser le JSON depuis Notion

---

### Solution 3 : Utiliser les Ingrédients du Widget 1 (Limité)

**Principe** : Parser le texte des ingrédients stockés dans Notion pour extraire les quantités.

**Avantages** :
- ✅ Pas de modification majeure du code
- ✅ Utilise les données déjà stockées

**Inconvénients** :
- ⚠️ Parsing de texte naturel = peu fiable
- ⚠️ Les quantités peuvent être imprécises
- ⚠️ Ne fonctionne pas pour toutes les recettes

---

## 💰 Impact Financier

### Avec la Solution Actuelle

**Par semaine** : 4 points API
**Par mois** (4 semaines) : 16 points API
**Par an** : 208 points API

**Avec un plan Spoonacular gratuit** (150 points/mois) :
- ✅ Suffisant pour ~9 semaines par mois
- ⚠️ Risque d'épuisement si vous utilisez d'autres fonctionnalités

### Avec la Solution 1 (Optimisée)

**Par semaine** : 1 point API
**Par mois** (4 semaines) : 4 points API
**Par an** : 52 points API

**Avec un plan Spoonacular gratuit** (150 points/mois) :
- ✅ Suffisant pour 37 semaines par mois
- ✅ Beaucoup plus de marge

---

## 🎯 Recommandation

**Je recommande la Solution 1** : Stocker les ingrédients structurés dans un fichier JSON local.

**Pourquoi ?**
- ✅ Économise 75% des points API
- ✅ Simple à implémenter
- ✅ Améliore les performances (pas d'attente API)
- ✅ Plus robuste (fonctionne même si Spoonacular est en panne)

**Implémentation** :
- Modifier `workflow_recipes.py` pour sauvegarder les ingrédients structurés
- Modifier `workflow_courses.py` pour lire depuis le fichier en priorité
- Fallback sur l'API si le fichier n'existe pas

---

## 📝 Résumé

| Métrique | Actuel | Optimisé (Solution 1) | Économie |
|----------|--------|----------------------|----------|
| **Points API/semaine** | 4 | 1 | **-75%** |
| **Points API/mois** | 16 | 4 | **-75%** |
| **Points API/an** | 208 | 52 | **-75%** |

**Conclusion** : Oui, la logique actuelle utilise **2 fois plus de tokens** (en fait 4 fois plus si on compte les 3 recettes sélectionnées). L'optimisation permettrait d'économiser **75% des points API**.

---

## ❓ Questions

**Q: Est-ce que je dois optimiser maintenant ?**
R: Si vous êtes sur le plan gratuit (150 points/mois), vous pouvez attendre. Si vous utilisez beaucoup d'autres fonctionnalités Spoonacular, l'optimisation est recommandée.

**Q: Les ingrédients peuvent-ils changer sur Spoonacular ?**
R: Oui, mais rarement. Les recettes sont généralement stables. Si vous voulez être sûr d'avoir les dernières données, vous pouvez garder un fallback sur l'API.

**Q: Comment implémenter la Solution 1 ?**
R: Je peux vous aider à modifier le code pour stocker et lire les ingrédients depuis un fichier JSON local.

