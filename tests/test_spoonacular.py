"""Tests pour le module Spoonacular."""

from unittest.mock import Mock, patch
import pytest

from app.spoonacular import normalize, get_recipe_ingredients_with_quantities


def test_normalize_recipe():
    """Test normalisation d'une recette Spoonacular."""
    raw_recipe = {
        "title": "Chicken Recipe",
        "readyInMinutes": 30,
        "servings": 4,
        "sourceUrl": "https://example.com",
        "image": "https://example.com/image.jpg",
        "extendedIngredients": [
            {
                "name": "chicken",
                "nameClean": "chicken breast",
                "measures": {
                    "metric": {"amount": 500, "unitShort": "g", "unit": "grams"}
                },
            },
            {
                "name": "tomatoes",
                "measures": {"metric": {"amount": 2, "unitShort": "piece"}},
            },
        ],
        "nutrition": {
            "nutrients": [
                {"name": "Calories", "amount": 500},
                {"name": "Protein", "amount": 40},
                {"name": "Carbohydrates", "amount": 20},
                {"name": "Fat", "amount": 15},
            ]
        },
    }
    
    normalized = normalize(raw_recipe)
    
    assert normalized["title"] == "Chicken Recipe"
    assert normalized["readyMinutes"] == 30
    assert normalized["servings"] == 4
    assert normalized["sourceUrl"] == "https://example.com"
    assert "ingredients" in normalized
    assert len(normalized["ingredients"]) == 2
    assert normalized["ingredients"][0]["name"] == "chicken breast"
    assert normalized["ingredients"][0]["amount"] == 500
    assert normalized["ingredients"][0]["unit"] == "g"
    assert normalized["nutrition"]["calories"] == 500
    assert normalized["nutrition"]["protein"] == 40


def test_normalize_recipe_preserves_id():
    """Test que normalize préserve l'ID Spoonacular."""
    raw_recipe = {
        "id": 123456,
        "title": "Test Recipe",
        "readyInMinutes": 30,
        "servings": 4,
        "sourceUrl": "https://example.com",
        "image": "https://example.com/image.jpg",
        "extendedIngredients": [],
        "nutrition": {"nutrients": []},
    }
    
    normalized = normalize(raw_recipe)
    
    assert normalized["id"] == 123456


def test_normalize_recipe_without_id():
    """Test normalisation sans ID."""
    raw_recipe = {
        "title": "Test Recipe",
        "readyInMinutes": 30,
        "servings": 4,
        "sourceUrl": "https://example.com",
        "image": "https://example.com/image.jpg",
        "extendedIngredients": [],
        "nutrition": {"nutrients": []},
    }
    
    normalized = normalize(raw_recipe)
    
    assert "id" not in normalized


@patch('app.spoonacular.SPOONACULAR_API_KEY', 'test_key')
@patch('app.spoonacular.BASE_URL', 'https://api.spoonacular.com')
@patch('app.spoonacular.requests.get')
@patch('app.spoonacular.retry_http')
def test_get_recipe_ingredients_with_quantities(
    mock_retry,
    mock_get,
):
    """Test récupération des ingrédients avec quantités."""
    # Mock retry_http
    def mock_retry_wrapper(func):
        return func
    mock_retry.return_value = mock_retry_wrapper
    
    # Mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 123456,
        "title": "Chicken Recipe",
        "extendedIngredients": [
            {
                "name": "chicken",
                "nameClean": "chicken breast",
                "originalString": "500g chicken breast",
                "measures": {
                    "metric": {"amount": 500, "unitShort": "g", "unit": "grams"}
                },
                "aisle": "Meat",
            },
            {
                "name": "tomatoes",
                "nameClean": "tomatoes",
                "originalString": "2 tomatoes",
                "measures": {
                    "metric": {"amount": 2, "unitShort": "piece", "unit": "pieces"}
                },
                "aisle": "Produce",
            },
        ],
    }
    mock_get.return_value = mock_response
    
    result = get_recipe_ingredients_with_quantities(123456, portions_multiplier=2.0)
    
    assert len(result) == 2
    assert result[0]["name"] == "chicken breast"
    assert result[0]["amount"] == 1000  # 500 * 2
    assert result[0]["unit"] == "g"
    assert result[0]["aisle"] == "Meat"
    assert result[0]["recipe_id"] == 123456
    assert result[1]["amount"] == 4  # 2 * 2


@patch('app.spoonacular.SPOONACULAR_API_KEY', None)
@patch('app.spoonacular.SPOONACULAR_API_KEY2', None)
def test_get_recipe_ingredients_with_quantities_no_key():
    """Test erreur quand aucune clé API."""
    with pytest.raises(RuntimeError, match="Aucune clé API"):
        get_recipe_ingredients_with_quantities(123456)


def test_normalize_recipe_minimal():
    """Test normalisation avec données minimales."""
    raw_recipe = {
        "title": "Simple Recipe",
    }
    
    normalized = normalize(raw_recipe)
    
    assert normalized["title"] == "Simple Recipe"
    assert normalized["servings"] == 1  # Valeur par défaut
    assert "ingredients" in normalized
    assert isinstance(normalized["ingredients"], list)

