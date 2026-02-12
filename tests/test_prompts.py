"""Tests pour le chargement et versioning des prompts."""

import pytest

from app.llm import _load_prompt, get_prompt_version, PROMPT_VERSIONS


def test_load_prompt_exists():
    """Test chargement d'un prompt existant."""
    content = _load_prompt("choose_recipes.txt")
    assert isinstance(content, str)
    assert len(content) > 0


def test_load_prompt_not_found():
    """Test chargement d'un prompt inexistant."""
    with pytest.raises(FileNotFoundError):
        _load_prompt("nonexistent.txt")


def test_get_prompt_version():
    """Test récupération de la version d'un prompt."""
    version = get_prompt_version("choose_recipes.txt")
    assert version == "v1.0"
    
    version = get_prompt_version("deduplicate_courses.txt")
    assert version == "v1.0"


def test_get_prompt_version_unknown():
    """Test récupération de version pour prompt inconnu."""
    version = get_prompt_version("unknown.txt")
    assert version == "unknown"


def test_all_prompts_versioned():
    """Test que tous les prompts sont versionnés."""
    prompt_files = [
        "choose_recipes.txt",
        "consolidate.txt",
        "deduplicate_courses.txt",
        "complete_quantities.txt",
    ]
    
    for prompt_file in prompt_files:
        assert prompt_file in PROMPT_VERSIONS
        version = get_prompt_version(prompt_file)
        assert version != "unknown"

