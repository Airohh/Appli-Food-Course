"""Export de la base Courses vers `courses.json`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from app.config import DATA_DIR, models_scorecard_db_id_2
from notion_tools.notion_reader import (
    export_database,
    get_client,
    get_database_properties,
    normalize_id,
    resolve_property_name,
    find_property_by_type,
)

OUTPUT_PATH = DATA_DIR / "courses.json"
COURSES_DB_ID = models_scorecard_db_id_2

def _to_number(value) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None

def fetch_courses() -> list[Dict]:
    normalized_id = normalize_id(COURSES_DB_ID)
    if not normalized_id:
        raise RuntimeError("Aucun identifiant de base Courses fourni.")

    client = get_client()
    schema = get_database_properties(client, normalized_id)

    name_key = resolve_property_name(client, normalized_id, ["Aliment", "Name", "Nom"])
    if not name_key:
        name_key = find_property_by_type(client, normalized_id, ["title"])
    if not name_key:
        available = ", ".join(f"{name} ({definition.get('type')})" for name, definition in schema.items())
        raise RuntimeError(
            "Impossible de trouver la colonne titre dans la base Courses. "
            f"Colonnes disponibles: {available}"
        )

    pages = export_database(client, normalized_id)
    items = []
    for page in pages:
        if not page:
            continue
        title = str(page.get(name_key) or "").strip()
        if not title:
            continue

        item = dict(page)
        for key, definition in schema.items():
            if definition.get("type") == "number" and key in item:
                item[key] = _to_number(item.get(key))

        item["__schema__"] = schema
        items.append(item)

    return items

def main() -> None:
    print("➡️  Lecture de la base Courses…")
    items = fetch_courses()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   ✅ {len(items)} élément(s) enregistré(s) dans {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
