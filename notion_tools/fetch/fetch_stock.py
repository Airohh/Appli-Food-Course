"""Export du stock Notion vers un fichier JSON.

Usage : `python fetch_stock.py`
Le fichier `stock.json` sert de snapshot complet, incluant toutes les
propriétés connues et le schéma de la base pour faciliter la
resynchronisation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from app.config import DATA_DIR, models_scorecard_db_id_3
from notion_tools.notion_reader import (
    export_database,
    get_client,
    get_database_properties,
    normalize_id,
    resolve_property_name,
    find_property_by_type,
)


OUTPUT_PATH = DATA_DIR / "stock.json"
STOCK_DB_ID = models_scorecard_db_id_3


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


def _page_to_stock_item(
    page: Dict,
    name_key: str,
    quantity_key: str | None,
    unit_key: str | None,
) -> Dict:
    aliment = str(page.get(name_key) or "").strip()
    quantite_raw = page.get(quantity_key) if quantity_key else ""
    unite = str(page.get(unit_key) or "").strip() if unit_key else ""

    quantite = _to_number(quantite_raw)

    item: Dict[str, object] = {
        "Aliment": aliment,
        "Quantité": quantite if quantite is not None else "",
        "Unité": unite,
    }

    return item


def fetch_stock() -> List[Dict]:
    normalized_id = normalize_id(STOCK_DB_ID)
    if not normalized_id:
        raise RuntimeError("Aucun identifiant de base Stock fourni.")

    client = get_client()
    schema = get_database_properties(client, normalized_id)

    name_key = resolve_property_name(client, normalized_id, ["Aliment", "Name", "Nom"])
    if not name_key:
        name_key = find_property_by_type(client, normalized_id, ["title"])
    if not name_key:
        available = ", ".join(f"{name} ({definition.get('type')})" for name, definition in schema.items())
        raise RuntimeError(
            "Impossible de trouver la colonne 'Aliment' (propriété de type titre) dans la base Stock. "
            f"Colonnes disponibles: {available}"
        )

    # Colonne quantité : on accepte un autre nom ou le premier champ numérique
    quantity_key = resolve_property_name(client, normalized_id, ["Quantité", "Quantite", "Quantity"])
    if not quantity_key:
        quantity_key = find_property_by_type(client, normalized_id, ["number"])

    # Colonne unité : texte libre, select ou multi-select
    unit_key = resolve_property_name(client, normalized_id, ["Unité", "Unite", "Unit"])
    if not unit_key:
        unit_key = find_property_by_type(client, normalized_id, ["rich_text", "select", "multi_select"])

    pages = export_database(client, normalized_id)
    items = []
    for page in pages:
        if not page:
            continue
        aliment = str(page.get(name_key) or "").strip()
        if not aliment:
            continue

        item = dict(page)
        if quantity_key and quantity_key in item:
            item[quantity_key] = _to_number(item.get(quantity_key))
        if unit_key and unit_key in item and item[unit_key] is None:
            item[unit_key] = ""

        # Sauvegarde le schéma complet dans l'item pour la synchronisation inverse
        item["__schema__"] = schema

        items.append(item)

    return items


def main() -> None:
    print("➡️  Lecture du stock Notion…")
    items = fetch_stock()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   ✅ {len(items)} élément(s) enregistré(s) dans {OUTPUT_PATH}")


if __name__ == "__main__":
    main()


