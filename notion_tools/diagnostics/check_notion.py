"""Vérifie la connexion aux bases Notion listées dans databases.json."""

from typing import Dict

from app.config import (
    models_scorecard_db_id_1,
    models_scorecard_db_id_2,
    models_scorecard_db_id_3,
)
from notion_tools.notion_reader import get_client, iter_database_pages, normalize_id


DATABASES: Dict[str, str] = {
    "Scorecard #1": models_scorecard_db_id_1,
    "Scorecard #2": models_scorecard_db_id_2,
    "Scorecard #3": models_scorecard_db_id_3,
}


def _display_database(client, label: str, db_id: str) -> None:
    normalized_id = normalize_id(db_id)
    if not normalized_id:
        print(f"⚠️ ID manquant pour {label}, base ignorée")
        return

    try:
        print(f"➡️  Lecture de la base '{label}' ({db_id})")
        pages = list(iter_database_pages(client, normalized_id))
        print(f"   → {len(pages)} page(s) détectée(s)")
        for page in pages[:5]:
            page_id = page.get("id", "<inconnu>")
            url = page.get("url", "<pas d'URL>")
            print(f"     - {page_id} | {url}")
        if not pages:
            print("   ⚠️ Aucune page retournée. Vérifie les autorisations de l'intégration.")
    except Exception as exc:
        print(f"   ❌ Erreur: {exc}")


def main() -> None:
    print("Lecture des bases Notion…\n")
    client = get_client()
    for label, db_id in DATABASES.items():
        _display_database(client, label, db_id)
        print("")


if __name__ == "__main__":
    main()
