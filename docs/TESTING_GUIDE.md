# Guide de Test Complet - Workflow Mobile Notion

## 🎯 Objectif

Tester le workflow complet de A à Z :
1. Proposer des recettes → Notion
2. Sélectionner des recettes dans Notion
3. Générer la liste de courses → Notion
4. Gérer le stock (transfert, soustraction)

## 📋 Prérequis

### 1. Configuration Notion

Vérifier que vous avez :
- ✅ 3 bases de données Notion configurées :
  - **Recettes** : avec colonnes `Name`, `Lien`, `Temps`, `Photo`, `Calories`, `Proteines`, `Ingredients`, `État` (ou `Terminée`), `Semaine`, `Portions` (optionnel), `Sélectionnée` (optionnel)
  - **Courses** : avec colonnes `Aliment`, `Quantité`, `Unité`, `Recettes`, `Statut`, `Semaine`, `Acheté` (optionnel)
  - **Stock** : avec colonnes `Aliment`, `Quantite` (ou `Quantité`), `Unité`, `Categorie` (ou `Catégorie`), `Expiration` (optionnel), `Place` (optionnel)

### 2. Variables d'environnement

Vérifier votre `.env` :
```bash
NOTION_TOKEN=secret_xxx
NOTION_API_KEY=secret_xxx
NOTION_RECIPES_DB=xxx
NOTION_GROCERIES_DB=xxx
NOTION_STOCK_DB=xxx
SPOONACULAR_API_KEY=xxx
NTFY_TOPIC=courses-ia
```

### 3. Tests unitaires

D'abord, vérifier que tous les tests passent :
```bash
cd Appli-Food-Course
pytest tests/ -v
```

## 🧪 Plan de Test Progressif

### Phase 1 : Tests en Mode Dry-Run (Sans Modifier Notion)

#### 1.1 Test de proposition de recettes (dry-run)

```bash
python -m app.workflow_recipes --dry-run --n-candidates 3 --n-final 2
```

**Vérifications :**
- ✅ Pas d'erreur
- ✅ Affiche le nombre de recettes candidates
- ✅ Affiche le nombre de recettes finales
- ✅ Ne modifie pas Notion (dry-run)

#### 1.2 Test de génération de courses (dry-run)

**Prérequis :** Avoir au moins 1 recette sélectionnée dans Notion pour la semaine actuelle

```bash
python -m app.workflow_courses --dry-run
```

**Vérifications :**
- ✅ Lit les recettes sélectionnées
- ✅ Récupère les ingrédients
- ✅ Affiche le nombre d'articles générés
- ✅ Ne modifie pas Notion (dry-run)

### Phase 2 : Tests Réels (Avec Notion)

#### 2.1 Préparation : Nettoyer les bases (Optionnel)

**⚠️ ATTENTION :** Ne supprimez pas les bases, archivez juste les entrées de la semaine actuelle.

**Option A : Nettoyage manuel dans Notion**
- Ouvrir la base Recettes
- Filtrer par Semaine = semaine actuelle
- Archiver/supprimer les entrées

**Option B : Utiliser le script (si vous voulez vraiment nettoyer)**
```python
# Script de nettoyage (à créer si besoin)
from app.workflow_recipes import archive_old_recipes
from app.utils import week_label

semaine = week_label()
archived = archive_old_recipes(semaine, dry_run=False)
print(f"Archivé {archived} recettes")
```

#### 2.2 Test 1 : Proposer des recettes

```bash
python -m app.workflow_recipes \
  --n-candidates 9 \
  --n-final 6 \
  --notion-url "https://notion.so/votre-vue-recettes"
```

**Vérifications dans Notion :**
- ✅ 6 nouvelles recettes créées
- ✅ Toutes ont `Semaine` = semaine actuelle (ex: "Semaine 46 – 2025")
- ✅ Toutes ont `Portions` = 1 (si colonne existe)
- ✅ Toutes ont `Sélectionnée` = false (si colonne existe)
- ✅ Toutes ont `Lien`, `Temps`, `Photo` remplis
- ✅ `Calories` et `Proteines` sont remplis (si colonnes existent)
- ✅ `Ingredients` est rempli (si colonne existe)
- ✅ Notification reçue sur ntfy.sh

**Vérifications locales :**
- ✅ Fichier `data/menu.json` créé avec 6 recettes

#### 2.3 Test 2 : Sélectionner des recettes dans Notion

**Action manuelle dans Notion :**
1. Ouvrir la base Recettes
2. Sélectionner 2-3 recettes (cocher `Sélectionnée` = true)
3. Ajuster les `Portions` si besoin (ex: 4 portions)

#### 2.4 Test 3 : Générer la liste de courses

```bash
python -m app.workflow_courses \
  --notion-url "https://notion.so/votre-vue-courses"
```

**Vérifications dans Notion :**
- ✅ Nouvelles lignes de courses créées
- ✅ Toutes ont `Semaine` = semaine actuelle (ex: "Semaine 46 – 2025")
- ✅ Toutes ont `Acheté` = false (si colonne existe)
- ✅ Toutes ont `Statut` = "Pas commencé" ou vide (selon votre configuration)
- ✅ `Aliment`, `Quantité`, `Unité` sont remplis
- ✅ `Recettes` contient les noms des recettes sources
- ✅ Quantités correctes (multipliées par portions)
- ✅ Anciennes courses de la semaine archivées
- ✅ Notification reçue sur ntfy.sh

**Vérifications locales :**
- ✅ Fichier `data/menu.json` mis à jour
- ✅ Fichier `data/groceries.json` créé
- ✅ Fichier `data/achats_filtres.json` créé

#### 2.5 Test 4 : Vérifier la soustraction du stock

**Prérequis :** Avoir des items en stock avec `Categorie` = "durable"

**Vérifications :**
- ✅ Les courses durables sont soustraites du stock
- ✅ Les courses frais ne sont pas soustraites
- ✅ Les quantités sont correctes

### Phase 3 : Tests Avancés

#### 3.1 Test : Transfert des courses achetées vers le stock

**Action manuelle dans Notion :**
1. Cocher `Acheté` = true pour quelques courses
2. Relancer le workflow de proposition de recettes (qui transfère automatiquement)

**Vérifications :**
- ✅ Les courses achetées apparaissent dans le Stock
- ✅ Les quantités sont correctes

#### 3.2 Test : Soustraction du stock quand recette terminée

**Action manuelle dans Notion :**
1. Changer `État` = "Terminée" (ou cocher `Terminée` = true si vous avez cette colonne) pour une recette
2. Exécuter :

```bash
python -m app.workflow_stock --recipe-id "page_id_de_la_recette"
```

**Vérifications :**
- ✅ Le stock est soustrait pour les ingrédients de la recette
- ✅ Seulement les durables sont soustraits
- ✅ Les quantités sont correctes

## 🔍 Checklist de Validation

### Fonctionnalités Core

- [ ] Proposition de recettes fonctionne
- [ ] Archivage des anciennes recettes fonctionne
- [ ] Transfert des courses achetées vers stock fonctionne
- [ ] Lecture des recettes sélectionnées fonctionne
- [ ] Génération de la liste de courses fonctionne
- [ ] Soustraction du stock (durable/frais) fonctionne
- [ ] Push vers Notion fonctionne
- [ ] Notifications ntfy.sh fonctionnent

### Données

- [ ] Les recettes ont tous les champs requis
- [ ] Les courses ont tous les champs requis
- [ ] Les quantités sont correctes (multiplication par portions)
- [ ] Les unités sont cohérentes
- [ ] Les labels de semaine sont corrects

### Fichiers JSON

- [ ] `data/menu.json` est créé/mis à jour
- [ ] `data/groceries.json` est créé
- [ ] `data/achats_filtres.json` est créé

## 🐛 Dépannage

### Erreur : "Base Recettes non configurée"
- Vérifier `NOTION_RECIPES_DB` dans `.env`
- Vérifier que l'ID est correct

### Erreur : "Clé API Notion manquante"
- Vérifier `NOTION_TOKEN` ou `NOTION_API_KEY` dans `.env`

### Erreur : "Aucune clé API Spoonacular"
- Vérifier `SPOONACULAR_API_KEY` dans `.env`

### Les recettes ne sont pas créées
- Vérifier les permissions de la base Notion
- Vérifier que le token a les bonnes permissions
- Vérifier les logs pour plus de détails

### Les courses ne sont pas générées
- Vérifier qu'il y a des recettes sélectionnées
- Vérifier que les recettes ont un `spoon_id` valide
- Vérifier que l'API Spoonacular fonctionne

## 📝 Logs

Les logs sont dans `data/logs/app.log` (si configuré) ou dans la console.

Pour plus de détails, exécuter avec `-v` :
```bash
python -m app.workflow_recipes -v
```

## ✅ Critères de Succès

Le projet est prêt si :
1. ✅ Tous les tests unitaires passent
2. ✅ Le workflow de proposition de recettes fonctionne
3. ✅ Le workflow de génération de courses fonctionne
4. ✅ Les données dans Notion sont correctes
5. ✅ Les notifications sont reçues
6. ✅ Les fichiers JSON sont générés

## 🚀 Prochaines Étapes

Une fois les tests validés :
1. Configurer les workflows GitHub Actions
2. Tester les workflows GitHub Actions
3. Documenter les vues Notion recommandées
4. Mettre en production

