"""Tests pour l'intégration Notion Phase B (push functions)."""

import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from integrations.notion import config
from integrations.notion.groceries import push_groceries_to_notion
from integrations.notion.mealplan import push_mealplan_to_notion
from integrations.notion.recipes import push_recipes_to_notion


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_menu_json(tmp_path):
    """Crée un fichier menu.json de test."""
    menu_data = [
        {
            "Nom": "Poulet grillé",
            "Temps": 30,
            "Calories (~)": 450,
            "Protéines (g)": 45,
            "Lien": "https://example.com/poulet",
            "ingredients": [
                {"name": "chicken", "amount": 500, "unit": "g"},
            ],
        },
        {
            "Nom": "Salade de quinoa",
            "Temps": 20,
            "Calories (~)": 350,
            "Protéines (g)": 15,
        },
    ]
    menu_path = tmp_path / "menu.json"
    menu_path.write_text(json.dumps(menu_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return menu_path


@pytest.fixture
def mock_groceries_json(tmp_path):
    """Crée un fichier achats_filtres.json de test."""
    groceries_data = [
        {
            "Aliment": "Poulet",
            "Quantité": 500,
            "Unité": "g",
            "Catégorie": "Viande",
            "À acheter ?": True,
            "Recettes": "Poulet grillé",
        },
        {
            "Aliment": "Quinoa",
            "Quantité": 200,
            "Unité": "g",
            "Catégorie": "Céréales",
            "À acheter ?": True,
        },
    ]
    groceries_path = tmp_path / "achats_filtres.json"
    groceries_path.write_text(
        json.dumps(groceries_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return groceries_path


@pytest.fixture
def mock_notion_config():
    """Mock de la configuration Notion."""
    mock_cfg = Mock()
    mock_cfg.recipes_db_id = "recipes_db_123"
    mock_cfg.groceries_db_id = "groceries_db_123"
    mock_cfg.mealplan_db_id = "mealplan_db_123"
    mock_cfg.sync_enabled = True
    return mock_cfg


@pytest.fixture
def mock_notion_schema():
    """Mock du schéma Notion."""
    return {
        "Name": {"type": "title"},
        "Temps": {"type": "number"},
        "Calories (~)": {"type": "number"},
        "Protéines (g)": {"type": "number"},
        "Lien": {"type": "url"},
        "Article": {"type": "title"},
        "Quantité": {"type": "number"},
        "Unité": {"type": "rich_text"},
        "Catégorie": {"type": "select"},
        "À acheter ?": {"type": "checkbox"},
        "Date": {"type": "date"},
        "Type": {"type": "select"},
        "Recette": {"type": "relation"},
    }


# ============================================================================
# Tests push_recipes_to_notion
# ============================================================================

def test_push_recipes_dry_run(mock_menu_json, mock_notion_config):
    """Test push_recipes_to_notion en mode dry-run."""
    with patch("integrations.notion.recipes.get_config", return_value=mock_notion_config):
        result = push_recipes_to_notion(path=mock_menu_json, dry_run=True)
        
        assert result["n_created"] == 0
        assert result["n_updated"] == 0
        assert result["n_errors"] == 0


def test_push_recipes_file_not_found(mock_notion_config):
    """Test push_recipes_to_notion avec fichier inexistant."""
    with patch("integrations.notion.recipes.get_config", return_value=mock_notion_config):
        with pytest.raises(FileNotFoundError):
            push_recipes_to_notion(path="nonexistent.json", dry_run=False)


def test_push_recipes_success(mock_menu_json, mock_notion_config, mock_notion_schema):
    """Test push_recipes_to_notion avec succès."""
    mock_client = MagicMock()
    mock_page = {"id": "page_123"}
    
    with patch("integrations.notion.recipes.get_config", return_value=mock_notion_config):
        with patch("integrations.notion.recipes.get_client", return_value=mock_client):
            with patch(
                "integrations.notion.recipes.get_database_properties",
                return_value=mock_notion_schema,
            ):
                with patch("integrations.notion.recipes.normalize_id", return_value="db_123"):
                    with patch(
                        "integrations.notion.recipes.upsert_page",
                        return_value=(True, False, "page_123"),
                    ):
                        with patch("integrations.notion.recipes.clear_cache"):
                            result = push_recipes_to_notion(path=mock_menu_json, dry_run=False)
                            
                            assert result["n_created"] == 2  # 2 recettes
                            assert result["n_updated"] == 0
                            assert result["n_errors"] == 0


def test_push_recipes_missing_db_id(mock_menu_json):
    """Test push_recipes_to_notion sans DB ID configuré."""
    mock_cfg = Mock()
    mock_cfg.recipes_db_id = ""
    
    with patch("integrations.notion.recipes.get_config", return_value=mock_cfg):
        with pytest.raises(ValueError, match="NOTION_RECIPES_DB"):
            push_recipes_to_notion(path=mock_menu_json, dry_run=False)


# ============================================================================
# Tests push_mealplan_to_notion
# ============================================================================

def test_push_mealplan_dry_run(mock_menu_json, mock_notion_config):
    """Test push_mealplan_to_notion en mode dry-run."""
    with patch("integrations.notion.mealplan.get_config", return_value=mock_notion_config):
        result = push_mealplan_to_notion(path=mock_menu_json, dry_run=True)
        
        assert result["n_created"] == 0
        assert result["n_updated"] == 0
        assert result["n_errors"] == 0


def test_push_mealplan_success(mock_menu_json, mock_notion_config, mock_notion_schema):
    """Test push_mealplan_to_notion avec succès."""
    mock_client = MagicMock()
    
    with patch("integrations.notion.mealplan.get_config", return_value=mock_notion_config):
        with patch("integrations.notion.mealplan.get_client", return_value=mock_client):
            with patch(
                "integrations.notion.mealplan.get_database_properties",
                return_value=mock_notion_schema,
            ):
                with patch("integrations.notion.mealplan.normalize_id", side_effect=["db_mealplan", "db_recipes"]):
                    with patch(
                        "integrations.notion.mealplan.resolve_relation_by_title",
                        return_value="recipe_page_123",
                    ):
                        with patch(
                            "integrations.notion.mealplan.upsert_page",
                            return_value=(True, False, "page_123"),
                        ):
                            with patch("integrations.notion.mealplan.clear_cache"):
                                result = push_mealplan_to_notion(
                                    path=mock_menu_json,
                                    start_date=date(2024, 1, 15),
                                    dry_run=False,
                                )
                                
                                assert result["n_created"] == 2  # 2 recettes
                                assert result["n_updated"] == 0
                                assert result["n_errors"] == 0


def test_push_mealplan_missing_db_id(mock_menu_json):
    """Test push_mealplan_to_notion sans DB ID configuré."""
    mock_cfg = Mock()
    mock_cfg.mealplan_db_id = ""
    mock_cfg.recipes_db_id = "recipes_db_123"
    
    with patch("integrations.notion.mealplan.get_config", return_value=mock_cfg):
        with pytest.raises(ValueError, match="NOTION_MEALPLAN_DB"):
            push_mealplan_to_notion(path=mock_menu_json, dry_run=False)


def test_push_mealplan_empty_recipes(tmp_path, mock_notion_config):
    """Test push_mealplan_to_notion avec liste vide."""
    empty_menu = tmp_path / "empty_menu.json"
    empty_menu.write_text("[]", encoding="utf-8")
    
    with patch("integrations.notion.mealplan.get_config", return_value=mock_notion_config):
        result = push_mealplan_to_notion(path=empty_menu, dry_run=False)
        
        assert result["n_created"] == 0
        assert result["n_updated"] == 0
        assert result["n_errors"] == 0


# ============================================================================
# Tests push_groceries_to_notion
# ============================================================================

def test_push_groceries_dry_run(mock_groceries_json, mock_notion_config):
    """Test push_groceries_to_notion en mode dry-run."""
    with patch("integrations.notion.groceries.get_config", return_value=mock_notion_config):
        result = push_groceries_to_notion(path=mock_groceries_json, dry_run=True)
        
        assert result["n_created"] == 0
        assert result["n_updated"] == 0
        assert result["n_errors"] == 0


def test_push_groceries_success(mock_groceries_json, mock_notion_config, mock_notion_schema):
    """Test push_groceries_to_notion avec succès."""
    mock_client = MagicMock()
    
    with patch("integrations.notion.groceries.get_config", return_value=mock_notion_config):
        with patch("integrations.notion.groceries.get_client", return_value=mock_client):
            with patch(
                "integrations.notion.groceries.get_database_properties",
                return_value=mock_notion_schema,
            ):
                with patch("integrations.notion.groceries.normalize_id", return_value="db_123"):
                    with patch(
                        "integrations.notion.groceries.upsert_page",
                        return_value=(True, False, "page_123"),
                    ):
                        with patch("integrations.notion.groceries.clear_cache"):
                            result = push_groceries_to_notion(path=mock_groceries_json, dry_run=False)
                            
                            assert result["n_created"] == 2  # 2 articles
                            assert result["n_updated"] == 0
                            assert result["n_errors"] == 0


def test_push_groceries_missing_db_id(mock_groceries_json):
    """Test push_groceries_to_notion sans DB ID configuré."""
    mock_cfg = Mock()
    mock_cfg.groceries_db_id = ""
    
    with patch("integrations.notion.groceries.get_config", return_value=mock_cfg):
        with pytest.raises(ValueError, match="NOTION_GROCERIES_DB"):
            push_groceries_to_notion(path=mock_groceries_json, dry_run=False)


def test_push_groceries_with_clear_week(mock_groceries_json, mock_notion_config, mock_notion_schema):
    """Test push_groceries_to_notion avec clear_week."""
    mock_client = MagicMock()
    
    with patch("integrations.notion.groceries.get_config", return_value=mock_notion_config):
        with patch("integrations.notion.groceries.get_client", return_value=mock_client):
            with patch(
                "integrations.notion.groceries.get_database_properties",
                return_value=mock_notion_schema,
            ):
                with patch("integrations.notion.groceries.normalize_id", return_value="db_123"):
                    with patch(
                        "integrations.notion.groceries.upsert_page",
                        return_value=(True, False, "page_123"),
                    ):
                        with patch("integrations.notion.groceries.clear_cache"):
                            result = push_groceries_to_notion(
                                path=mock_groceries_json,
                                clear_week=True,
                                dry_run=False,
                            )
                            
                            # Le clear_week n'est pas encore implémenté, mais ça ne doit pas planter
                            assert result["n_created"] == 2


# ============================================================================
# Tests d'intégration (dry-run avec vrais fichiers)
# ============================================================================

def test_integration_dry_run_with_real_files():
    """Test d'intégration en dry-run avec les vrais fichiers (si existent)."""
    from app.config import DATA_DIR
    
    menu_path = DATA_DIR / "menu.json"
    groceries_path = DATA_DIR / "achats_filtres.json"
    
    # Mock la config pour éviter les erreurs
    mock_cfg = Mock()
    mock_cfg.recipes_db_id = "test_db"
    mock_cfg.groceries_db_id = "test_db"
    mock_cfg.mealplan_db_id = "test_db"
    
    if menu_path.exists():
        with patch("integrations.notion.recipes.get_config", return_value=mock_cfg):
            result = push_recipes_to_notion(path=menu_path, dry_run=True)
            assert "n_created" in result
            assert "n_updated" in result
            assert "n_errors" in result
    
    if groceries_path.exists():
        with patch("integrations.notion.groceries.get_config", return_value=mock_cfg):
            result = push_groceries_to_notion(path=groceries_path, dry_run=True)
            assert "n_created" in result
            assert "n_updated" in result
            assert "n_errors" in result

