"""Tests pour les mappers Notion."""

import pytest

from integrations.notion.mappers import (
    recipe_to_notion_properties,
    grocery_to_notion_properties,
)


@pytest.fixture
def recipe_schema():
    """Schéma de base de données Recettes."""
    return {
        "Name": {"type": "title"},
        "Lien": {"type": "url"},
        "Temps": {"type": "number"},
        "Photo": {"type": "url"},
        "Portions": {"type": "number"},
        "Sélectionnée": {"type": "checkbox"},
        "Semaine": {"type": "select"},
        "Terminée": {"type": "checkbox"},
    }


@pytest.fixture
def grocery_schema():
    """Schéma de base de données Courses."""
    return {
        "Aliment": {"type": "title"},
        "Quantité": {"type": "number"},
        "Unité": {"type": "rich_text"},
        "Catégorie": {"type": "select"},
        "Semaine": {"type": "select"},
        "Acheté": {"type": "checkbox"},
    }


def test_recipe_to_notion_properties_portions(recipe_schema):
    """Test mapping des portions."""
    recipe = {
        "title": "Test Recipe",
        "Portions": 4,
    }
    
    props = recipe_to_notion_properties(recipe, recipe_schema)
    
    assert "Portions" in props
    assert props["Portions"]["number"] == 4


def test_recipe_to_notion_properties_selected(recipe_schema):
    """Test mapping de Sélectionnée."""
    recipe = {
        "title": "Test Recipe",
        "Sélectionnée": True,
    }
    
    props = recipe_to_notion_properties(recipe, recipe_schema)
    
    assert "Sélectionnée" in props
    assert props["Sélectionnée"]["checkbox"] is True


def test_recipe_to_notion_properties_semaine(recipe_schema):
    """Test mapping de Semaine (select ou multi_select)."""
    recipe = {
        "title": "Test Recipe",
        "Semaine": "Semaine 46 – 2025",
    }
    
    props = recipe_to_notion_properties(recipe, recipe_schema)
    
    assert "Semaine" in props
    # Le code détecte automatiquement si c'est select ou multi_select
    if "select" in props["Semaine"]:
        assert props["Semaine"]["select"]["name"] == "Semaine 46 – 2025"
    elif "multi_select" in props["Semaine"]:
        assert len(props["Semaine"]["multi_select"]) == 1
        assert props["Semaine"]["multi_select"][0]["name"] == "Semaine 46 – 2025"
    else:
        pytest.fail(f"Semaine devrait être select ou multi_select, mais c'est: {props['Semaine']}")


def test_recipe_to_notion_properties_terminee(recipe_schema):
    """Test mapping de Terminée."""
    recipe = {
        "title": "Test Recipe",
        "Terminée": True,
    }
    
    props = recipe_to_notion_properties(recipe, recipe_schema)
    
    assert "Terminée" in props
    assert props["Terminée"]["checkbox"] is True


def test_grocery_to_notion_properties_semaine(grocery_schema):
    """Test mapping de Semaine pour les courses."""
    grocery = {
        "Aliment": "Poulet",
        "Quantité": 500,
        "Unité": "g",
        "Semaine": "Semaine 46 – 2025",
    }
    
    props = grocery_to_notion_properties(grocery, grocery_schema)
    
    assert "Semaine" in props
    assert props["Semaine"]["select"]["name"] == "Semaine 46 – 2025"


def test_grocery_to_notion_properties_achete(grocery_schema):
    """Test mapping de Acheté."""
    grocery = {
        "Aliment": "Poulet",
        "Quantité": 500,
        "Unité": "g",
        "Acheté": True,
    }
    
    props = grocery_to_notion_properties(grocery, grocery_schema)
    
    assert "Acheté" in props
    assert props["Acheté"]["checkbox"] is True


def test_grocery_to_notion_properties_achete_false(grocery_schema):
    """Test mapping de Acheté = False."""
    grocery = {
        "Aliment": "Poulet",
        "Quantité": 500,
        "Unité": "g",
        "Acheté": False,
    }
    
    props = grocery_to_notion_properties(grocery, grocery_schema)
    
    assert "Acheté" in props
    assert props["Acheté"]["checkbox"] is False

