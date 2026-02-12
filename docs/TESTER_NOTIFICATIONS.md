# 🧪 Tester les Notifications

## Méthode 1 : Script de Test (Recommandé)

```bash
cd Appli-Food-Course
python test_notification.py
```

Ce script :
- ✅ Vérifie que `NTFY_TOPIC` est configuré
- ✅ Envoie une notification de test
- ✅ Affiche des messages clairs

## Méthode 2 : Commande Python Directe

```bash
cd Appli-Food-Course
python -m app.utils
```

Ou depuis le répertoire parent :
```bash
cd Appli-Food-Course
python -c "import sys; sys.path.insert(0, '.'); from app.utils import notify_ntfy; notify_ntfy('Test', 'Notifications OK !')"
```

## Méthode 3 : Via le Workflow

```bash
cd Appli-Food-Course
python -m app.workflow_recipes --n-candidates 3 --n-final 2
```

Cela enverra automatiquement une notification si `NTFY_TOPIC` est configuré.

## Vérifications

### 1. Vérifier que NTFY_TOPIC est dans .env

```bash
# Windows PowerShell
Get-Content Appli-Food-Course\.env | Select-String "NTFY_TOPIC"

# Linux/Mac
grep NTFY_TOPIC Appli-Food-Course/.env
```

### 2. Vérifier la valeur

Le topic doit être : `v8-vK551qEV_Fj4mjgYIAA`

### 3. Vérifier que vous êtes abonné

- Ouvrez l'app ntfy.sh sur votre téléphone
- Vérifiez que le topic `v8-vK551qEV_Fj4mjgYIAA` apparaît dans la liste

## Dépannage

### "NTFY_TOPIC non configuré"

**Solution :** Ajoutez dans `.env` :
```bash
NTFY_TOPIC=v8-vK551qEV_Fj4mjgYIAA
```

### "Erreur notification ntfy: ..."

**Causes possibles :**
- Problème de connexion Internet
- Topic invalide
- Serveur ntfy.sh temporairement indisponible

**Solution :** Réessayez après quelques secondes

### Je ne reçois pas la notification

1. ✅ Vérifiez que vous êtes abonné au topic dans l'app
2. ✅ Vérifiez que l'app ntfy.sh a les permissions de notification
3. ✅ Vérifiez que votre téléphone est connecté à Internet
4. ✅ Testez avec le script `test_notification.py` pour voir les erreurs

## Test Manuel via cURL

Vous pouvez aussi tester directement avec cURL :

```bash
curl -d "Test message" -H "Title: Test" https://ntfy.sh/v8-vK551qEV_Fj4mjgYIAA
```

Si ça fonctionne avec cURL mais pas avec Python, c'est un problème de configuration Python.


