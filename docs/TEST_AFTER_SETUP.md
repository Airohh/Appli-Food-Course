# Guide : Tester après configuration des secrets

Tu as configuré tous les secrets GitHub ! Maintenant, testons que tout fonctionne.

## ✅ Checklist de configuration

Vérifie que tu as bien configuré :

- [x] `NOTION_TOKEN` ✅
- [x] `NOTION_RECIPES_DB` ✅
- [x] `NOTION_GROCERIES_DB` ✅
- [x] `NOTION_STOCK_DB` ✅
- [x] `NOTION_MEALPLAN_DB` ✅
- [x] `NOTION_SYNC_ENABLED` ✅
- [x] `OPENAI_API_KEY` ✅
- [x] `SPOONACULAR_API_KEY` ✅
- [x] `SPOONACULAR_API_KEY2` ✅

## 🧪 Test 1 : Vérifier les secrets (optionnel)

Tu peux vérifier que les secrets sont bien configurés en regardant dans GitHub :
- Repo → Settings → Secrets and variables → Actions
- Tu devrais voir tous les secrets listés

## 🧪 Test 2 : Tester le workflow GitHub Actions

### Méthode 1 : Via l'interface GitHub

1. Va sur ton repo → **"Actions"**
2. Sélectionne **"Run Pipeline (Production)"**
3. Clique sur **"Run workflow"**
4. **Important** : Coche **"Synchroniser vers Notion"** si tu veux tester la sync
5. Clique sur **"Run workflow"**
6. Suis l'exécution dans les logs

### Ce qui devrait se passer

1. ✅ Le workflow se lance
2. ✅ Il installe les dépendances
3. ✅ Il rafraîchit le stock depuis Notion
4. ✅ Il lance le pipeline (Spoonacular → LLM → Consolidation)
5. ✅ Il génère `menu.json` et `achats_filtres.json`
6. ✅ Si `NOTION_SYNC_ENABLED=true` ou si tu as coché la case :
   - Il synchronise les recettes vers Notion
   - Il crée le plan de repas dans Notion
   - Il synchronise la liste de courses vers Notion
7. ✅ Il commit et push les fichiers JSON

### Vérifier les résultats

1. **Dans GitHub** :
   - Va dans le dossier `data/`
   - Vérifie que `menu.json` et `achats_filtres.json` sont à jour

2. **Dans Notion** :
   - Ouvre ta base **Recettes** → Vérifie que les nouvelles recettes sont là
   - Ouvre ta base **Meal Plan** → Vérifie que le plan de repas est créé
   - Ouvre ta base **Courses** → Vérifie que la liste de courses est synchronisée

## 🧪 Test 3 : Tester en local (optionnel)

Si tu veux tester en local avant de push sur GitHub :

1. Crée un fichier `.env` à la racine :
   ```bash
   NOTION_TOKEN=ton_token_ici
   NOTION_API_KEY=ton_token_ici
   NOTION_RECIPES_DB=2a29b6ccc7e480eab4ede002ce3b2984
   NOTION_GROCERIES_DB=2a29b6ccc7e48080b7e7ec94e052e98f
   NOTION_STOCK_DB=2a29b6ccc7e480949befe46134ebf834
   NOTION_MEALPLAN_DB=2a49b6ccc7e481a280e9f239131b1472
   NOTION_SYNC_ENABLED=true
   OPENAI_API_KEY=sk-ton_token_ici
   SPOONACULAR_API_KEY=ton_token_ici
   SPOONACULAR_API_KEY2=ton_token_2_ici
   ```

2. Teste en dry-run d'abord :
   ```bash
   # Test sans rien modifier
   python -m integrations.notion.recipes --dry-run
   python -m integrations.notion.mealplan --dry-run
   python -m integrations.notion.groceries --dry-run
   ```

3. Si tout est OK, teste pour de vrai :
   ```bash
   python -m app.main --mode prod
   ```

## 🆘 Dépannage

### Erreur : "NOTION_TOKEN manquant"

**Solution** : Vérifie que le secret `NOTION_TOKEN` est bien configuré dans GitHub Secrets.

### Erreur : "Permission denied" sur Notion

**Solution** : 
1. Va sur chaque base Notion
2. Clique sur "..." → "Connections"
3. Vérifie que ton intégration "Appli Food Course" est listée
4. Si elle n'y est pas, ajoute-la

### Erreur : "Invalid database ID"

**Solution** : 
1. Vérifie que les IDs font bien 32 caractères
2. Vérifie qu'il n'y a pas d'espaces avant/après
3. Utilise l'outil de diagnostic : `python -m notion_tools.diagnostics.check_notion`

### Le workflow échoue sur la sync Notion

**Solution** :
1. Vérifie les logs du workflow pour voir l'erreur exacte
2. Vérifie que `NOTION_SYNC_ENABLED=true` dans les secrets
3. Vérifie que toutes les bases sont partagées avec l'intégration

## ✅ Prochaines étapes

Une fois que tout fonctionne :

1. **Utilise le workflow régulièrement** :
   - Lance-le via GitHub Actions quand tu veux générer un nouveau menu
   - Ou configure un raccourci mobile (voir README.md)

2. **Vérifie les résultats dans Notion** :
   - Le plan de repas devrait être créé automatiquement
   - Les recettes devraient être synchronisées
   - La liste de courses devrait être à jour

3. **Personnalise si besoin** :
   - Modifie les paramètres dans `app/config.py` (nombre de recettes, calories, etc.)
   - Ajuste les schémas Notion si nécessaire

## 🎉 C'est prêt !

Ton intégration Notion est maintenant complètement configurée et prête à l'emploi !

