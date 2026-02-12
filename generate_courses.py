#!/usr/bin/env python3
"""
Script simple pour générer la liste de courses depuis les recettes sélectionnées dans Notion.

Ce script peut être lancé directement ou via un bouton Notion.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from app.workflow_courses import generate_courses_from_selection
from app.config import NOTION_COURSES_VIEW_URL


def main():
    """Génère la liste de courses depuis les recettes sélectionnées."""
    print("🛒 Génération de la liste de courses...")
    print("=" * 50)
    
    try:
        result = generate_courses_from_selection(
            dry_run=False,
            notion_courses_url=NOTION_COURSES_VIEW_URL,
        )
        
        print("\n" + "=" * 50)
        print("✅ Liste de courses générée avec succès !")
        print(f"   - {result.get('n_selected', 0)} recette(s) sélectionnée(s)")
        print(f"   - {result.get('n_items', 0)} article(s) dans la liste")
        print(f"   - {result.get('n_subtracted', 0)} article(s) soustrait(s) du stock")
        
        return 0
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

