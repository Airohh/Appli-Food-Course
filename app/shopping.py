# Fonctions pour regrouper les ingrédients et filtrer ce qui est déjà en stock

from __future__ import annotations

import json
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Dict, List, Sequence, Set

from .config import DATA_DIR

from unidecode import unidecode


def normalize_aliment(name: str | None) -> str:
    if not name:
        return ""
    return unidecode(str(name)).strip().lower()


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


def _build_stock_index(stock: Sequence[object] | None) -> Set[str]:
    index: Set[str] = set()
    if not stock:
        return index
    for item in stock:
        if isinstance(item, dict):
            name = item.get("Aliment") or item.get("name") or item.get("Nom")
        else:
            name = str(item)
        norm = normalize_aliment(name)
        if norm:
            index.add(norm)
    return index


def _is_available(aliment: str, stock_index: Set[str], fuzzy_threshold: float = 0.88) -> bool:
    norm = normalize_aliment(aliment)
    if not norm:
        return False
    if norm in stock_index:
        return True
    for candidate in stock_index:
        if SequenceMatcher(None, norm, candidate).ratio() >= fuzzy_threshold:
            return True
    return False


ROUNDING_RULES = {
    "spice": ("tsp", 0.25),
    "liquid": ("ml", 1.0),
    "meat": ("g", 10.0),
    "produce": ("piece", 1.0),
}

UNIT_CONVERSIONS = {
    # Conversions existantes
    ("g", "tsp"): lambda qty: qty / 5.0,
    ("tsp", "g"): lambda qty: qty * 5.0,
    ("g", "ml"): lambda qty: qty,
    ("ml", "g"): lambda qty: qty,
    ("piece", "g"): lambda qty: qty,
    ("g", "piece"): lambda qty: qty,
    # Nouvelles conversions
    ("tbsp", "ml"): lambda qty: qty * 15.0,
    ("ml", "tbsp"): lambda qty: qty / 15.0,
    ("tsp", "ml"): lambda qty: qty * 5.0,
    ("ml", "tsp"): lambda qty: qty / 5.0,
    ("cup", "ml"): lambda qty: qty * 240.0,
    ("ml", "cup"): lambda qty: qty / 240.0,
    ("oz", "g"): lambda qty: qty * 28.35,
    ("g", "oz"): lambda qty: qty / 28.35,
    ("lb", "g"): lambda qty: qty * 453.59,
    ("g", "lb"): lambda qty: qty / 453.59,
    ("clove", "pc"): lambda qty: qty,
    ("piece", "pc"): lambda qty: qty,
    ("pc", "piece"): lambda qty: qty,
}


def _convert_unit(qty: float, current_unit: str, target_unit: str) -> float:
    func = UNIT_CONVERSIONS.get((current_unit, target_unit))
    if not func:
        raise ValueError("Conversion indisponible")
    return func(qty)


def _apply_rounding(category: str | None, qty: float, unit: str) -> tuple[float, str]:
    rule = ROUNDING_RULES.get(category or "")
    if not rule:
        return qty, unit
    preferred_unit, step = rule
    try:
        if unit != preferred_unit:
            qty = _convert_unit(qty, unit, preferred_unit)
            unit = preferred_unit
        rounded = round(qty / step) * step
        return round(rounded, 4), unit
    except ValueError:
        return qty, unit


def consolidate_groceries(
    selected: List[Dict],
    stock: Sequence[object] | None = None,
    fuzzy_threshold: float = 0.88,
) -> List[Dict]:
    stock_index = _build_stock_index(stock)

    tally: Dict[str, Dict[str, object]] = defaultdict(
        lambda: {
            "Aliment": "",
            "units": defaultdict(float),
            "Notes": [],
            "Recettes": set(),
            "Category": None,
            "CategoryAlt": set(),
        }
    )

    for rec in selected:
        rec_name = rec.get("Nom") or rec.get("title") or rec.get("name") or ""
        ingredients = rec.get("ingredients") or rec.get("Ingrédients")

        def _process_ing(
            name: str,
            amount: float | None = None,
            unit: str | None = None,
            category: str | None = None,
            note: str | None = None,
        ):
            if not name:
                return
            if stock_index and _is_available(name, stock_index, fuzzy_threshold):
                return
            norm = normalize_aliment(name)
            if not norm:
                return
            entry = tally[norm]
            if not entry["Aliment"]:
                entry["Aliment"] = name
            unit_norm = (unit or "").strip()
            if amount is not None:
                entry["units"][unit_norm] += float(amount)
            else:
                entry["Notes"].append(str(unit or "").strip())
            if rec_name:
                entry["Recettes"].add(rec_name)
            if category:
                if not entry["Category"]:
                    entry["Category"] = category
                elif entry["Category"] != category:
                    entry["CategoryAlt"].add(category)
            if note:
                entry["Notes"].append(note)

        if isinstance(ingredients, str):
            for raw in [x.strip() for x in ingredients.split(",") if x.strip()]:
                _process_ing(raw)
        elif isinstance(ingredients, list) and ingredients:
            if isinstance(ingredients[0], dict):
                for ing in ingredients:
                    amount = _to_number(ing.get("amount"))
                    _process_ing(
                        ing.get("name"),
                        amount,
                        ing.get("unit"),
                        ing.get("category"),
                        ing.get("notes"),
                    )
            elif isinstance(ingredients[0], str):
                for raw in ingredients:
                    _process_ing(raw.strip())

    consolidated: List[Dict] = []
    for data in tally.values():
        units = data["units"]
        if len(units) == 1:
            unit, qty = next(iter(units.items()))
            qty_value = round(qty, 2) if qty else ""
            unit_value = unit
        else:
            qty_value = ""
            unit_value = ""
            if units:
                detail_parts = [
                    f"{round(val, 2)} {unit}".strip()
                    for unit, val in units.items()
                    if val
                ]
                if detail_parts:
                    data["Notes"].append(" + ".join(detail_parts))

        main_cat = data.get("Category")
        alt_cats = sorted(
            c for c in data.get("CategoryAlt", set()) if c and c != main_cat
        )

        if isinstance(qty_value, (int, float)) and unit_value:
            qty_value, unit_value = _apply_rounding(main_cat, qty_value, unit_value)

        entry = {
            "Aliment": data["Aliment"],
            "Quantité": qty_value,
            "Unité": unit_value,
            "Recettes": ", ".join(sorted(data["Recettes"])) if data["Recettes"] else "",
        }
        notes_joined = "; ".join(n for n in data["Notes"] if n).strip()
        if notes_joined:
            entry["Notes"] = notes_joined
        if main_cat:
            entry["Categorie"] = main_cat
        if alt_cats:
            entry["Categorie_alt"] = alt_cats
        consolidated.append(entry)

    consolidated.sort(key=lambda x: normalize_aliment(x["Aliment"]))
    return consolidated


def merge_courses(
    courses: List[Dict],
    stock: Sequence[object] | None = None,
    fuzzy_threshold: float = 0.88,
    return_stats: bool = False,
) -> List[Dict] | tuple[List[Dict], Dict[str, int]]:
    stock_index = _build_stock_index(stock)

    tally: Dict[str, Dict[str, object]] = defaultdict(
        lambda: {
            "Aliment": "",
            "units": defaultdict(float),
            "Notes": [],
            "Recettes": set(),
            "Categorie": None,
            "CategoryAlt": set(),
        }
    )

    skipped_stock = 0
    for item in courses:
        name = item.get("Aliment") or item.get("Name") or item.get("Nom") or ""
        norm = normalize_aliment(name)
        if not norm:
            continue
        if stock_index and _is_available(name, stock_index, fuzzy_threshold):
            skipped_stock += 1
            continue

        unit = item.get("Unité") or item.get("Unite") or ""
        amount = _to_number(item.get("Quantité") or item.get("Quantite"))
        notes = item.get("Notes") or ""

        entry = tally[norm]
        if not entry["Aliment"]:
            entry["Aliment"] = name
        incoming_category = item.get("Categorie") or item.get("Category")
        if incoming_category:
            if not entry["Categorie"]:
                entry["Categorie"] = incoming_category
            elif entry["Categorie"] != incoming_category:
                entry["CategoryAlt"].add(incoming_category)

        if amount is not None:
            entry["units"][unit] += amount
        else:
            entry["Notes"].append(str(item.get("Quantité") or item.get("Quantite") or ""))
        if notes:
            entry["Notes"].append(str(notes))
        recettes = item.get("Recettes") or item.get("Recette") or ""
        if recettes:
            entry["Recettes"].update(r.strip() for r in recettes.split(",") if r.strip())

    merged: List[Dict] = []
    for data in tally.values():
        units = data["units"]
        if len(units) == 1:
            unit, qty = next(iter(units.items()))
            qty_value = round(qty, 2) if qty else ""
            unit_value = unit
        else:
            qty_value = ""
            unit_value = ""
            if units:
                detail_parts = [
                    f"{round(val, 2)} {unit}".strip()
                    for unit, val in units.items()
                    if val
                ]
                if detail_parts:
                    data["Notes"].append(" + ".join(detail_parts))

        main_cat = data.get("Categorie")
        alt_cats = sorted(
            c for c in data.get("CategoryAlt", set()) if c and c != main_cat
        )
        if isinstance(qty_value, (int, float)) and unit_value:
            qty_value, unit_value = _apply_rounding(main_cat, qty_value, unit_value)

        entry = {
            "Aliment": data["Aliment"],
            "Quantité": qty_value,
            "Unité": unit_value,
            "Recettes": ", ".join(sorted(data["Recettes"])) if data["Recettes"] else "",
        }
        if main_cat:
            entry["Categorie"] = main_cat
        if alt_cats:
            entry["Categorie_alt"] = alt_cats
        notes_joined = "; ".join(n for n in data["Notes"] if n).strip()
        if notes_joined:
            entry["Notes"] = notes_joined
        merged.append(entry)

    merged.sort(key=lambda x: normalize_aliment(x["Aliment"]))

    if return_stats:
        return merged, {
            "input": len(courses),
            "output": len(merged),
            "skipped_stock": skipped_stock,
        }
    return merged


DEFAULT_STOCK_PATH = DATA_DIR / "stock.json"


def prepare_stock_lookup(stock_path: str | None = None) -> List[Dict]:
    from pathlib import Path

    if stock_path is None:
        stock_path = DEFAULT_STOCK_PATH
    path = Path(stock_path)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _convert_unit_for_subtraction(
    qty: float,
    unit: str,
    stock_qty: float,
    stock_unit: str
) -> float | None:
    """
    Convertit les unités pour permettre la soustraction.
    
    Returns:
        Quantité convertie ou None si conversion impossible
    """
    # Normaliser les unités (simple lower, pas normalize_aliment qui est pour les noms)
    unit_lower = (unit or "").strip().lower()
    stock_unit_lower = (stock_unit or "").strip().lower()
    
    # Si même unité, pas de conversion
    if unit_lower == stock_unit_lower:
        return stock_qty
    
    # Conversions de base
    conversions = {
        ("g", "kg"): lambda x: x * 1000,
        ("kg", "g"): lambda x: x / 1000,
        ("ml", "l"): lambda x: x * 1000,
        ("l", "ml"): lambda x: x / 1000,
        ("ml", "cl"): lambda x: x * 10,
        ("cl", "ml"): lambda x: x / 10,
    }
    
    # Essayer conversion directe
    key = (stock_unit_lower, unit_lower)
    if key in conversions:
        return conversions[key](stock_qty)
    
    # Conversions via UNIT_CONVERSIONS si disponible
    try:
        if (stock_unit_lower, unit_lower) in UNIT_CONVERSIONS:
            return UNIT_CONVERSIONS[(stock_unit_lower, unit_lower)](stock_qty)
    except:
        pass
    
    return None


def subtract_stock_from_groceries(
    groceries: List[Dict[str, Any]],
    stock: Sequence[object] | None = None
) -> List[Dict[str, Any]]:
    """
    Soustrait le stock des courses (durable uniquement).
    
    Règles :
    - Si durable et quantité/unité compatibles → max(qty - stock, 0)
    - Si durable mais quantité inconnue → soustraire par défaut (g:200, ml:100, pc:1)
    - Si frais → ne pas soustraire
    
    Args:
        groceries: Liste de courses
        stock: Liste d'items du stock
    
    Returns:
        Liste de courses avec quantités soustraites
    """
    if not stock:
        return groceries
    
    # Construire un index du stock par nom normalisé
    stock_lookup: Dict[str, Dict[str, Any]] = {}
    for item in stock:
        if not isinstance(item, dict):
            continue
        
        name = item.get("Aliment") or item.get("Name") or item.get("Nom") or ""
        if not name:
            continue
        
        norm_name = normalize_aliment(name)
        if not norm_name:
            continue
        
        categorie = item.get("Categorie") or item.get("Category") or ""
        qty = _to_number(item.get("Quantité") or item.get("Quantity"))
        unit = item.get("Unité") or item.get("Unit") or ""
        
        stock_lookup[norm_name] = {
            "categorie": categorie.lower() if categorie else "",
            "qty": qty,
            "unit": unit,
        }
    
    result = []
    defaults = {"g": 200, "ml": 100, "pc": 1, "pièce": 1, "piece": 1}
    
    for grocery in groceries:
        name = grocery.get("Aliment") or grocery.get("name") or ""
        norm_name = normalize_aliment(name)
        
        if not norm_name:
            result.append(grocery)
            continue
        
        stock_item = stock_lookup.get(norm_name)
        
        # Si pas dans le stock, garder tel quel
        if not stock_item:
            result.append(grocery)
            continue
        
        categorie = stock_item["categorie"]
        
        # Si frais → ne pas soustraire
        if "frais" in categorie:
            result.append(grocery)
            continue
        
        # Si durable → soustraire
        grocery_qty = _to_number(grocery.get("Quantité") or grocery.get("Quantite") or 0) or 0
        grocery_unit = grocery.get("Unité") or grocery.get("Unite") or ""
        stock_qty = stock_item["qty"]
        stock_unit = stock_item["unit"]
        
        # Conversion et soustraction
        if stock_qty is not None and stock_unit and grocery_unit:
            # Essayer conversion
            converted_stock = _convert_unit_for_subtraction(
                grocery_qty, grocery_unit, stock_qty, stock_unit
            )
            if converted_stock is not None:
                new_qty = max(grocery_qty - converted_stock, 0)
                grocery["Quantité"] = new_qty
                result.append(grocery)
                continue
        
        # Si quantité inconnue → soustraire par défaut
        grocery_unit_lower = grocery_unit.lower() if grocery_unit else ""
        default_subtract = defaults.get(grocery_unit_lower, 0)
        new_qty = max(grocery_qty - default_subtract, 0)
        grocery["Quantité"] = new_qty
        result.append(grocery)
    
    return result