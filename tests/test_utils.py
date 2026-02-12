"""Tests pour le module utils."""

from datetime import date
from unittest.mock import patch, Mock

import pytest
import requests

from app.utils import week_label, notify_ntfy, extract_spoon_id_from_url


def test_week_label_default():
    """Test week_label avec date par défaut (aujourd'hui)."""
    result = week_label()
    assert isinstance(result, str)
    assert "Semaine" in result
    assert "–" in result or "-" in result


def test_week_label_specific_date():
    """Test week_label avec une date spécifique."""
    # Date connue : 2024-01-15 est dans la semaine 3 de 2024
    test_date = date(2024, 1, 15)
    result = week_label(test_date)
    assert "Semaine" in result
    assert "2024" in result


def test_week_label_format():
    """Test que le format est correct."""
    test_date = date(2024, 1, 15)
    result = week_label(test_date)
    # Format attendu : "Semaine {week} – {year}"
    parts = result.split(" – ")
    assert len(parts) == 2
    assert parts[0].startswith("Semaine")
    assert parts[1].isdigit()


@patch('app.utils.requests.post')
@patch('app.utils.NTFY_TOPIC', 'test-topic')
def test_notify_ntfy_success(mock_post):
    """Test notification ntfy réussie."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    
    notify_ntfy("Test Title", "Test Body")
    
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "ntfy.sh/test-topic" in call_args[0][0]
    assert call_args[1]["headers"]["Title"] == "Test Title"
    assert call_args[1]["data"] == b"Test Body"


@patch('app.utils.requests.post')
@patch('app.utils.NTFY_TOPIC', 'test-topic')
def test_notify_ntfy_error(mock_post):
    """Test notification ntfy avec erreur."""
    mock_post.side_effect = requests.RequestException("Network error")
    
    # Ne doit pas lever d'exception
    notify_ntfy("Test Title", "Test Body")
    
    mock_post.assert_called_once()


def test_extract_spoon_id_from_url_standard():
    """Test extraction ID depuis URL standard."""
    url = "https://spoonacular.com/recipes/123456"
    result = extract_spoon_id_from_url(url)
    assert result == 123456


def test_extract_spoon_id_from_url_with_params():
    """Test extraction ID depuis URL avec paramètres."""
    url = "https://spoonacular.com/recipes/789012?foo=bar"
    result = extract_spoon_id_from_url(url)
    assert result == 789012


def test_extract_spoon_id_from_url_query_param():
    """Test extraction ID depuis paramètre de requête."""
    url = "https://example.com/recipe?id=456789"
    result = extract_spoon_id_from_url(url)
    assert result == 456789


def test_extract_spoon_id_from_url_no_match():
    """Test extraction ID quand aucun ID trouvé."""
    url = "https://example.com/recipe"
    result = extract_spoon_id_from_url(url)
    assert result is None


def test_extract_spoon_id_from_url_empty():
    """Test extraction ID avec URL vide."""
    result = extract_spoon_id_from_url("")
    assert result is None


def test_extract_spoon_id_from_url_none():
    """Test extraction ID avec None."""
    result = extract_spoon_id_from_url(None)
    assert result is None

