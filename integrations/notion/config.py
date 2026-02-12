"""Configuration pour l'intégration Notion avec validation Pydantic."""

from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class NotionConfig(BaseModel):
    """Configuration Notion validée."""

    api_key: str = Field(..., description="Clé API Notion")
    recipes_db_id: str = Field(..., description="ID de la base Recettes")
    groceries_db_id: str = Field(..., description="ID de la base Courses")
    mealplan_db_id: Optional[str] = Field(None, description="ID de la base Meal Plan")
    stock_db_id: Optional[str] = Field(None, description="ID de la base Stock")
    sync_enabled: bool = Field(False, description="Activer la synchronisation Notion")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("NOTION_API_KEY est requis")
        return v.strip()

    @field_validator("recipes_db_id", "groceries_db_id")
    @classmethod
    def validate_required_db(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Les IDs des bases Recettes et Courses sont requis")
        return v.strip()

    def model_post_init(self, __context: object) -> None:
        """Valide que si sync_enabled=True, toutes les bases nécessaires sont présentes."""
        if self.sync_enabled:
            if not self.recipes_db_id:
                raise ValueError("NOTION_RECIPES_DB requis si NOTION_SYNC_ENABLED=true")
            if not self.groceries_db_id:
                raise ValueError("NOTION_GROCERIES_DB requis si NOTION_SYNC_ENABLED=true")
            # Meal Plan est optionnel même si sync activé (on peut juste sync recettes + courses)


def load_notion_config() -> NotionConfig:
    """
    Charge la configuration Notion depuis les variables d'environnement.
    
    Variables supportées (alignées sur l'existant) :
    - NOTION_API_KEY ou NOTION_TOKEN : Clé API
    - NOTION_RECIPES_DB : ID base Recettes
    - NOTION_GROCERIES_DB : ID base Courses
    - NOTION_MEALPLAN_DB : ID base Meal Plan (optionnel)
    - NOTION_STOCK_DB : ID base Stock (optionnel)
    - NOTION_SYNC_ENABLED : Activer la sync (défaut: false)
    
    Compatibilité : Supporte aussi les anciens noms *_DB_ID en alias.
    """
    # Charge depuis app.config pour réutiliser la logique existante
    from app.config import (
        NOTION_GROCERIES_DB,
        NOTION_RECIPES_DB,
        NOTION_STOCK_DB,
        api_key,
    )

    # API Key (priorité : NOTION_API_KEY > NOTION_TOKEN)
    notion_api_key = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN") or api_key or ""

    # DB IDs (priorité : env var > app.config)
    recipes_db = os.getenv("NOTION_RECIPES_DB") or NOTION_RECIPES_DB or ""
    groceries_db = os.getenv("NOTION_GROCERIES_DB") or NOTION_GROCERIES_DB or ""
    mealplan_db = os.getenv("NOTION_MEALPLAN_DB") or os.getenv("NOTION_DB_MEALPLAN_ID") or ""
    stock_db = os.getenv("NOTION_STOCK_DB") or NOTION_STOCK_DB or ""

    # Feature flag
    sync_enabled_str = os.getenv("NOTION_SYNC_ENABLED", "false").lower()
    sync_enabled = sync_enabled_str in ("true", "1", "yes", "on")

    return NotionConfig(
        api_key=notion_api_key,
        recipes_db_id=recipes_db,
        groceries_db_id=groceries_db,
        mealplan_db_id=mealplan_db if mealplan_db else None,
        stock_db_id=stock_db if stock_db else None,
        sync_enabled=sync_enabled,
    )


# Instance globale (lazy-loaded)
_config: Optional[NotionConfig] = None


def get_config() -> NotionConfig:
    """Retourne la configuration Notion (singleton)."""
    global _config
    if _config is None:
        _config = load_notion_config()
    return _config

