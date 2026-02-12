"""Utilitaires généraux pour le workflow."""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

import requests

from .config import NTFY_TOPIC


def week_label(d: date | None = None) -> str:
    """
    Retourne le label de semaine au format 'Semaine {iso_week} – {iso_year}'.
    
    Args:
        d: Date (défaut: aujourd'hui)
    
    Returns:
        Label de semaine, ex: "Semaine 46 – 2025"
    """
    if d is None:
        d = date.today()
    iso_year, iso_week, _ = d.isocalendar()
    return f"Semaine {iso_week} – {iso_year}"


def notify_ntfy(title: str, body: str, click_url: str | None = None) -> None:
    """
    Envoie une notification via ntfy.sh.
    
    Args:
        title: Titre de la notification
        body: Corps de la notification
        click_url: URL cliquable (optionnel). Si fourni, le header "Click" sera ajouté
                   pour rendre le lien cliquable dans la notification.
    """
    # Si pas de topic configuré, on ignore silencieusement
    if not NTFY_TOPIC or not NTFY_TOPIC.strip():
        print("⚠️ NTFY_TOPIC non configuré, notification ignorée")
        return
    
    try:
        # Les headers HTTP doivent être en latin-1, mais on peut utiliser UTF-8 pour le body
        # Pour le titre, on essaie de l'encoder en latin-1, sinon on utilise une version ASCII
        try:
            title_encoded = title.encode("latin-1", errors="replace").decode("latin-1")
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Si ça ne marche pas, on utilise une version ASCII
            title_encoded = title.encode("ascii", errors="replace").decode("ascii")
        
        headers = {
            "Title": title_encoded,
            "Content-Type": "text/plain; charset=utf-8",
        }
        
        # Ajouter le header Click si une URL est fournie (rend le lien cliquable)
        if click_url:
            try:
                click_encoded = click_url.encode("latin-1", errors="replace").decode("latin-1")
                headers["Click"] = click_encoded
            except (UnicodeEncodeError, UnicodeDecodeError):
                # Si l'URL contient des caractères non-latin-1, on l'encode en ASCII
                click_encoded = click_url.encode("ascii", errors="replace").decode("ascii")
                headers["Click"] = click_encoded
        
        # Support de l'authentification (optionnel)
        auth = None
        from .config import NTFY_USER, NTFY_PASS
        if NTFY_USER and NTFY_PASS:
            auth = (NTFY_USER, NTFY_PASS)
        
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC.strip()}",
            data=body.encode("utf-8"),
            headers=headers,
            auth=auth,
            timeout=5,
        )
        response.raise_for_status()  # Lève une exception si erreur HTTP
    except Exception as e:
        print(f"⚠️ Erreur notification ntfy: {e}")
        raise  # Re-lève l'exception pour le debug


def extract_spoon_id_from_url(url: str) -> Optional[int]:
    """
    Extrait l'ID Spoonacular depuis une URL.
    
    Supporte plusieurs formats :
    - URL Spoonacular : "https://spoonacular.com/recipes/123456"
    - URL image Spoonacular : "https://img.spoonacular.com/recipes-123456-312x231.jpg"
    - URL avec paramètre : "https://example.com/recipe?id=123456"
    
    Args:
        url: URL Spoonacular ou image Spoonacular
    
    Returns:
        ID Spoonacular ou None si non trouvé
    """
    if not url:
        return None
    
    # Pattern 1: /recipes/{id} (URL Spoonacular standard)
    match = re.search(r'/recipes/(\d+)', url)
    if match:
        return int(match.group(1))
    
    # Pattern 2: Image Spoonacular : recipes-{id}- ou recipes/{id}/
    # Ex: "https://img.spoonacular.com/recipes-123456-312x231.jpg"
    # Ex: "https://spoonacular.com/recipeImages/123456-312x231.jpg"
    match = re.search(r'recipes-(\d+)-', url)
    if match:
        return int(match.group(1))
    
    match = re.search(r'recipeImages/(\d+)-', url)
    if match:
        return int(match.group(1))
    
    match = re.search(r'/recipes/(\d+)/', url)
    if match:
        return int(match.group(1))
    
    # Pattern 3: Paramètre de requête ?id={id} ou &id={id}
    match = re.search(r'[?&]id=(\d+)', url)
    if match:
        return int(match.group(1))
    
    return None

