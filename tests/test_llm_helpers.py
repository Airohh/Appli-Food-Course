"""Tests pour les fonctions helper du module LLM."""

import pytest

from app.llm import _lite_candidates, get_prompt_version, PROMPT_VERSIONS


def test_lite_candidates():
    """Test réduction des recettes candidates."""
    candidates = [
        {
            "title": "Recette 1",
            "readyMinutes": 30,
            "nutrition": {"protein": 30, "calories": 500},
            "ingredients": [{"name": "poulet"}, {"name": "tomates"}],
        },
        {
            "title": "Recette 2",
            "readyMinutes": 60,  # Trop long
            "nutrition": {"protein": 20, "calories": 400},
            "ingredients": [{"name": "riz"}],
        },
        {
            "title": "Recette 3",
            "readyMinutes": 25,
            "nutrition": {"protein": 35, "calories": 600},
            "ingredients": [{"name": "saumon"}],
        },
    ]
    
    result = _lite_candidates(candidates, limit=2)
    
    assert len(result) <= 2
    assert all("title" in r for r in result)
    assert all("readyMinutes" in r for r in result)
    assert all("ingredients" in r for r in result)


def test_lite_candidates_empty():
    """Test avec liste vide."""
    result = _lite_candidates([], limit=10)
    assert result == []


def test_lite_candidates_limit():
    """Test que le limit est respecté."""
    candidates = [
        {
            "title": f"Recette {i}",
            "readyMinutes": 30,
            "nutrition": {"protein": 30, "calories": 500},
            "ingredients": [{"name": "ingredient"}],
        }
        for i in range(50)
    ]
    
    result = _lite_candidates(candidates, limit=10)
    assert len(result) <= 10

