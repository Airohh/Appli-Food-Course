# ✅ Checklist de Démarrage

## État Actuel du Projet

### ✅ Code
- ✅ Tous les tests unitaires passent
- ✅ Workflows GitHub Actions configurés
- ✅ Support des topics ntfy.sh sécurisés
- ✅ Gestion flexible des schémas Notion (Photo URL/Files, Semaine Select/Multi-select)
- ✅ Documentation complète

### ⚠️ À Vérifier

#### 1. Configuration Notion
- [ ] Les 3 bases de données existent : **Recettes**, **Courses**, **Stock**
- [ ] Les colonnes requises sont présentes (voir `docs/SCHEMA_NOTION.md`)
- [ ] L'intégration Notion a accès aux 3 bases

#### 2. Secrets GitHub
- [ ] `NOTION_TOKEN` configuré
- [ ] `NOTION_RECIPES_DB` configuré (ID de la base Recettes)
- [ ] `NOTION_GROCERIES_DB` configuré (ID de la base Courses)
- [ ] `NOTION_STOCK_DB` configuré (ID de la base Stock)
- [ ] `SPOONACULAR_API_KEY` configuré
- [ ] `NTFY_TOPIC` configuré (optionnel, pour les notifications)

#### 3. Bases de Données Notion

**Si vous avez des données de test à nettoyer :**

Voir le guide détaillé : `docs/NETTOYAGE_DONNEES_TEST.md`

**Résumé rapide :**
1. **Base Recettes** : Supprimez toutes les pages (gardez les colonnes)
2. **Base Courses** : Supprimez toutes les pages (gardez les colonnes)
3. **Base Stock** : 
   - Option A : Videz complètement (repartir à zéro)
   - Option B : Gardez quelques items de test avec catégorie "durable" ou "frais" pour tester la soustraction

**Important :**
- ⚠️ **Ne supprimez PAS les bases elles-mêmes**, seulement les pages
- ⚠️ **Ne supprimez PAS les colonnes**, gardez la structure
- Si vous supprimez accidentellement une colonne, recréez-la avec le même nom et type

## 🚀 Première Utilisation

### 1. Test en mode dry-run (sans modifier Notion)

```bash
cd Appli-Food-Course

# Test proposition de recettes
python -m app.workflow_recipes --dry-run --n-candidates 3 --n-final 2

# Test génération de courses (nécessite des recettes sélectionnées)
python -m app.workflow_courses --dry-run
```

### 2. Utilisation réelle

**Étape 1 : Proposer des recettes**
```bash
python -m app.workflow_recipes --n-candidates 6 --n-final 3
```

**Étape 2 : Dans Notion**
- Ouvrez la base Recettes
- Cochez 3 recettes (colonne "Sélectionnée")
- Ajustez les portions si nécessaire

**Étape 3 : Générer la liste de courses**
```bash
python -m app.workflow_courses
```

## 📝 Recommandation

**Je recommande de GARDER vos données existantes** car :
1. Le code gère automatiquement l'archivage
2. Vous gardez votre historique
3. Le stock existant sera utilisé pour la soustraction
4. Les anciennes courses seront automatiquement archivées avant d'en créer de nouvelles

**Si vous voulez vraiment nettoyer :**
- Nettoyez seulement les recettes et courses des semaines précédentes
- **Gardez le stock** pour que la soustraction automatique fonctionne

## ❓ Questions Fréquentes

**Q: Dois-je supprimer toutes mes bases de données ?**
R: Non ! Gardez-les. Le code gère automatiquement l'archivage et la mise à jour.

**Q: Que se passe-t-il avec les anciennes recettes ?**
R: Elles sont automatiquement archivées (colonne "Semaine" mise à jour ou recettes déplacées) quand vous lancez `workflow_recipes`.

**Q: Que se passe-t-il avec les anciennes courses ?**
R: Elles sont automatiquement archivées (supprimées ou marquées) avant de créer les nouvelles pour la semaine actuelle.

**Q: Dois-je vider mon stock ?**
R: Non ! Gardez votre stock. Il sera utilisé automatiquement pour soustraire les quantités lors de la génération des courses.

