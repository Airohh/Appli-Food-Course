"""Tests pour le module shopping."""

import pytest

from app.shopping import (
    consolidate_groceries,
    merge_courses,
    normalize_aliment,
    prepare_stock_lookup,
    subtract_stock_from_groceries,
    _convert_unit_for_subtraction,
)


def test_normalize_aliment():
    """Test normalisation des noms d'aliments."""
    assert normalize_aliment("Poulet") == "poulet"
    assert normalize_aliment("  Tomates  ") == "tomates"
    assert normalize_aliment("Épinards") == "epinards"  # Sans accents
    assert normalize_aliment(None) == ""
    assert normalize_aliment("") == ""


def test_consolidate_groceries_basic():
    """Test consolidation basique des ingrédients."""
    recipes = [
        {
            "Nom": "Recette 1",
            "ingredients": [
                {"name": "poulet", "amount": 200, "unit": "g"},
                {"name": "tomates", "amount": 2, "unit": "pièces"},
            ],
        },
        {
            "Nom": "Recette 2",
            "ingredients": [
                {"name": "poulet", "amount": 300, "unit": "g"},
                {"name": "oignons", "amount": 1, "unit": "pièce"},
            ],
        },
    ]
    
    result = consolidate_groceries(recipes)
    
    # Vérifier que les ingrédients sont consolidés
    assert len(result) > 0
    # Poulet devrait être fusionné (200g + 300g = 500g)
    poulet_items = [item for item in result if normalize_aliment(item.get("Aliment", "")) == "poulet"]
    assert len(poulet_items) > 0


def test_merge_courses_deduplication():
    """Test déduplication dans merge_courses."""
    courses = [
        {"Aliment": "Poulet", "Quantité": 200, "Unité": "g", "Recettes": "Recette 1"},
        {"Aliment": "poulet", "Quantité": 300, "Unité": "g", "Recettes": "Recette 2"},
        {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces", "Recettes": "Recette 1"},
    ]
    
    merged, stats = merge_courses(courses, return_stats=True)
    
    # Vérifier que les doublons sont fusionnés
    assert stats["output"] <= stats["input"]
    # Poulet devrait être fusionné
    poulet_items = [item for item in merged if normalize_aliment(item.get("Aliment", "")) == "poulet"]
    assert len(poulet_items) <= 1


def test_merge_courses_stock_filtering():
    """Test filtrage du stock dans merge_courses."""
    courses = [
        {"Aliment": "Poulet", "Quantité": 200, "Unité": "g"},
        {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
    ]
    
    stock = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    ]
    
    merged, stats = merge_courses(courses, stock=stock, return_stats=True)
    
    # Poulet devrait être filtré (déjà en stock)
    assert stats["skipped_stock"] > 0
    poulet_items = [item for item in merged if normalize_aliment(item.get("Aliment", "")) == "poulet"]
    assert len(poulet_items) == 0


def test_prepare_stock_lookup(tmp_path):
    """Test préparation de l'index de stock."""
    import json
    
    stock = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
        {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
    ]
    
    # Créer un fichier temporaire avec le stock
    stock_file = tmp_path / "stock.json"
    stock_file.write_text(json.dumps(stock, ensure_ascii=False), encoding="utf-8")
    
    result = prepare_stock_lookup(stock_file)
    
    assert result is not None
    assert len(result) == 2
    assert result[0]["Aliment"] == "Poulet"
    assert result[1]["Aliment"] == "Tomates"


def test_prepare_stock_lookup_empty(tmp_path):
    """Test avec fichier inexistant (retourne liste vide)."""
    stock_file = tmp_path / "nonexistent.json"
    result = prepare_stock_lookup(stock_file)
    assert result == []


def test_convert_unit_for_subtraction_same_unit():
    """Test conversion d'unités - même unité."""
    result = _convert_unit_for_subtraction(100, "g", 50, "g")
    assert result == 50


def test_convert_unit_for_subtraction_kg_to_g():
    """Test conversion kg vers g."""
    result = _convert_unit_for_subtraction(100, "g", 1, "kg")
    assert result == 1000


def test_convert_unit_for_subtraction_g_to_kg():
    """Test conversion g vers kg."""
    result = _convert_unit_for_subtraction(1000, "kg", 500, "g")
    assert result == 0.5


def test_convert_unit_for_subtraction_ml_to_l():
    """Test conversion ml vers l."""
    result = _convert_unit_for_subtraction(100, "ml", 1, "l")
    assert result == 1000


def test_convert_unit_for_subtraction_incompatible():
    """Test conversion d'unités incompatibles."""
    result = _convert_unit_for_subtraction(100, "g", 50, "ml")
    assert result is None


def test_subtract_stock_from_groceries_no_stock():
    """Test soustraction sans stock."""
    groceries = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    ]
    result = subtract_stock_from_groceries(groceries, stock=None)
    assert result == groceries


def test_subtract_stock_from_groceries_durable():
    """Test soustraction avec stock durable."""
    groceries = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    ]
    stock = [
        {
            "Aliment": "Poulet",
            "Quantité": 200,
            "Unité": "g",
            "Categorie": "durable",
        },
    ]
    result = subtract_stock_from_groceries(groceries, stock)
    assert len(result) == 1
    assert result[0]["Quantité"] == 300  # 500 - 200


def test_subtract_stock_from_groceries_frais():
    """Test que les frais ne sont pas soustraits."""
    groceries = [
        {"Aliment": "Tomates", "Quantité": 5, "Unité": "piece"},
    ]
    stock = [
        {
            "Aliment": "Tomates",
            "Quantité": 2,
            "Unité": "piece",
            "Categorie": "frais",
        },
    ]
    result = subtract_stock_from_groceries(groceries, stock)
    assert len(result) == 1
    assert result[0]["Quantité"] == 5  # Non soustrait


def test_subtract_stock_from_groceries_not_in_stock():
    """Test avec aliment non présent dans le stock."""
    groceries = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    ]
    stock = [
        {
            "Aliment": "Tomates",
            "Quantité": 2,
            "Unité": "piece",
            "Categorie": "frais",
        },
    ]
    result = subtract_stock_from_groceries(groceries, stock)
    assert len(result) == 1
    assert result[0]["Quantité"] == 500  # Non modifié


def test_subtract_stock_from_groceries_zero_result():
    """Test que le résultat ne peut pas être négatif."""
    groceries = [
        {"Aliment": "Poulet", "Quantité": 100, "Unité": "g"},
    ]
    stock = [
        {
            "Aliment": "Poulet",
            "Quantité": 500,
            "Unité": "g",
            "Categorie": "durable",
        },
    ]
    result = subtract_stock_from_groceries(groceries, stock)
    assert len(result) == 1
    assert result[0]["Quantité"] == 0  # max(100 - 500, 0) = 0


def test_subtract_stock_from_groceries_default_subtraction():
    """Test soustraction par défaut quand unités incompatibles."""
    groceries = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
    ]
    stock = [
        {
            "Aliment": "Poulet",
            "Quantité": 100,
            "Unité": "kg",  # Incompatible avec g
            "Categorie": "durable",
        },
    ]
    result = subtract_stock_from_groceries(groceries, stock)
    assert len(result) == 1
    # Devrait soustraire par défaut (200g pour "g")
    assert result[0]["Quantité"] == 300  # 500 - 200

