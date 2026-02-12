# 🐛 Problème : Recettes Sans Lien dans Notion

## 🔍 Diagnostic

Les recettes dans Notion n'ont pas de champ "Lien" rempli, ce qui empêche de récupérer l'ID Spoonacular.

## ✅ Solutions

### Solution 1 : Relancer le Widget 1 (Recommandé)

Le Widget 1 devrait remplir automatiquement le champ "Lien" avec l'URL Spoonacular.

**Actions** :
1. Lancez le Widget 1 (Proposer Recettes)
2. Vérifiez que les nouvelles recettes ont un champ "Lien" rempli
3. Sélectionnez ces nouvelles recettes
4. Lancez le Widget 2

### Solution 2 : Vérifier le Schéma Notion

Vérifiez que la colonne "Lien" existe dans votre base Notion "Recettes" :
- Type : **URL**
- Nom : **"Lien"** (exactement)

### Solution 3 : Fallback par Nom (Déjà Implémenté)

J'ai ajouté un fallback qui cherche l'ID dans le cache par nom de recette. Mais cela ne fonctionne que si :
- Le cache contient les recettes (Widget 1 lancé)
- Le nom de la recette correspond exactement

## 🔧 Code Ajouté

Le code cherche maintenant l'ID dans le cache par nom si le champ "Lien" est vide :

```python
# Fallback : si pas d'ID, chercher dans le cache par nom
if not spoon_id and recipe_name:
    recipe_name_lower = recipe_name.lower().strip()
    if recipe_name_lower in cache_by_name:
        cached_id, _ = cache_by_name[recipe_name_lower]
        spoon_id = int(cached_id)
```

## 📋 Checklist

- [ ] Le Widget 1 a été lancé récemment
- [ ] Le cache contient des recettes (vérifier les logs)
- [ ] La colonne "Lien" existe dans Notion
- [ ] Les recettes ont un champ "Lien" rempli
- [ ] Le nom des recettes correspond exactement entre Notion et le cache

## 🚀 Prochaines Étapes

1. **Lancez le Widget 1** pour créer de nouvelles recettes avec le champ "Lien" rempli
2. **Sélectionnez ces nouvelles recettes** dans Notion
3. **Lancez le Widget 2** pour générer les courses

