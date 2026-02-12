# 🔗 Comment Obtenir les URLs des Vues Notion

Pour que les notifications contiennent des liens cliquables vers vos vues Notion, vous devez obtenir les URLs de vos vues.

## 📋 Étape 1 : Obtenir l'URL de la Vue Recettes

1. **Ouvrez votre base "Recettes" dans Notion**
2. **Créez ou sélectionnez une vue** (ex: "Galerie mobile", "Table", etc.)
   - Si vous n'avez pas de vue, créez-en une en cliquant sur "Add a view" en haut
3. **Cliquez sur "Share"** (Partager) en haut à droite de la page
4. **Cliquez sur "Copy link"** (Copier le lien)
5. **Copiez l'URL complète**

**Exemple d'URL :**
```
https://www.notion.so/your-workspace/Recettes-abc123def456?view=xyz789
```

## 📋 Étape 2 : Obtenir l'URL de la Vue Courses

1. **Ouvrez votre base "Courses" dans Notion**
2. **Créez ou sélectionnez une vue** (ex: "A acheter", "Mobile", etc.)
3. **Cliquez sur "Share"** (Partager) en haut à droite
4. **Cliquez sur "Copy link"** (Copier le lien)
5. **Copiez l'URL complète**

**Exemple d'URL :**
```
https://www.notion.so/your-workspace/Courses-abc123def456?view=xyz789
```

## 📋 Étape 3 : Ajouter les URLs dans `.env`

Ouvrez le fichier `.env` dans `Appli-Food-Course/` et ajoutez :

```bash
# URLs Notion (pour les notifications avec liens cliquables)
NOTION_RECIPES_VIEW_URL=https://www.notion.so/your-workspace/Recettes-abc123def456?view=xyz789
NOTION_COURSES_VIEW_URL=https://www.notion.so/your-workspace/Courses-abc123def456?view=xyz789
```

**Exemple de `.env` complet :**
```bash
# Notion
NOTION_TOKEN=secret_xxx
NOTION_API_KEY=secret_xxx
NOTION_RECIPES_DB=xxx
NOTION_GROCERIES_DB=xxx
NOTION_STOCK_DB=xxx

# Spoonacular
SPOONACULAR_API_KEY=xxx
SPOONACULAR_API_KEY2=yyy

# Notifications
NTFY_TOPIC=v8-vK551qEV_Fj4mjgYIAA

# URLs Notion (pour les notifications avec liens cliquables)
NOTION_RECIPES_VIEW_URL=https://www.notion.so/your-workspace/Recettes-abc123def456?view=xyz789
NOTION_COURSES_VIEW_URL=https://www.notion.so/your-workspace/Courses-abc123def456?view=xyz789
```

## ✅ Résultat

Une fois configuré, les notifications contiendront des liens cliquables :

- **Notification "Recettes prêtes"** → Cliquez pour ouvrir la vue Recettes
- **Notification "Liste prête"** → Cliquez pour ouvrir la vue Courses

## 🔄 Alternative : Passer l'URL en paramètre

Si vous préférez ne pas stocker les URLs dans `.env`, vous pouvez les passer en paramètre :

```bash
# Recettes
python -m app.workflow_recipes --n-candidates 6 --n-final 3 --notion-url "https://notion.so/votre-vue-recettes"

# Courses
python -m app.workflow_courses --notion-url "https://notion.so/votre-vue-courses"
```

L'URL passée en paramètre a la priorité sur celle dans `.env`.

## ❓ Dépannage

### L'URL ne fonctionne pas

1. ✅ Vérifiez que l'URL est complète (commence par `https://`)
2. ✅ Vérifiez que la vue est partagée (Share → Copy link)
3. ✅ Testez l'URL dans un navigateur pour vérifier qu'elle fonctionne

### Je ne vois pas le lien cliquable dans la notification

1. ✅ Vérifiez que vous avez bien ajouté l'URL dans `.env` ou passé `--notion-url`
2. ✅ Vérifiez que l'app ntfy.sh est à jour
3. ✅ Sur Android, le lien devrait être cliquable directement dans la notification
4. ✅ Sur iOS, vous devrez peut-être appuyer longuement sur la notification

