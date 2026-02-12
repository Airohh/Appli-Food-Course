# 🐛 Debug : Aucune Course dans Notion

## 🔍 Problème

Aucune course n'arrive dans la base de données Notion après avoir lancé le workflow GitHub Actions.

## ✅ Vérifications à Faire

### 1. Vérifier que le Code est Bien Poussé sur GitHub

**GitHub Actions utilise le code qui est commité sur GitHub, pas votre code local !**

1. **Vérifiez que vos changements sont commités** :
   ```bash
   git status
   ```
   - Si vous voyez des fichiers modifiés, ils ne sont pas encore commités

2. **Commitez et poussez vos changements** :
   ```bash
   git add .
   git commit -m "fix: amélioration logs et calcul portions"
   git push
   ```

3. **Vérifiez sur GitHub** :
   - Allez sur votre repository GitHub
   - Vérifiez que le dernier commit contient vos changements
   - Le workflow GitHub Actions utilisera ce commit

### 2. Vérifier les Logs du Workflow

Dans les logs GitHub Actions, cherchez ces messages :

#### ✅ Messages Normaux
- `"X recette(s) sélectionnée(s)"` → Des recettes sont trouvées
- `"Total : X ingrédient(s) récupéré(s)"` → Des ingrédients sont récupérés
- `"X article(s) agrégé(s)"` → Des articles sont créés
- `"X article(s) après filtrage"` → Des articles restent après filtrage
- `"X créé(s), X mis à jour"` → Des courses sont créées dans Notion

#### ⚠️ Messages d'Erreur
- `"Aucune recette sélectionnée"` → Aucune recette n'est sélectionnée dans Notion
- `"Pas d'ID Spoonacular"` → Les recettes n'ont pas d'ID Spoonacular
- `"Aucun ingrédient récupéré"` → Problème avec le cache ou l'API
- `"La liste de courses est vide"` → Aucun article après traitement
- `"Aucun article avec quantité > 0"` → Tout a été soustrait du stock

### 3. Vérifier dans Notion

1. **Vérifiez que des recettes sont sélectionnées** :
   - Ouvrez la base "Recettes" dans Notion
   - Vérifiez que la colonne "Sélectionnée" est cochée pour 3 recettes
   - Vérifiez que la colonne "Semaine" correspond à la semaine actuelle

2. **Vérifiez que les recettes ont un ID Spoonacular** :
   - Vérifiez que la colonne "Lien" contient une URL Spoonacular
   - Ou que la colonne "Photo" contient une image Spoonacular

### 4. Vérifier le Cache

Le cache est créé lors du Widget 1 (proposer recettes). Si vous n'avez pas lancé le Widget 1 récemment, le cache peut être vide.

**Solution** : Lancez d'abord le Widget 1 pour créer le cache, puis le Widget 2.

### 5. Vérifier les Secrets GitHub

Vérifiez que tous les secrets sont bien configurés dans GitHub :
- `NOTION_TOKEN` : Token Notion
- `NOTION_RECIPES_DB` : ID de la base Recettes
- `NOTION_GROCERIES_DB` : ID de la base Courses
- `NOTION_STOCK_DB` : ID de la base Stock
- `SPOONACULAR_API_KEY` : Clé API Spoonacular
- `SPOONACULAR_API_KEY2` : Clé API Spoonacular de secours (optionnel)

## 🔧 Actions Correctives

### Si Aucune Recette Sélectionnée

1. Ouvrez Notion
2. Cochez "Sélectionnée" pour 3 recettes
3. Vérifiez que "Semaine" correspond à la semaine actuelle
4. Relancez le workflow

### Si Pas d'ID Spoonacular

1. Vérifiez que les recettes ont un "Lien" vers Spoonacular
2. Si non, lancez d'abord le Widget 1 pour proposer de nouvelles recettes

### Si Cache Vide

1. Lancez d'abord le Widget 1 (proposer recettes)
2. Attendez qu'il se termine
3. Puis lancez le Widget 2 (générer courses)

### Si Tout est Soustrait du Stock

C'est normal ! Si tous les ingrédients sont déjà en stock, la liste de courses sera vide.

**Solution** : Vérifiez votre base Stock dans Notion.

## 📊 Logs de Debug Ajoutés

J'ai ajouté des logs de debug pour mieux comprendre ce qui se passe :

- `📦 Cache chargé : X recette(s) en cache`
- `📊 Total : X ingrédient(s) récupéré(s)`
- `📝 X article(s) après filtrage`
- `📋 X article(s) à synchroniser`
- `📊 Résultat : X créé(s), X mis à jour, X erreur(s)`

Ces logs vous aideront à identifier où le problème se situe.

## 🚀 Prochaines Étapes

1. **Commitez et poussez vos changements** sur GitHub
2. **Relancez le workflow** GitHub Actions
3. **Consultez les logs** pour voir où ça bloque
4. **Partagez les logs** si le problème persiste

