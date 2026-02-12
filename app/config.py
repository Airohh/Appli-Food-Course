# Charge les variables d'environnement et les IDs des bases Notion

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Union


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
DATABASES_PATH = PROJECT_ROOT / "databases.json"
DATA_DIR = PROJECT_ROOT / "data"


def _load_env_file(env_path: Path) -> None:
    # Lit le fichier .env et charge les variables (sans dépendance externe)

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _load_database_ids(path: Path) -> Union[Dict[str, str], List[str]]:
    if not path.exists():
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    if isinstance(raw, dict):
        return {
            str(key).strip().lower(): str(value).strip()
            for key, value in raw.items()
            if value
        }

    if isinstance(raw, list):
        return [str(item).strip() for item in raw if item]

    return {}


_load_env_file(ENV_PATH)

try:  # Optionnel : permet de surcharger via python-dotenv si installé
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - dépendance facultative
    load_dotenv = None  # type: ignore

if callable(load_dotenv):  # pragma: no branch - dépend de l'installation
    load_dotenv(ENV_PATH)
    load_dotenv()


_DATABASE_IDS: Union[Dict[str, str], List[str]] = _load_database_ids(DATABASES_PATH)


def _from_db_file(possible_keys: Iterable[str], index: int | None = None) -> str:
    if isinstance(_DATABASE_IDS, dict):
        for key in possible_keys:
            normalized = str(key).strip().lower()
            value = _DATABASE_IDS.get(normalized)
            if value:
                return value
    elif isinstance(_DATABASE_IDS, list) and index is not None:
        if 0 <= index < len(_DATABASE_IDS):
            return _DATABASE_IDS[index]
    return ""


api_key = (
    os.getenv("NOTION_API_KEY")
    or os.getenv("NOTION_TOKEN")
    or ""
)

NOTION_RECIPES_DB = (
    os.getenv("NOTION_RECIPES_DB")
    or _from_db_file(
        ("recipes", "recettes", "models_scorecard_db_id_1", "notion_recipes_db"),
        index=0,
    )
)

NOTION_GROCERIES_DB = (
    os.getenv("NOTION_GROCERIES_DB")
    or _from_db_file(
        ("groceries", "courses", "models_scorecard_db_id_2", "notion_groceries_db"),
        index=1,
    )
)

NOTION_STOCK_DB = (
    os.getenv("NOTION_STOCK_DB")
    or _from_db_file(
        ("stock", "models_scorecard_db_id_3", "notion_stock_db"),
        index=2,
    )
)

models_scorecard_db_id_1 = NOTION_RECIPES_DB
models_scorecard_db_id_2 = NOTION_GROCERIES_DB
models_scorecard_db_id_3 = NOTION_STOCK_DB


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY") or ""
SPOONACULAR_API_KEY2 = os.getenv("SPOONACULAR_API_KEY2") or ""
SPOONACULAR_API_KEY3 = os.getenv("SPOONACULAR_API_KEY3") or ""

DIET = os.getenv("DIET", "high-protein")
TARGET_CALORIES = int(os.getenv("TARGET_CALORIES", "2100"))
MAX_READY_MIN = int(os.getenv("MAX_READY_MIN", "45"))
N_RECIPES_CANDIDATES = int(os.getenv("N_RECIPES_CANDIDATES", "70"))
N_RECIPES_FINAL = int(os.getenv("N_RECIPES_FINAL", "6"))
LANG = os.getenv("LANG", "fr")

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() in {"true", "1", "yes"}

HAS_NOTION = bool(api_key and NOTION_RECIPES_DB and NOTION_GROCERIES_DB)
HAS_NOTION_STOCK = bool(api_key and NOTION_STOCK_DB)

# Notifications
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "")
NTFY_USER = os.getenv("NTFY_USER", "")  # Optionnel : pour topics privés
NTFY_PASS = os.getenv("NTFY_PASS", "")  # Optionnel : pour topics privés

# URLs Notion (optionnel : pour les notifications avec liens cliquables)
NOTION_RECIPES_VIEW_URL = os.getenv("NOTION_RECIPES_VIEW_URL", "")
NOTION_COURSES_VIEW_URL = os.getenv("NOTION_COURSES_VIEW_URL", "")

