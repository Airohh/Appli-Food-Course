"""Exporte les bases Notion en fichiers JSON (format simplifié)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from app.config import (
    DATA_DIR,
    models_scorecard_db_id_1,
    models_scorecard_db_id_2,
    models_scorecard_db_id_3,
)
from notion_tools.notion_reader import export_database, get_client, normalize_id, slugify


DATABASES: Dict[str, str] = {
    "Scorecard #1": models_scorecard_db_id_1,
    "Scorecard #2": models_scorecard_db_id_2,
    "Scorecard #3": models_scorecard_db_id_3,
}


def main(output_dir: Path = DATA_DIR / "exports") -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    client = get_client()

    for label, db_id in DATABASES.items():
        normalized_id = normalize_id(db_id)
        if not normalized_id:
            print(f"⚠️ ID manquant pour {label}, base ignorée")
            continue

        try:
            print(f"➡️  Export de '{label}' vers JSON…")
            pages = export_database(client, normalized_id)
            filename = output_dir / f"{slugify(label)}.json"
            filename.write_text(
                json.dumps(pages, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"   ✅ {len(pages)} entrée(s) écrite(s) dans {filename}")
        except Exception as exc:
            print(f"   ❌ Erreur lors de l'export : {exc}")


if __name__ == "__main__":
    main()

