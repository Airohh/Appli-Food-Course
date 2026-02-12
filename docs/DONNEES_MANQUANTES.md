# ⚠️ Données Manquantes dans les Recettes

## Problème

Parfois, certaines recettes n'ont pas de **Lien** ou de **Calories** dans Notion.

## Causes Possibles

### 1. API Spoonacular

L'API Spoonacular ne retourne pas toujours toutes les données pour toutes les recettes :
- Certaines recettes n'ont pas de `sourceUrl` (lien vers le site source)
- Certaines recettes n'ont pas de données nutritionnelles complètes

### 2. Solutions Implémentées

#### Pour le Lien

Si `sourceUrl` est manquant mais qu'on a un ID Spoonacular, le code construit automatiquement l'URL :
```
https://spoonacular.com/recipes/{id}
```

Cela garantit qu'il y a toujours un lien vers la recette sur Spoonacular.

#### Pour les Calories

Les calories sont extraites depuis `nutrition.nutrients` dans la réponse API. Si elles sont manquantes :
- Le champ reste vide dans Notion (c'est normal)
- Vous pouvez les remplir manuellement si nécessaire

## Vérification

Pour vérifier quelles données sont disponibles :

1. **Vérifier dans `data/menu.json`** :
```bash
python -c "import json; from pathlib import Path; data = json.loads(Path('data/menu.json').read_text(encoding='utf-8')); [print(f'{r.get(\"title\")}: sourceUrl={r.get(\"sourceUrl\", \"MANQUANT\")}, calories={r.get(\"nutrition\", {}).get(\"calories\", \"MANQUANT\")}') for r in data]"
```

2. **Vérifier dans Notion** :
- Ouvrez la base Recettes
- Vérifiez les colonnes "Lien" et "Calories"

## Améliorations Futures

Si vous voulez toujours avoir des données complètes, vous pouvez :

1. **Filtrer les recettes** : Ne garder que celles qui ont toutes les données
2. **Remplir manuellement** : Ajouter les données manquantes dans Notion
3. **Utiliser une autre source** : Compléter avec une autre API ou base de données

## C'est Normal ?

**Oui, c'est normal** que certaines recettes n'aient pas toutes les données. L'API Spoonacular dépend de sources externes qui ne sont pas toujours complètes.

Le code fait maintenant de son mieux pour :
- ✅ Construire un lien Spoonacular si `sourceUrl` est manquant
- ✅ Extraire les calories si disponibles
- ✅ Laisser les champs vides si les données ne sont vraiment pas disponibles

