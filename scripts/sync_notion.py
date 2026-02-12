"""Exporte toutes les bases Notion vers un fichier JSON consolidé.

Usage : `python -m scripts.sync_notion` ou `python scripts/sync_notion.py`
Génère `data/notion_dump.json` avec toutes les bases exportées.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

# Ajouter le répertoire parent au PYTHONPATH pour permettre les imports
if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.config import (
    DATA_DIR,
    models_scorecard_db_id_1,
    models_scorecard_db_id_2,
    models_scorecard_db_id_3,
)
from notion_tools.notion_reader import export_database, get_client, normalize_id


DATABASES: Dict[str, str] = {
    "recipes": models_scorecard_db_id_1,
    "courses": models_scorecard_db_id_2,
    "stock": models_scorecard_db_id_3,
}


def main() -> None:
    output_path = DATA_DIR / "notion_dump.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    client = get_client()
    dump: Dict[str, list] = {}

    for label, db_id in DATABASES.items():
        normalized_id = normalize_id(db_id)
        if not normalized_id:
            print(f"[WARN] ID manquant pour {label}, base ignorée")
            continue

        try:
            print(f"[INFO] Export de '{label}'...")
            pages = export_database(client, normalized_id)
            dump[label] = pages
            print(f"   -> {len(pages)} entrée(s) exportée(s)")
        except Exception as exc:
            print(f"   [ERROR] Erreur lors de l'export de '{label}': {exc}")
            dump[label] = []

    output_path.write_text(
        json.dumps(dump, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Dump complet écrit dans {output_path}")


if __name__ == "__main__":
    main()

