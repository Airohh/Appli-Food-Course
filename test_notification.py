#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de test pour les notifications ntfy.sh"""

import sys
import os
from pathlib import Path

# Forcer UTF-8 pour la console Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils import notify_ntfy
from app.config import NTFY_TOPIC

def main():
    print("Test des notifications ntfy.sh")
    print("=" * 50)
    
    # Vérifier la configuration
    if not NTFY_TOPIC or not NTFY_TOPIC.strip():
        print("[ERREUR] NTFY_TOPIC n'est pas configuré dans .env")
        print("   Ajoutez : NTFY_TOPIC=v8-vK551qEV_Fj4mjgYIAA")
        return 1
    
    print(f"[OK] Topic configuré : {NTFY_TOPIC}")
    print()
    
    # Test avec requests directement pour voir la réponse
    import requests
    url = f"https://ntfy.sh/{NTFY_TOPIC.strip()}"
    print(f"URL de test : {url}")
    print()
    print("Envoi de la notification...")
    
    try:
        response = requests.post(
            url,
            data="Test direct - Si vous recevez ce message, les notifications fonctionnent !".encode("utf-8"),
            headers={
                "Title": "Test Notification",
                "Content-Type": "text/plain; charset=utf-8",
            },
            timeout=10,
        )
        print(f"[OK] Statut HTTP : {response.status_code}")
        print(f"[OK] Réponse : {response.text[:100] if response.text else '(vide)'}")
        print()
        
        # Test aussi avec la fonction notify_ntfy
        print("Test avec la fonction notify_ntfy()...")
        notify_ntfy("Test", "Si vous recevez ce message, les notifications fonctionnent !")
        print("[OK] Notification envoyée avec succès")
        print()
        print("=" * 50)
        print("VERIFICATIONS IMPORTANTES :")
        print("=" * 50)
        print("1. Ouvrez l'app ntfy.sh sur votre telephone")
        print(f"2. Abonnez-vous au topic : {NTFY_TOPIC}")
        print("   (Bouton + ou 'Subscribe to topic')")
        print("3. Verifiez que le topic apparaît dans votre liste")
        print("4. Verifiez que l'app a les permissions de notification")
        print("5. Attendez quelques secondes (les notifications peuvent prendre du temps)")
        print()
        print("Si vous n'etes toujours pas abonne, voici comment faire :")
        print("- Ouvrez l'app ntfy.sh")
        print("- Cliquez sur le bouton + (ou 'Subscribe')")
        print(f"- Entrez le topic : {NTFY_TOPIC}")
        print("- Cliquez sur 'Subscribe'")
        return 0
    except requests.exceptions.RequestException as e:
        print(f"[ERREUR] Problème de connexion : {e}")
        print()
        print("Causes possibles :")
        print("- Problème de connexion Internet")
        print("- Firewall bloque les requêtes vers ntfy.sh")
        print("- Serveur ntfy.sh temporairement indisponible")
        return 1
    except Exception as e:
        print(f"[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

