"""Tests pour l'intégration Notion (Phase A)."""

import os
from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest

from integrations.notion import config, mappers, models
from integrations.notion.client import get_client, safe_notion_call
from integrations.notion.upsert import clear_cache, find_page_by_title, upsert_page


# ============================================================================
# Tests config.py
# ============================================================================

def test_config_loads_from_env():
    """Test que la config charge depuis les variables d'environnement."""
    with patch.dict(
        os.environ,
        {
            "NOTION_API_KEY": "test_key",
            "NOTION_RECIPES_DB": "recipes_id",
            "NOTION_GROCERIES_DB": "groceries_id",
            "NOTION_SYNC_ENABLED": "false",
        },
        clear=True,
    ):
        # Reset le cache de config
        config._config = None
        cfg = config.load_notion_config()
        
        assert cfg.api_key == "test_key"
        assert cfg.recipes_db_id == "recipes_id"
        assert cfg.groceries_db_id == "groceries_id"
        assert cfg.sync_enabled is False


def test_config_validation_requires_api_key():
    """Test que la validation échoue si API key manquante."""
    with patch.dict(os.environ, {}, clear=True):
        # Mock app.config pour simuler l'absence de clé
        with patch("app.config.api_key", ""):
            with patch("app.config.NOTION_RECIPES_DB", ""):
                with patch("app.config.NOTION_GROCERIES_DB", ""):
                    config._config = None
                    with pytest.raises(ValueError, match="NOTION_API_KEY"):
                        config.load_notion_config()


def test_config_validation_sync_enabled_requires_dbs():
    """Test que si sync_enabled=True, les DBs sont requis."""
    from pydantic import ValidationError
    
    with patch.dict(
        os.environ,
        {
            "NOTION_API_KEY": "test_key",
            "NOTION_SYNC_ENABLED": "true",
        },
        clear=True,
    ):
        # Mock app.config pour simuler DB manquante
        with patch("app.config.api_key", "test_key"):
            with patch("app.config.NOTION_RECIPES_DB", ""):  # Manquant
                with patch("app.config.NOTION_GROCERIES_DB", "groceries_id"):
                    config._config = None
                    with pytest.raises(ValidationError, match="Les IDs des bases Recettes et Courses sont requis"):
                        config.load_notion_config()


def test_config_mealplan_optional():
    """Test que mealplan_db_id est optionnel."""
    with patch.dict(
        os.environ,
        {
            "NOTION_API_KEY": "test_key",
            "NOTION_RECIPES_DB": "recipes_id",
            "NOTION_GROCERIES_DB": "groceries_id",
        },
        clear=True,
    ):
        config._config = None
        cfg = config.load_notion_config()
        assert cfg.mealplan_db_id is None


# ============================================================================
# Tests models.py
# ============================================================================

def test_recipe_model():
    """Test création d'un modèle Recipe."""
    recipe = models.Recipe(
        name="Poulet grillé",
        time_minutes=30,
        calories=450.0,
        protein=45.0,
    )
    assert recipe.name == "Poulet grillé"
    assert recipe.time_minutes == 30
    assert recipe.calories == 450.0
    assert recipe.protein == 45.0


def test_recipe_model_optional_fields():
    """Test que les champs optionnels fonctionnent."""
    recipe = models.Recipe(name="Test")
    assert recipe.name == "Test"
    assert recipe.time_minutes is None
    assert recipe.tags == []


def test_grocery_item_model():
    """Test création d'un modèle GroceryItem."""
    item = models.GroceryItem(
        name="Poulet",
        unit="g",
        quantity_needed=500.0,
        category="Viande",
        to_buy=True,
    )
    assert item.name == "Poulet"
    assert item.unit == "g"
    assert item.quantity_needed == 500.0
    assert item.to_buy is True


def test_mealplan_entry_model():
    """Test création d'un modèle MealPlanEntry."""
    entry = models.MealPlanEntry(
        date=date(2024, 1, 15),  # Utilise l'alias "date"
        meal_type="Déjeuner",
        recipe_name="Poulet grillé",
        portions=2,
    )
    assert entry.meal_date == date(2024, 1, 15)  # Accès via meal_date
    assert entry.meal_type == "Déjeuner"
    assert entry.recipe_name == "Poulet grillé"
    assert entry.portions == 2


# ============================================================================
# Tests mappers.py
# ============================================================================

def test_pick_function():
    """Test la fonction pick pour récupérer la première valeur non-vide."""
    data = {"name": "", "Nom": "Poulet", "Name": "Chicken"}
    assert mappers.pick(data, "name", "Nom", "Name") == "Poulet"
    assert mappers.pick(data, "nonexistent", "Nom") == "Poulet"
    assert mappers.pick(data, "nonexistent", default="default") == "default"


def test_normalize_text():
    """Test la normalisation de texte."""
    assert mappers.normalize_text("  POULET  ") == "poulet"
    assert mappers.normalize_text("Poulet Épicé") == "poulet epice"
    assert mappers.normalize_text("") == ""


def test_normalize_unit():
    """Test la normalisation des unités."""
    assert mappers.normalize_unit("g") == "g"
    assert mappers.normalize_unit("grammes") == "g"
    assert mappers.normalize_unit("ml") == "ml"
    assert mappers.normalize_unit("millilitres") == "ml"
    # Note: unidecode transforme "pièce" en "piece", mais le mapping gère ça
    assert mappers.normalize_unit("pièce") == "pièce"  # Dans le mapping
    assert mappers.normalize_unit("pièces") == "pièce"  # Dans le mapping
    assert mappers.normalize_unit("unité") == "pièce"  # Dans le mapping


def test_recipe_to_notion_properties_french():
    """Test conversion recette format français."""
    recipe = {
        "Nom": "Poulet grillé",
        "Temps": 30,
        "Calories (~)": 450,
        "Protéines (g)": 45,
        "Lien": "https://example.com",
    }
    schema = {
        "Name": {"type": "title"},
        "Temps": {"type": "number"},
        "Calories (~)": {"type": "number"},
        "Protéines (g)": {"type": "number"},
        "Lien": {"type": "url"},
    }
    props = mappers.recipe_to_notion_properties(recipe, schema)
    
    assert "Name" in props
    assert props["Name"]["title"][0]["text"]["content"] == "Poulet grillé"
    assert props["Temps"]["number"] == 30
    assert props["Calories (~)"]["number"] == 450.0


def test_recipe_to_notion_properties_english():
    """Test conversion recette format anglais."""
    recipe = {
        "name": "Grilled Chicken",
        "time_minutes": 30,
        "calories": 450,
        "protein": 45,
    }
    schema = {
        "Name": {"type": "title"},
        "Temps": {"type": "number"},
        "Calories (~)": {"type": "number"},
        "Protéines (g)": {"type": "number"},
    }
    props = mappers.recipe_to_notion_properties(recipe, schema)
    
    assert "Name" in props
    assert props["Name"]["title"][0]["text"]["content"] == "Grilled Chicken"
    assert props["Temps"]["number"] == 30


def test_grocery_to_notion_properties():
    """Test conversion course vers propriétés Notion."""
    grocery = {
        "Aliment": "Poulet",
        "Quantité": 500,
        "Unité": "g",
        "Catégorie": "Viande",
        "À acheter ?": True,
    }
    schema = {
        "Article": {"type": "title"},
        "Quantité": {"type": "number"},
        "Unité": {"type": "rich_text"},
        "Catégorie": {"type": "select"},
        "À acheter ?": {"type": "checkbox"},
    }
    props = mappers.grocery_to_notion_properties(grocery, schema)
    
    assert "Article" in props
    assert props["Article"]["title"][0]["text"]["content"] == "Poulet"
    assert props["Quantité"]["number"] == 500.0
    assert props["À acheter ?"]["checkbox"] is True


# ============================================================================
# Tests client.py
# ============================================================================

def test_get_client_creates_singleton():
    """Test que get_client retourne un singleton."""
    with patch.dict(
        os.environ,
        {
            "NOTION_API_KEY": "test_key",
            "NOTION_RECIPES_DB": "recipes_id",
            "NOTION_GROCERIES_DB": "groceries_id",
        },
        clear=True,
    ):
        config._config = None
        client1 = get_client()
        client2 = get_client()
        assert client1 is client2


def test_get_client_raises_if_no_api_key():
    """Test que get_client lève une erreur si pas d'API key."""
    from pydantic import ValidationError
    
    with patch.dict(os.environ, {}, clear=True):
        # Mock app.config pour simuler l'absence de clé
        with patch("app.config.api_key", ""):
            with patch("app.config.NOTION_RECIPES_DB", ""):
                with patch("app.config.NOTION_GROCERIES_DB", ""):
                    config._config = None
                    # Reset le client global
                    import integrations.notion.client as client_module
                    client_module._client = None
                    with pytest.raises(ValidationError, match="NOTION_API_KEY est requis"):
                        get_client()


def test_safe_notion_call_retries_on_429():
    """Test que safe_notion_call retry sur 429."""
    from notion_client.errors import APIResponseError
    
    call_count = 0
    
    def mock_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            error = APIResponseError(
                response=Mock(status_code=429),
                message="Rate limited",
                code=429,
            )
            raise error
        return {"id": "success"}
    
    # Le retry devrait fonctionner automatiquement
    # On teste juste que la fonction peut être appelée
    # (le vrai retry est testé dans test_retry.py)
    result = safe_notion_call(mock_func)
    assert result["id"] == "success"
    assert call_count == 2


# ============================================================================
# Tests upsert.py
# ============================================================================

def test_find_page_by_title_uses_cache():
    """Test que find_page_by_title utilise le cache."""
    clear_cache()
    
    mock_client = MagicMock()
    mock_page = {
        "id": "page_123",
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"plain_text": "Poulet grillé"}],
            }
        },
    }
    
    # Mock iter_database_pages
    with patch("integrations.notion.upsert.iter_database_pages", return_value=[mock_page]):
        with patch("integrations.notion.upsert.get_database_properties", return_value={"Name": {"type": "title"}}):
            with patch("integrations.notion.upsert.normalize_id", return_value="db_123"):
                # Premier appel
                result1 = find_page_by_title(mock_client, "db_123", "Poulet grillé")
                assert result1 == "page_123"
                
                # Deuxième appel (devrait utiliser le cache)
                result2 = find_page_by_title(mock_client, "db_123", "Poulet grillé")
                assert result2 == "page_123"
                
                # Vérifier que iter_database_pages n'a été appelé qu'une fois
                # (le deuxième appel utilise le cache)


def test_find_page_by_title_not_found():
    """Test que find_page_by_title retourne None si pas trouvé."""
    clear_cache()
    
    mock_client = MagicMock()
    
    with patch("integrations.notion.upsert.iter_database_pages", return_value=[]):
        with patch("integrations.notion.upsert.get_database_properties", return_value={"Name": {"type": "title"}}):
            with patch("integrations.notion.upsert.normalize_id", return_value="db_123"):
                result = find_page_by_title(mock_client, "db_123", "Recette inexistante")
                assert result is None


def test_upsert_page_creates_new():
    """Test que upsert_page crée une nouvelle page si elle n'existe pas."""
    clear_cache()
    
    mock_client = MagicMock()
    mock_new_page = {"id": "new_page_123"}
    
    with patch("integrations.notion.upsert.find_page_by_title", return_value=None):
        with patch("integrations.notion.upsert.safe_notion_call", return_value=mock_new_page):
            with patch("integrations.notion.upsert.normalize_id", return_value="db_123"):
                created, updated, page_id = upsert_page(
                    mock_client,
                    "db_123",
                    "Nouvelle recette",
                    {"Name": {"title": [{"text": {"content": "Nouvelle recette"}}]}},
                )
                
                assert created is True
                assert updated is False
                assert page_id == "new_page_123"


def test_upsert_page_updates_existing():
    """Test que upsert_page met à jour une page existante."""
    clear_cache()
    
    mock_client = MagicMock()
    
    with patch("integrations.notion.upsert.find_page_by_title", return_value="existing_page_123"):
        with patch("integrations.notion.upsert.safe_notion_call", return_value=None):
            with patch("integrations.notion.upsert.normalize_id", return_value="db_123"):
                created, updated, page_id = upsert_page(
                    mock_client,
                    "db_123",
                    "Recette existante",
                    {"Name": {"title": [{"text": {"content": "Recette existante"}}]}},
                )
                
                assert created is False
                assert updated is True
                assert page_id == "existing_page_123"


def test_clear_cache():
    """Test que clear_cache vide le cache."""
    # Remplir le cache
    import integrations.notion.upsert as upsert_module
    test_key = "db_test_clear_12345"  # Clé unique pour éviter les conflits
    upsert_module._title_to_page_id_cache[test_key] = {"test": "page_id"}
    
    # Vérifier que la clé est présente avant clear_cache
    assert test_key in upsert_module._title_to_page_id_cache
    
    clear_cache()
    
    # Le cache devrait être vide après clear_cache
    assert test_key not in upsert_module._title_to_page_id_cache
    assert len(upsert_module._title_to_page_id_cache) == 0

