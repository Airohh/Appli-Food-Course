"""Utilitaires communs pour lire les bases Notion."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

from notion_client import Client
from notion_client.errors import APIResponseError

from app.config import api_key


_DATABASE_PROPERTIES_CACHE: Dict[str, Dict[str, Dict]] = {}


def get_client() -> Client:
    if not api_key:
        raise RuntimeError("Clé API Notion manquante. Configure NOTION_API_KEY ou NOTION_TOKEN dans .env.")
    return Client(auth=api_key)


def normalize_id(raw_id: Optional[str]) -> Optional[str]:
    if not raw_id:
        return None

    token = raw_id.replace("-", "").strip()
    if len(token) != 32:
        return raw_id

    return f"{token[0:8]}-{token[8:12]}-{token[12:16]}-{token[16:20]}-{token[20:32]}"


@lru_cache(maxsize=None)
def get_data_source_id(client: Client, database_id: str) -> str:
    database = client.databases.retrieve(database_id=database_id)
    data_sources: Iterable[dict] = database.get("data_sources", [])
    if not data_sources:
        raise RuntimeError("Aucun data source associé à la base Notion.")
    return data_sources[0]["id"]


def query_data_source(client: Client, data_source_id: str, start_cursor: Optional[str] = None) -> Dict:
    body: Dict[str, object] = {}
    if start_cursor:
        body["start_cursor"] = start_cursor

    return client.request(
        path=f"data_sources/{data_source_id}/query",
        method="POST",
        body=body or None,
    )


def iter_database_pages(client: Client, database_id: str) -> Iterator[Dict]:
    normalized = normalize_id(database_id)
    if not normalized:
        return iter(())

    data_source_id = get_data_source_id(client, normalized)
    start_cursor: Optional[str] = None

    while True:
        response = query_data_source(client, data_source_id, start_cursor=start_cursor)
        results = response.get("results", [])
        for item in results:
            yield item

        if not response.get("has_more"):
            break
        start_cursor = response.get("next_cursor")


def _extract_text(spans: List[dict]) -> str:
    return "".join(span.get("plain_text", "") for span in spans).strip()


def simplify_property(prop: Dict) -> object:
    prop_type = prop.get("type")

    if prop_type == "title":
        return _extract_text(prop.get("title", []))
    if prop_type == "rich_text":
        return _extract_text(prop.get("rich_text", []))
    if prop_type == "number":
        return prop.get("number")
    if prop_type == "select":
        select = prop.get("select") or {}
        return select.get("name")
    if prop_type == "multi_select":
        return [item.get("name") for item in prop.get("multi_select", [])]
    if prop_type == "checkbox":
        return prop.get("checkbox")
    if prop_type == "date":
        date = prop.get("date") or {}
        if not date:
            return None
        return {
            "start": date.get("start"),
            "end": date.get("end"),
        }
    if prop_type == "relation":
        return [rel.get("id") for rel in prop.get("relation", [])]
    if prop_type == "people":
        return [person.get("id") for person in prop.get("people", [])]
    if prop_type == "url":
        return prop.get("url")
    if prop_type == "email":
        return prop.get("email")
    if prop_type == "phone_number":
        return prop.get("phone_number")
    if prop_type == "files":
        return [file.get("name") for file in prop.get("files", [])]
    if prop_type == "formula":
        formula = prop.get("formula") or {}
        return formula.get(formula.get("type"))
    if prop_type == "rollup":
        rollup = prop.get("rollup") or {}
        if rollup.get("type") == "array":
            return [simplify_property(item) for item in rollup.get("array", [])]
        return rollup.get(rollup.get("type"))

    return None


def page_to_dict(page: Dict) -> Dict:
    data: Dict[str, object] = {
        "id": page.get("id"),
        "url": page.get("url"),
        "created_time": page.get("created_time"),
        "last_edited_time": page.get("last_edited_time"),
    }

    props = page.get("properties", {})
    for name, prop in props.items():
        data[name] = simplify_property(prop)

    return data


def slugify(label: str) -> str:
    cleaned: List[str] = []
    for char in label.lower():
        if char.isalnum():
            cleaned.append(char)
        elif char in {" ", "-", "_", "#"}:
            if not cleaned or cleaned[-1] != "_":
                cleaned.append("_")
    slug = "".join(cleaned).strip("_")
    return slug or "database"


def export_database(client: Client, database_id: str) -> List[Dict]:
    return [page_to_dict(page) for page in iter_database_pages(client, database_id)]


def get_database_properties(client: Client, database_id: str) -> Dict[str, Dict]:
    normalized = normalize_id(database_id)
    if not normalized:
        raise RuntimeError("Identifiant de base de données invalide.")

    cache_key = normalized.replace("-", "").lower()
    if cache_key not in _DATABASE_PROPERTIES_CACHE:
        database = client.databases.retrieve(database_id=normalized)
        properties = database.get("properties") or {}

        if not properties:
            data_sources = database.get("data_sources", []) or []
            for ds in data_sources:
                ds_id = ds.get("id")
                if not ds_id:
                    continue
                try:
                    ds_info = client.request(path=f"/data_sources/{ds_id}", method="GET")
                except Exception:
                    continue

                if isinstance(ds_info, dict):
                    properties = (
                        ds_info.get("properties")
                        or (ds_info.get("schema") or {}).get("properties")
                        or ds_info.get("schema")
                        or {}
                    )
                if properties:
                    break

        if not properties:
            raise RuntimeError(
                "Impossible de récupérer le schéma de la base Notion (aucune propriété retournée)."
            )

        _DATABASE_PROPERTIES_CACHE[cache_key] = properties

    return _DATABASE_PROPERTIES_CACHE[cache_key]


def resolve_property_name(
    client: Client,
    database_id: str,
    candidates: Sequence[str],
) -> Optional[str]:
    properties = get_database_properties(client, database_id)
    normalized_candidates = [c.strip().lower() for c in candidates]

    for actual_name in properties.keys():
        if actual_name.strip().lower() in normalized_candidates:
            return actual_name
    return None


def find_property_by_type(
    client: Client,
    database_id: str,
    property_types: Sequence[str],
) -> Optional[str]:
    properties = get_database_properties(client, database_id)
    types_set = set(property_types)

    for actual_name, definition in properties.items():
        if definition.get("type") in types_set:
            return actual_name
    return None


def build_property_payload(value, definition: Dict) -> Optional[Dict]:
    prop_type = definition.get("type")

    if prop_type == "title":
        text = str(value or "Sans titre")
        return {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": text[:1900],
                    },
                }
            ]
        }

    if prop_type == "rich_text":
        content = str(value or "")
        if content:
            return {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": content[:1900],
                        },
                    }
                ]
            }
        return {"rich_text": []}

    if prop_type == "number":
        if value in ("", None):
            return {"number": None}
        try:
            return {"number": float(value)}
        except (TypeError, ValueError):
            return {"number": None}

    if prop_type == "select":
        if not value:
            return {"select": None}
        return {"select": {"name": str(value)}}

    if prop_type == "multi_select":
        if not value:
            return {"multi_select": []}
        if isinstance(value, str):
            items = [v.strip() for v in value.split(",") if v.strip()]
        else:
            items = [str(v).strip() for v in value if v]
        return {"multi_select": [{"name": v[:100]} for v in items]}

    if prop_type == "checkbox":
        if isinstance(value, bool):
            checked = value
        else:
            checked = str(value).strip().lower() in {"true", "1", "yes", "oui"}
        return {"checkbox": checked}

    if prop_type == "date":
        start = None
        end = None
        if isinstance(value, dict):
            start = value.get("start") or value.get("date") or value.get("value")
            end = value.get("end")
        elif value:
            start = str(value)
        return {"date": {"start": start, "end": end}} if start else {"date": None}

    if prop_type == "url":
        return {"url": str(value) if value else None}

    if prop_type == "email":
        return {"email": str(value) if value else None}

    if prop_type == "phone_number":
        return {"phone_number": str(value) if value else None}

    # Types non gérés : relation, people, files, formule complexe, etc.
    return None


