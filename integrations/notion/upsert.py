"""Fonctions d'upsert idempotentes pour Notion."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from notion_client import Client

from integrations.notion.client import safe_notion_call
from integrations.notion.mappers import normalize_text
from notion_tools.notion_reader import (
    get_database_properties,
    iter_database_pages,
    normalize_id,
    simplify_property,
)


# Cache local pour éviter les requêtes répétées (par DB, par run)
_title_to_page_id_cache: Dict[str, Dict[str, str]] = {}


def clear_cache() -> None:
    """Vide le cache des titres → page_id."""
    global _title_to_page_id_cache
    _title_to_page_id_cache = {}


def find_page_by_title(
    client: Client,
    database_id: str,
    title: str,
    title_property: Optional[str] = None,
) -> Optional[str]:
    """
    Trouve une page par son titre dans une base Notion.
    
    Utilise un cache local pour éviter les requêtes répétées.
    
    Args:
        client: Client Notion
        database_id: ID de la base
        title: Titre à chercher
        title_property: Nom de la propriété titre (si None, détecte automatiquement)
    
    Returns:
        page_id si trouvé, None sinon
    """
    # Normalise l'ID de la base
    normalized_db_id = normalize_id(database_id)
    if not normalized_db_id:
        return None
    
    # Normalise le titre pour le cache
    normalized_title = normalize_text(title)
    
    # Vérifie le cache
    if normalized_db_id not in _title_to_page_id_cache:
        _title_to_page_id_cache[normalized_db_id] = {}
    
    if normalized_title in _title_to_page_id_cache[normalized_db_id]:
        return _title_to_page_id_cache[normalized_db_id][normalized_title]
    
    # Récupère le schéma pour trouver la propriété titre
    if not title_property:
        try:
            schema = get_database_properties(client, normalized_db_id)
            for prop_name, prop_def in schema.items():
                if prop_def.get("type") == "title":
                    title_property = prop_name
                    break
        except Exception:
            pass
    
    # Parcourt les pages pour trouver le titre
    try:
        for page in iter_database_pages(client, normalized_db_id):
            props = page.get("properties", {})
            
            # Si on connaît la propriété titre, on l'utilise directement
            if title_property and title_property in props:
                page_title = simplify_property(props[title_property])
                if normalize_text(str(page_title)) == normalized_title:
                    page_id = page.get("id")
                    if page_id:
                        _title_to_page_id_cache[normalized_db_id][normalized_title] = page_id
                        return page_id
            else:
                # Sinon, on cherche toutes les propriétés de type title
                for prop_name, prop_value in props.items():
                    if prop_value.get("type") == "title":
                        page_title = simplify_property(prop_value)
                        if normalize_text(str(page_title)) == normalized_title:
                            page_id = page.get("id")
                            if page_id:
                                _title_to_page_id_cache[normalized_db_id][normalized_title] = page_id
                                return page_id
    except Exception:
        pass
    
    return None


def upsert_page(
    client: Client,
    database_id: str,
    title: str,
    properties: Dict,
    title_property: Optional[str] = None,
) -> Tuple[bool, bool, str]:
    """
    Crée ou met à jour une page dans Notion (idempotent).
    
    Args:
        client: Client Notion
        database_id: ID de la base
        title: Titre de la page (pour le matching)
        properties: Propriétés Notion (doit inclure le titre)
        title_property: Nom de la propriété titre (si None, détecte automatiquement)
    
    Returns:
        Tuple (created, updated, page_id)
        - created: True si la page a été créée
        - updated: True si la page a été mise à jour
        - page_id: ID de la page
    """
    # Normalise l'ID de la base
    normalized_db_id = normalize_id(database_id)
    if not normalized_db_id:
        raise ValueError(f"ID de base invalide: {database_id}")
    
    # Cherche la page existante
    existing_page_id = find_page_by_title(client, normalized_db_id, title, title_property)
    
    if existing_page_id:
        # Mise à jour
        try:
            safe_notion_call(
                client.pages.update,
                page_id=existing_page_id,
                properties=properties,
            )
            return (False, True, existing_page_id)
        except Exception as e:
            # Si la mise à jour échoue, on essaie de créer (peut-être que la page a été supprimée)
            pass
    
    # Création
    try:
        new_page = safe_notion_call(
            client.pages.create,
            parent={"database_id": normalized_db_id},
            properties=properties,
        )
        page_id = new_page.get("id")
        if page_id:
            # Met à jour le cache
            normalized_title = normalize_text(title)
            if normalized_db_id not in _title_to_page_id_cache:
                _title_to_page_id_cache[normalized_db_id] = {}
            _title_to_page_id_cache[normalized_db_id][normalized_title] = page_id
            return (True, False, page_id)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la création/mise à jour de la page '{title}': {e}")
    
    raise RuntimeError(f"Impossible de créer ou mettre à jour la page '{title}'")


def resolve_relation_by_title(
    client: Client,
    target_database_id: str,
    recipe_name: str,
    title_property: Optional[str] = None,
) -> Optional[str]:
    """
    Résout une relation en trouvant la page par titre.
    
    Utile pour créer des relations vers des recettes par nom.
    
    Returns:
        page_id si trouvé, None sinon
    """
    normalized_db_id = normalize_id(target_database_id)
    if not normalized_db_id:
        return None
    return find_page_by_title(client, normalized_db_id, recipe_name, title_property)

