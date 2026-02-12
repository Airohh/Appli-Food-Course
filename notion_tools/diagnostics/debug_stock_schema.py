"""Affiche le schéma détaillé de la base Stock dans Notion."""

from __future__ import annotations

from pprint import pprint

from app.config import models_scorecard_db_id_3
from notion_tools.notion_reader import get_client, get_database_properties, normalize_id


def main() -> None:
    db_id = normalize_id(models_scorecard_db_id_3)
    if not db_id:
        raise RuntimeError("Aucun identifiant de base Stock défini.")

    client = get_client()
    schema = get_database_properties(client, db_id)

    print(f"Schéma de la base Stock ({db_id}):\n")
    for name, definition in schema.items():
        print(f"- {name} (type: {definition.get('type')})")
        details = {k: v for k, v in definition.items() if k != "type" and k != "id"}
        if details:
            pprint(details)
        print()


if __name__ == "__main__":
    main()

