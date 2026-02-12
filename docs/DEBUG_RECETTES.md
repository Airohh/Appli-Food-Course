# 🔍 Debug : Vérifier les Données des Recettes

## Problème

Les liens et calories ne sont pas sauvegardés dans Notion.

## Vérifications

### 1. Vérifier les données dans menu.json

```bash
cd Appli-Food-Course
python -c "import json; from pathlib import Path; data = json.loads((Path('data') / 'menu.json').read_text(encoding='utf-8')); print('Première recette:'); import json; print(json.dumps(data[0] if data else {}, indent=2, ensure_ascii=False))"
```

**Vérifiez que :**
- ✅ `sourceUrl` est présent
- ✅ `nutrition.calories` est présent et > 0

### 2. Vérifier le mapping

Le code cherche :
- **Lien** : `sourceUrl` dans la recette → colonne "Lien" (type URL) dans Notion
- **Calories** : `nutrition.calories` dans la recette → colonne "Calories" (type Number) dans Notion

### 3. Corrections apportées

1. **Lien** : Le code cherche maintenant d'abord par nom "Lien", puis par type en excluant "Photo"
2. **Calories** : Amélioration de l'extraction depuis `nutrition.calories`

## Test

Relancez la création de recettes :

```bash
python -m app.workflow_recipes --n-candidates 3 --n-final 2
```

Puis vérifiez dans Notion que les colonnes "Lien" et "Calories" sont bien remplies.

## Si ça ne fonctionne toujours pas

1. Vérifiez que les colonnes existent dans Notion :
   - "Lien" doit être de type **URL**
   - "Calories" doit être de type **Number**

2. Vérifiez les données dans `data/menu.json` :
   - Les recettes doivent avoir `sourceUrl` et `nutrition.calories`

3. Vérifiez les logs lors de la synchronisation :
   - Des erreurs peuvent apparaître si les colonnes n'existent pas

