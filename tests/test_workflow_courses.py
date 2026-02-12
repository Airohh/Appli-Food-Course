"""Tests pour le module workflow_courses."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from app.workflow_courses import (
    get_selected_recipes_this_week,
    generate_courses_from_selection,
)


@pytest.fixture
def mock_client():
    """Mock du client Notion."""
    return Mock()


@pytest.fixture
def mock_recipe_pages():
    """Pages de recettes mockées."""
    return [
        {
            "id": "recipe1",
            "Name": "Poulet rôti",
            "Sélectionnée": {"checkbox": True},
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
            "Portions": {"number": 4},
            "Lien": {"url": "https://spoonacular.com/recipes/123456"},
        },
        {
            "id": "recipe2",
            "Name": "Salade",
            "Sélectionnée": {"checkbox": True},
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
            "Portions": {"number": 2},
            "Lien": {"url": "https://spoonacular.com/recipes/789012"},
        },
        {
            "id": "recipe3",
            "Name": "Non sélectionnée",
            "Sélectionnée": {"checkbox": False},
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
        },
    ]


@patch('app.workflow_courses.get_client')
@patch('app.workflow_courses.export_database')
@patch('app.workflow_courses.normalize_id')
@patch('app.workflow_courses.week_label')
def test_get_selected_recipes_this_week(
    mock_week_label,
    mock_normalize_id,
    mock_export,
    mock_get_client,
    mock_client,
    mock_recipe_pages,
):
    """Test lecture des recettes sélectionnées."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_normalize_id.return_value = "db_id"
    mock_get_client.return_value = mock_client
    mock_export.return_value = mock_recipe_pages
    
    result = get_selected_recipes_this_week()
    
    # Seulement recipe1 et recipe2 devraient être retournées
    assert len(result) == 2
    assert result[0]["name"] == "Poulet rôti"
    assert result[0]["portions"] == 4
    assert result[0]["spoon_id"] == 123456
    assert result[1]["spoon_id"] == 789012


@patch('app.workflow_courses.get_client')
@patch('app.workflow_courses.export_database')
@patch('app.workflow_courses.normalize_id')
@patch('app.workflow_courses.week_label')
def test_get_selected_recipes_this_week_default_portions(
    mock_week_label,
    mock_normalize_id,
    mock_export,
    mock_get_client,
    mock_client,
):
    """Test avec portions par défaut."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_normalize_id.return_value = "db_id"
    mock_get_client.return_value = mock_client
    
    pages = [
        {
            "id": "recipe1",
            "Name": "Recette sans portions",
            "Sélectionnée": {"checkbox": True},
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
            "Lien": {"url": "https://spoonacular.com/recipes/123456"},
        },
    ]
    mock_export.return_value = pages
    
    result = get_selected_recipes_this_week()
    
    assert len(result) == 1
    assert result[0]["portions"] == 2  # Défaut


@patch('app.workflow_courses.get_selected_recipes_this_week')
@patch('app.workflow_courses.get_recipe_ingredients_with_quantities')
@patch('app.workflow_courses.fetch_stock')
@patch('app.workflow_courses.subtract_stock_from_groceries')
@patch('app.workflow_courses.push_groceries_to_notion')
@patch('app.workflow_courses.week_label')
@patch('app.workflow_courses.notify_ntfy')
@patch('app.workflow_courses.DATA_DIR')
def test_generate_courses_from_selection(
    mock_data_dir,
    mock_notify,
    mock_week_label,
    mock_push,
    mock_subtract,
    mock_fetch_stock,
    mock_get_ingredients,
    mock_get_selected,
    tmp_path,
):
    """Test génération des courses depuis sélection."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_get_selected.return_value = [
        {
            "name": "Poulet rôti",
            "portions": 4,
            "spoon_id": 123456,
            "page_id": "recipe1",
        }
    ]
    
    mock_get_ingredients.return_value = [
        {
            "name": "chicken",
            "amount": 500,
            "unit": "g",
            "aisle": "Meat",
            "recipe_title": "Poulet rôti",
        },
        {
            "name": "tomatoes",
            "amount": 2,
            "unit": "piece",
            "aisle": "Produce",
            "recipe_title": "Poulet rôti",
        },
    ]
    
    mock_fetch_stock.return_value = []
    mock_subtract.return_value = [
        {"Aliment": "chicken", "Quantité": 500, "Unité": "g"},
        {"Aliment": "tomatoes", "Quantité": 2, "Unité": "piece"},
    ]
    mock_push.return_value = {"n_created": 2, "n_updated": 0, "n_errors": 0}
    
    # Mock DATA_DIR
    mock_data_dir.__truediv__ = lambda self, other: tmp_path / other
    mock_data_dir.mkdir = Mock()
    
    result = generate_courses_from_selection(
        dry_run=False,
        notion_courses_url="https://notion.so/test",
    )
    
    assert result["n_selected"] == 1
    assert result["n_items"] == 2
    mock_notify.assert_called_once()


@patch('app.workflow_courses.get_selected_recipes_this_week')
@patch('app.workflow_courses.week_label')
def test_generate_courses_from_selection_no_recipes(
    mock_week_label,
    mock_get_selected,
):
    """Test quand aucune recette sélectionnée."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_get_selected.return_value = []
    
    result = generate_courses_from_selection(dry_run=True)
    
    assert result["n_selected"] == 0
    assert result["n_items"] == 0


@patch('app.workflow_courses.get_selected_recipes_this_week')
@patch('app.workflow_courses.get_recipe_ingredients_with_quantities')
@patch('app.workflow_courses.week_label')
def test_generate_courses_from_selection_no_spoon_id(
    mock_week_label,
    mock_get_ingredients,
    mock_get_selected,
):
    """Test avec recette sans spoon_id."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_get_selected.return_value = [
        {
            "name": "Recette sans ID",
            "portions": 2,
            "spoon_id": None,
            "page_id": "recipe1",
        }
    ]
    
    result = generate_courses_from_selection(dry_run=True)
    
    # La recette sans spoon_id devrait être ignorée
    mock_get_ingredients.assert_not_called()
    assert result["n_selected"] == 1
    assert result["n_items"] == 0

