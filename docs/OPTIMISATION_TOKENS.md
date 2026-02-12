# ✅ Optimisation des Tokens Spoonacular - Implémentée

## 🎯 Objectif

Réduire l'utilisation des tokens Spoonacular en évitant les appels API redondants lors de la génération des courses.

## 📊 Résultat

**Avant** : 4 points API par semaine (1 pour proposer + 3 pour générer)
**Après** : 1 point API par semaine (1 pour proposer, 0 pour générer grâce au cache)

**Économie** : **75% de réduction** (de 4 à 1 point API par semaine)

---

## 🔧 Implémentation

### 1. Cache des Ingrédients (`workflow_recipes.py`)

Lors de la proposition des recettes, les ingrédients structurés sont maintenant sauvegardés dans un fichier cache :

**Fichier** : `data/recipes_ingredients_cache.json`

**Format** :
```json
{
  "123456": {
    "title": "Nom de la recette",
    "ingredients": [
      {
        "name": "chicken breast",
        "amount": 500,
        "unit": "g"
      },
      ...
    ]
  },
  ...
}
```

**Clé** : ID Spoonacular de la recette (string)
**Valeur** : Titre + liste des ingrédients au format `normalize()`

### 2. Lecture depuis le Cache (`workflow_courses.py`)

Lors de la génération des courses, le système :

1. **Charge le cache** depuis `data/recipes_ingredients_cache.json`
2. **Pour chaque recette sélectionnée** :
   - Cherche les ingrédients dans le cache (par ID Spoonacular)
   - Si trouvé : utilise les ingrédients du cache et multiplie par les portions
   - Si non trouvé : fallback sur l'API Spoonacular (comme avant)
3. **Affiche** dans les logs si les ingrédients viennent du cache ou de l'API

---

## 📝 Format de Conversion

Les ingrédients du cache (format `normalize()`) sont convertis vers le format attendu par le reste du code :

**Format cache** :
```python
{
    "name": "chicken breast",
    "amount": 500,
    "unit": "g"
}
```

**Format converti** :
```python
{
    "raw_name": "chicken breast",
    "name": "chicken breast",
    "amount": 500 * portions,  # Multiplié par les portions
    "unit": "g",
    "aisle": "Divers",  # Valeur par défaut
    "recipe_id": 123456,
    "recipe_title": "Nom de la recette"
}
```

---

## 🔄 Comportement

### Scénario 1 : Recette dans le Cache (Cas Normal)

1. Widget 1 : Propose 6 recettes → Cache mis à jour
2. Widget 2 : Génère les courses pour 3 recettes sélectionnées
   - ✅ Les 3 recettes sont dans le cache
   - ✅ Aucun appel API Spoonacular
   - ✅ Log : `"✅ Recette: X ingrédient(s) (depuis le cache)"`

**Résultat** : 1 point API au total (Widget 1 uniquement)

### Scénario 2 : Recette Non Trouvée dans le Cache (Fallback)

1. Widget 2 : Génère les courses pour une recette qui n'est pas dans le cache
   - ⚠️ La recette n'est pas dans le cache (ancienne recette, cache supprimé, etc.)
   - ✅ Fallback automatique sur l'API Spoonacular
   - ✅ Log : `"✅ Recette: X ingrédient(s) (depuis l'API)"`

**Résultat** : Appel API normal (comme avant l'optimisation)

---

## 📁 Fichiers Modifiés

1. **`app/workflow_recipes.py`** :
   - Ajout de la sauvegarde du cache après récupération des recettes
   - Cache mis à jour pour chaque recette proposée

2. **`app/workflow_courses.py`** :
   - Ajout du chargement du cache au début
   - Lecture depuis le cache en priorité
   - Fallback sur l'API si non trouvé
   - Conversion du format cache vers le format attendu

3. **`.gitignore`** :
   - Ajout de `data/recipes_ingredients_cache.json` pour éviter de commiter le cache

---

## 🧪 Tests

Pour tester l'optimisation :

1. **Lancer le Widget 1** :
   ```bash
   python -m app.workflow_recipes
   ```
   - Vérifier que le cache est créé : `data/recipes_ingredients_cache.json`
   - Vérifier le message : `"✅ Cache mis à jour pour 6 recette(s)"`

2. **Lancer le Widget 2** :
   ```bash
   python -m app.workflow_courses
   ```
   - Vérifier les logs : `"(depuis le cache)"` au lieu de `"(depuis l'API)"`
   - Vérifier qu'aucun appel API n'est fait (surveiller les logs Spoonacular)

3. **Tester le fallback** :
   - Supprimer le cache : `rm data/recipes_ingredients_cache.json`
   - Relancer le Widget 2
   - Vérifier que les appels API sont faits normalement

---

## ⚠️ Notes Importantes

1. **Le cache est persistant** : Il reste entre les exécutions et s'accumule au fil du temps
2. **Pas de nettoyage automatique** : Les anciennes recettes restent dans le cache
3. **Fallback automatique** : Si le cache est manquant ou corrompu, l'API est utilisée
4. **Format compatible** : Le cache utilise le même format que `normalize()`, donc compatible avec le code existant

---

## 🚀 Prochaines Améliorations Possibles

1. **Nettoyage automatique** : Supprimer les recettes du cache qui ne sont plus utilisées
2. **Expiration** : Ajouter une date d'expiration aux entrées du cache
3. **Compression** : Compresser le cache si il devient trop volumineux
4. **Synchronisation** : Synchroniser le cache avec Notion pour partage entre machines

---

## ✅ Résumé

L'optimisation est **implémentée et fonctionnelle**. Elle permet d'économiser **75% des tokens Spoonacular** en réutilisant les ingrédients déjà récupérés lors de la proposition des recettes.

**Impact** :
- ✅ **Économie** : 3 points API par semaine (de 4 à 1)
- ✅ **Performance** : Plus rapide (pas d'attente API lors du Widget 2)
- ✅ **Robustesse** : Fallback automatique si le cache est manquant
- ✅ **Transparence** : Logs clairs indiquant la source des données

