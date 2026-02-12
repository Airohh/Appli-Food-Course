"""Tests pour le module config."""

from unittest.mock import patch

import pytest

from app import config


def test_from_db_file_with_dict():
    """Test récupération depuis dictionnaire _DATABASE_IDS."""
    with patch.object(config, '_DATABASE_IDS', {"test_db": "test_value"}):
        result = config._from_db_file(["TEST_DB"], index=None)
        assert result == "test_value"


def test_from_db_file_not_found():
    """Test quand la clé n'existe pas."""
    with patch.object(config, '_DATABASE_IDS', {}):
        result = config._from_db_file(["NONEXISTENT_KEY"], index=None)
        assert result == ""


def test_from_db_file_multiple_keys():
    """Test avec plusieurs clés possibles."""
    with patch.object(config, '_DATABASE_IDS', {"key2": "value2"}):
        result = config._from_db_file(["KEY1", "KEY2", "KEY3"], index=None)
        assert result == "value2"


def test_from_db_file_first_match():
    """Test que la première clé trouvée est utilisée."""
    with patch.object(config, '_DATABASE_IDS', {"key1": "value1", "key2": "value2"}):
        result = config._from_db_file(["KEY1", "KEY2"], index=None)
        assert result == "value1"  # KEY1 est trouvée en premier


def test_from_db_file_with_list():
    """Test récupération depuis liste _DATABASE_IDS avec index."""
    with patch.object(config, '_DATABASE_IDS', ["value0", "value1", "value2"]):
        result = config._from_db_file([], index=1)
        assert result == "value1"

