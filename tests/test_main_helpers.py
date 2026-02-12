"""Tests pour les fonctions helper du module main."""

import pytest

from app.main import _enrich_with_ingredients, _has_quantities, _stock_names


def test_stock_names():
    """Test extraction des noms de stock."""
    stock = [
        {"Aliment": "Poulet", "Quantité": 500},
        {"Aliment": "Tomates", "Quantité": 3},
        {"Aliment": "Riz", "Quantité": 1},
    ]
    
    names = _stock_names(stock)
    
    assert len(names) == 3
    assert "Poulet" in names
    assert "Tomates" in names
    assert "Riz" in names


def test_stock_names_empty():
    """Test avec stock vide."""
    names = _stock_names([])
    assert names == []


def test_stock_names_deduplication():
    """Test déduplication des noms (même nom en minuscules/majuscules)."""
    stock = [
        {"Aliment": "Poulet", "Quantité": 500},
        {"Aliment": "poulet", "Quantité": 300},  # Doublon
    ]
    
    names = _stock_names(stock)
    # Devrait garder seulement un "Poulet"
    assert len(names) == 1
    assert "Poulet" in names


def test_has_quantities():
    """Test détection de quantités."""
    groceries_with = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
        {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
    ]
    
    groceries_without = [
        {"Aliment": "Poulet"},
        {"Aliment": "Tomates", "Quantité": ""},
    ]
    
    assert _has_quantities(groceries_with) == True
    assert _has_quantities(groceries_without) == False


def test_has_quantities_mixed():
    """Test avec liste mixte (certains avec, certains sans quantités)."""
    groceries_mixed = [
        {"Aliment": "Poulet"},  # Sans quantité
        {"Aliment": "Tomates", "Quantité": 3},  # Avec quantité
    ]
    
    assert _has_quantities(groceries_mixed) == True  # Au moins un a une quantité


def test_enrich_with_ingredients():
    """Test enrichissement des recettes avec ingrédients."""
    selected = [
        {"Nom": "Recette 1", "Lien": "https://example.com/recipe1"},
    ]
    
    candidates = [
        {
            "title": "Recette 1",
            "sourceUrl": "https://example.com/recipe1",
            "readyMinutes": 30,
            "ingredients": [
                {"name": "poulet", "amount": 500, "unit": "g"},
                {"name": "tomates", "amount": 2, "unit": "pièces"},
            ],
            "nutrition": {"calories": 500, "protein": 40},
        },
    ]
    
    enriched = _enrich_with_ingredients(selected, candidates)
    
    assert len(enriched) == 1
    assert "ingredients" in enriched[0]
    assert len(enriched[0]["ingredients"]) == 2
    assert enriched[0]["Temps"] == 30


def test_enrich_with_ingredients_no_match():
    """Test quand aucune recette ne correspond."""
    selected = [{"Nom": "Recette X"}]
    candidates = [{"title": "Recette Y", "ingredients": []}]
    
    enriched = _enrich_with_ingredients(selected, candidates)
    
    assert len(enriched) == 1
    # La recette originale devrait être retournée sans modification
    assert "ingredients" not in enriched[0] or enriched[0].get("ingredients") is None

