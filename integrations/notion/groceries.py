"""Push de la liste de courses vers Notion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from integrations.notion.client import get_client
from integrations.notion.config import get_config
from integrations.notion.mappers import grocery_to_notion_properties
from integrations.notion.upsert import clear_cache, upsert_page
from notion_tools.notion_reader import get_database_properties, normalize_id, export_database


def clear_courses_for_week(
    semaine_label: str,
    archive: bool = True
) -> int:
    """
    Archive les lignes de Semaine = semaine_label dans Courses.
    
    Args:
        semaine_label: Label de la semaine (ex: "Semaine 46 – 2025")
        archive: Si True, archive les pages (défaut: True)
    
    Returns:
        Nombre de lignes archivées
    """
    config = get_config()
    if not config.groceries_db_id:
        return 0
    
    client = get_client()
    db_id = normalize_id(config.groceries_db_id)
    if not db_id:
        return 0
    
    # Récupérer toutes les pages
    pages = export_database(client, db_id)
    
    # Filtrer par Semaine
    to_archive = []
    for page in pages:
        semaine_prop = page.get("Semaine") or page.get("Week")
        semaine_value = None
        if semaine_prop and isinstance(semaine_prop, dict):
            # Gérer select ou multi_select
            if "select" in semaine_prop:
                semaine_value = semaine_prop.get("select", {}).get("name")
            elif "multi_select" in semaine_prop:
                multi_values = semaine_prop.get("multi_select", [])
                if multi_values and isinstance(multi_values, list):
                    # Prendre la première valeur
                    semaine_value = multi_values[0].get("name") if isinstance(multi_values[0], dict) else str(multi_values[0])
        elif isinstance(semaine_prop, (str, list)):
            if isinstance(semaine_prop, list) and len(semaine_prop) > 0:
                semaine_value = semaine_prop[0] if isinstance(semaine_prop[0], str) else str(semaine_prop[0])
            else:
                semaine_value = str(semaine_prop)
        
        if semaine_value == semaine_label:
            page_id = page.get("id")
            if page_id:
                to_archive.append(page_id)
    
    # Archiver (ou supprimer)
    archived = 0
    for page_id in to_archive:
        try:
            if archive:
                # Archiver la page Notion
                client.pages.update(page_id=page_id, archived=True)
            archived += 1
        except Exception as e:
            print(f"   ⚠️ Erreur archivage page {page_id}: {e}")
    
    return archived


def push_groceries_to_notion(
    path: Path | str | None = None,
    clear_week: bool = False,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Push la liste de courses depuis achats_filtres.json vers Notion.
    
    Args:
        path: Chemin vers achats_filtres.json (défaut: data/achats_filtres.json)
        clear_week: Si True, purge les entrées de la semaine avant d'écrire
        dry_run: Si True, ne fait rien, juste valide
    
    Returns:
        Dict avec n_created, n_updated, n_errors
    """
    from app.config import DATA_DIR
    
    if path is None:
        path = DATA_DIR / "achats_filtres.json"
    elif isinstance(path, str):
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    
    config = get_config()
    if not config.groceries_db_id:
        raise ValueError("NOTION_GROCERIES_DB non configuré")
    
    # Charge les courses
    groceries_data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(groceries_data, list):
        raise ValueError(f"Le fichier {path} doit contenir une liste de courses")
    
    if dry_run:
        print(f"[DRY-RUN] {len(groceries_data)} articles à synchroniser")
        if clear_week:
            print("[DRY-RUN] Purge de la semaine activée")
        return {"n_created": 0, "n_updated": 0, "n_errors": 0}
    
    # Initialise
    client = get_client()
    normalized_db_id = normalize_id(config.groceries_db_id)
    if not normalized_db_id:
        raise ValueError(f"ID de base invalide : {config.groceries_db_id}")
    
    # Récupère le schéma
    schema = get_database_properties(client, normalized_db_id)
    
    # Trouve la propriété titre
    title_prop = None
    for prop_name, prop_def in schema.items():
        if prop_def.get("type") == "title":
            title_prop = prop_name
            break
    
    if not title_prop:
        raise RuntimeError("Impossible de trouver une propriété titre dans la base Courses")
    
    # Clear cache
    clear_cache()
    
    # Purge de la semaine si demandé
    if clear_week:
        print("   🗑️  Purge des entrées de la semaine...")
        from app.utils import week_label
        semaine = week_label()
        archived = clear_courses_for_week(semaine, archive=True)
        print(f"   {archived} entrée(s) archivée(s)")
    
    n_created = 0
    n_updated = 0
    n_errors = 0
    
    print(f"➡️  Synchronisation de {len(groceries_data)} articles vers Notion...")
    
    for grocery in groceries_data:
        try:
            # Récupère le nom
            name = (
                grocery.get("Aliment")
                or grocery.get("name")
                or grocery.get("Name")
                or grocery.get("Article")
                or "Article sans nom"
            )
            
            # Convertit en propriétés Notion
            properties = grocery_to_notion_properties(grocery, schema)
            
            # Upsert
            created, updated, page_id = upsert_page(
                client,
                normalized_db_id,
                name,
                properties,
                title_prop,
            )
            
            if created:
                n_created += 1
            elif updated:
                n_updated += 1
                
        except Exception as e:
            n_errors += 1
            print(f"   ❌ Erreur pour '{name}': {e}")
    
    print(f"   ✅ {n_created} créé(s), {n_updated} mis à jour, {n_errors} erreur(s)")
    
    return {
        "n_created": n_created,
        "n_updated": n_updated,
        "n_errors": n_errors,
    }


def main() -> None:
    """CLI pour push_groceries_to_notion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Push la liste de courses vers Notion")
    parser.add_argument(
        "--file",
        type=Path,
        default=None,
        help="Chemin vers achats_filtres.json (défaut: data/achats_filtres.json)",
    )
    parser.add_argument(
        "--clear-week",
        action="store_true",
        help="Purge les entrées de la semaine avant d'écrire",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mode dry-run (ne fait rien)",
    )
    args = parser.parse_args()
    
    try:
        result = push_groceries_to_notion(
            path=args.file,
            clear_week=args.clear_week,
            dry_run=args.dry_run,
        )
        if args.dry_run:
            print(f"[DRY-RUN] Résultat: {result}")
    except Exception as e:
        print(f"Erreur: {e}")
        exit(1)


if __name__ == "__main__":
    main()

