"""Tests pour le module validators."""

import pytest

from app.validators import (
    sanitize_course_item,
    validate_course_item,
    validate_courses_list,
    validate_recipe_item,
    validate_recipes_list,
)


def test_validate_course_item_valid():
    """Test validation d'un item de course valide."""
    item = {
        "Aliment": "Poulet",
        "Quantité": 500,
        "Unité": "g",
        "Recettes": "Recette 1",
    }
    is_valid, error = validate_course_item(item)
    assert is_valid
    assert error == ""


def test_validate_course_item_missing_aliment():
    """Test validation d'un item sans aliment."""
    item = {"Quantité": 500, "Unité": "g"}
    is_valid, error = validate_course_item(item)
    assert not is_valid
    assert "Aliment" in error


def test_validate_course_item_empty_aliment():
    """Test validation d'un item avec aliment vide."""
    item = {"Aliment": "", "Quantité": 500}
    is_valid, error = validate_course_item(item)
    assert not is_valid
    assert "vide" in error.lower()


def test_validate_courses_list_valid():
    """Test validation d'une liste de courses valide."""
    courses = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
        {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
    ]
    is_valid, errors = validate_courses_list(courses)
    assert is_valid
    assert len(errors) == 0


def test_validate_courses_list_invalid():
    """Test validation d'une liste avec items invalides."""
    courses = [
        {"Aliment": "Poulet", "Quantité": 500},
        {"Quantité": 3},  # Manque Aliment
    ]
    is_valid, errors = validate_courses_list(courses)
    assert not is_valid
    assert len(errors) > 0


def test_sanitize_course_item():
    """Test nettoyage d'un item de course."""
    item = {
        "Aliment": "  Poulet  ",
        "Quantité": "500",
        "Unité": "  g  ",
    }
    cleaned = sanitize_course_item(item)
    assert cleaned["Aliment"] == "Poulet"
    assert cleaned["Quantité"] == 500.0
    assert cleaned["Unité"] == "g"
    assert "Recettes" in cleaned
    assert "Categorie" in cleaned


def test_validate_recipe_item_valid():
    """Test validation d'une recette valide."""
    recipe = {"Nom": "Poulet grillé", "Temps": 30}
    is_valid, error = validate_recipe_item(recipe)
    assert is_valid
    assert error == ""


def test_validate_recipe_item_missing_name():
    """Test validation d'une recette sans nom."""
    recipe = {"Temps": 30}
    is_valid, error = validate_recipe_item(recipe)
    assert not is_valid
    assert "nom" in error.lower()

