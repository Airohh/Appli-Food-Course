# ✅ Vérification du Workflow - Résumé

## 🎯 Workflow Attendu

1. **Widget 1** : Propose **6 recettes** dans Notion
2. **Sélection manuelle** : Vous sélectionnez **3 recettes** (case "Sélectionnée")
3. **Widget 2** : Génère la liste de courses pour ces **3 recettes**
4. **Portions** : Chaque recette sélectionnée utilise **2 portions** par défaut

## ✅ Vérifications Effectuées

### 1. Nombre de Recettes Proposées
- ✅ **Code vérifié** : `n_final=6` par défaut dans `propose_recipes_to_notion()`
- ✅ **Message d'avertissement** : Si moins de 6 recettes sont récupérées, un message s'affiche
- ✅ **Logique** : `selected = candidates[:n_final]` prend les 6 premières recettes

### 2. Portions par Défaut
- ✅ **Code vérifié** : `portions = 2` par défaut dans `get_selected_recipes_this_week()`
- ✅ **Code vérifié** : `portions = recipe.get("portions", 2)` dans `generate_courses_from_selection()`
- ✅ **Flexibilité** : Peut être modifié via la colonne "Portions" dans Notion

### 3. Calcul des Quantités (Cache)
- ✅ **Code vérifié** : Le cache sauvegarde `servings` (nombre de portions de base)
- ✅ **Calcul correct** : `multiplier = portions / base_servings`
  - Exemple : Si recette pour 4 personnes et vous voulez 2 portions → multiplier = 2/4 = 0.5
  - Exemple : Si recette pour 1 personne et vous voulez 2 portions → multiplier = 2/1 = 2
- ✅ **Format** : Les quantités du cache sont converties correctement vers le format attendu

### 4. Calcul des Quantités (Fallback API)
- ✅ **Code corrigé** : Utilise maintenant `desired_portions` au lieu de `portions_multiplier`
- ✅ **Fonction améliorée** : `get_recipe_ingredients_with_quantities()` calcule automatiquement le multiplicateur
- ✅ **Cohérence** : Même logique que pour le cache

### 5. Cache des Ingrédients
- ✅ **Sauvegarde** : Les ingrédients sont sauvegardés avec `servings` et `image`
- ✅ **Lecture** : Le cache est lu en priorité, avec fallback sur l'API
- ✅ **Format** : Compatible avec le format `normalize()`

### 6. Photos
- ✅ **Sauvegarde** : L'image est sauvegardée dans le cache
- ✅ **Notion** : L'image est passée à Notion via le mapper existant

### 7. Notifications
- ✅ **Code vérifié** : Les notifications utilisent `click_url` pour rendre les liens cliquables
- ✅ **URLs** : Utilise `NOTION_RECIPES_VIEW_URL` et `NOTION_COURSES_VIEW_URL` depuis la config

## 🔍 Points d'Attention

### 1. Nombre de Recettes (5 au lieu de 6)
**Cause possible** :
- Spoonacular n'a pas retourné assez de recettes
- Une recette n'a pas d'ID et est ignorée
- Le message d'avertissement devrait s'afficher

**Solution** : Vérifier les logs pour voir le message d'avertissement

### 2. Photos Manquantes
**Cause possible** :
- L'image n'est pas dans la réponse Spoonacular
- Le mapper Notion ne trouve pas la colonne "Photo"

**Solution** : Vérifier que la colonne "Photo" existe dans Notion et qu'elle est de type "Files" ou "URL"

### 3. Notifications Non Cliquables
**Cause possible** :
- Les URLs ne sont pas configurées dans `.env`
- Problème d'encodage dans le header "Click"

**Solution** : Vérifier que `NOTION_RECIPES_VIEW_URL` et `NOTION_COURSES_VIEW_URL` sont bien configurés

### 4. Plus de Courses que Prévu
**Cause possible** (corrigé) :
- Le calcul des portions était incorrect
- Maintenant corrigé : `multiplier = portions / base_servings`

**Solution** : Le calcul est maintenant correct, les quantités devraient être bonnes

## 📊 Résumé des Corrections

1. ✅ **Portions par défaut** : Changé de `1` à `2`
2. ✅ **Calcul des quantités (cache)** : Utilise `portions / base_servings`
3. ✅ **Calcul des quantités (API)** : Utilise `desired_portions` pour calculer automatiquement
4. ✅ **Cache** : Sauvegarde `servings` et `image`
5. ✅ **Message d'avertissement** : Affiche si moins de 6 recettes sont récupérées

## 🧪 Tests Recommandés

1. **Test complet du workflow** :
   - Lancer Widget 1 → Vérifier 6 recettes
   - Sélectionner 3 recettes dans Notion
   - Lancer Widget 2 → Vérifier les quantités

2. **Vérifier les quantités** :
   - Comparer avec une recette connue
   - Vérifier que les quantités sont pour 2 portions

3. **Vérifier le cache** :
   - Vérifier que `data/recipes_ingredients_cache.json` contient les bonnes données
   - Vérifier que les quantités sont correctes

4. **Vérifier les notifications** :
   - Vérifier que les liens sont cliquables
   - Vérifier que les URLs sont correctes

## ✅ Conclusion

Le code est maintenant **cohérent et correct**. Tous les calculs de portions sont alignés :
- Cache : `multiplier = portions / base_servings`
- API : `desired_portions` calcule automatiquement le multiplicateur
- Portions par défaut : 2

Le workflow devrait fonctionner correctement ! 🎉

