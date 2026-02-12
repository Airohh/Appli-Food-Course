"""Tests pour le module workflow_stock."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from app.workflow_stock import subtract_stock_when_recipe_completed


@pytest.fixture
def mock_client():
    """Mock du client Notion."""
    return Mock()


@pytest.fixture
def mock_recipe_page():
    """Page de recette mockée."""
    return {
        "id": "recipe_page_id",
        "properties": {
            "Terminée": {"checkbox": True},
            "Portions": {"number": 4},
            "Lien": {"url": "https://spoonacular.com/recipes/123456"},
            "Name": {"title": [{"plain_text": "Poulet rôti"}]},
        },
    }


@patch('app.workflow_stock.get_client')
@patch('app.workflow_stock.normalize_id')
@patch('app.workflow_stock.get_recipe_ingredients_with_quantities')
@patch('app.workflow_stock.fetch_stock')
@patch('app.workflow_stock.subtract_stock_from_groceries')
def test_subtract_stock_when_recipe_completed(
    mock_subtract,
    mock_fetch_stock,
    mock_get_ingredients,
    mock_normalize_id,
    mock_get_client,
    mock_client,
    mock_recipe_page,
):
    """Test soustraction du stock quand recette terminée."""
    mock_normalize_id.side_effect = lambda x: "db_id" if x else None
    mock_get_client.return_value = mock_client
    mock_client.pages.retrieve.return_value = mock_recipe_page
    
    mock_get_ingredients.return_value = [
        {
            "name": "chicken",
            "amount": 500,
            "unit": "g",
        },
        {
            "name": "tomatoes",
            "amount": 2,
            "unit": "piece",
        },
    ]
    
    mock_fetch_stock.return_value = [
        {
            "Aliment": "chicken",
            "Quantité": 1000,
            "Unité": "g",
            "Categorie": "durable",
        },
    ]
    
    mock_subtract.return_value = [
        {"Aliment": "chicken", "Quantité": 500, "Unité": "g"},
        {"Aliment": "tomatoes", "Quantité": 2, "Unité": "piece"},
    ]
    
    with patch('app.workflow_stock.get_database_properties') as mock_schema, \
         patch('app.workflow_stock.upsert_page') as mock_upsert, \
         patch('app.workflow_stock.grocery_to_notion_properties') as mock_map:
        mock_schema.return_value = {"Aliment": {"type": "title"}}
        mock_map.return_value = {}
        
        result = subtract_stock_when_recipe_completed(
            "recipe_page_id",
            dry_run=False,
        )
        
        assert "error" not in result
        assert result["ingredients_processed"] == 2
        assert result["stock_updated"] == 1
        assert result["spoon_id"] == 123456


@patch('app.workflow_stock.get_client')
@patch('app.workflow_stock.normalize_id')
def test_subtract_stock_when_recipe_not_completed(
    mock_normalize_id,
    mock_get_client,
    mock_client,
    mock_recipe_page,
):
    """Test quand la recette n'est pas terminée."""
    mock_normalize_id.side_effect = lambda x: "db_id" if x else None
    mock_get_client.return_value = mock_client
    
    # Recette non terminée
    mock_recipe_page["properties"]["Terminée"] = {"checkbox": False}
    mock_client.pages.retrieve.return_value = mock_recipe_page
    
    result = subtract_stock_when_recipe_completed("recipe_page_id", dry_run=False)
    
    assert "error" in result
    assert result["error"] == "Recette non terminée"


@patch('app.workflow_stock.get_client')
@patch('app.workflow_stock.normalize_id')
def test_subtract_stock_when_recipe_no_spoon_id(
    mock_normalize_id,
    mock_get_client,
    mock_client,
    mock_recipe_page,
):
    """Test quand la recette n'a pas de spoon_id."""
    mock_normalize_id.side_effect = lambda x: "db_id" if x else None
    mock_get_client.return_value = mock_client
    
    # Pas de lien
    mock_recipe_page["properties"]["Lien"] = None
    mock_client.pages.retrieve.return_value = mock_recipe_page
    
    result = subtract_stock_when_recipe_completed("recipe_page_id", dry_run=False)
    
    assert "error" in result
    assert "Impossible de récupérer l'ID Spoonacular" in result["error"]


@patch('app.workflow_stock.get_client')
@patch('app.workflow_stock.normalize_id')
@patch('app.workflow_stock.get_recipe_ingredients_with_quantities')
def test_subtract_stock_when_recipe_ingredients_error(
    mock_get_ingredients,
    mock_normalize_id,
    mock_get_client,
    mock_client,
    mock_recipe_page,
):
    """Test quand erreur lors de la récupération des ingrédients."""
    mock_normalize_id.side_effect = lambda x: "db_id" if x else None
    mock_get_client.return_value = mock_client
    mock_client.pages.retrieve.return_value = mock_recipe_page
    
    mock_get_ingredients.side_effect = Exception("API Error")
    
    result = subtract_stock_when_recipe_completed("recipe_page_id", dry_run=False)
    
    assert "error" in result
    assert "Erreur récupération ingrédients" in result["error"]

