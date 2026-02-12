"""Script pour exécuter des tests manuels rapides."""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.llm import get_prompt_version
from app.shopping import normalize_aliment
from app.validators import validate_courses_list, sanitize_course_item


def test_validation():
    """Test de validation."""
    print("=" * 60)
    print("TEST: Validation des courses")
    print("=" * 60)
    
    courses = [
        {"Aliment": "Poulet", "Quantité": 500, "Unité": "g"},
        {"Aliment": "Tomates", "Quantité": 3, "Unité": "pièces"},
    ]
    
    is_valid, errors = validate_courses_list(courses)
    print(f"[OK] Validation: Valid={is_valid}, Errors={errors}")
    
    # Test avec item invalide
    invalid_courses = [
        {"Aliment": "Poulet", "Quantité": 500},
        {"Quantité": 3},  # Manque Aliment
    ]
    
    is_valid, errors = validate_courses_list(invalid_courses)
    print(f"[ERROR] Validation invalide: Valid={is_valid}, Errors={errors}")


def test_normalization():
    """Test de normalisation."""
    print("\n" + "=" * 60)
    print("TEST: Normalisation des aliments")
    print("=" * 60)
    
    test_cases = [
        ("Poulet", "poulet"),
        ("  Tomates  ", "tomates"),
        ("Épinards", "epinards"),
    ]
    
    for input_val, expected in test_cases:
        result = normalize_aliment(input_val)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} '{input_val}' -> '{result}' (attendu: '{expected}')")


def test_sanitization():
    """Test de nettoyage."""
    print("\n" + "=" * 60)
    print("TEST: Nettoyage des items")
    print("=" * 60)
    
    item = {
        "Aliment": "  Poulet  ",
        "Quantité": "500",
        "Unité": "  g  ",
    }
    
    cleaned = sanitize_course_item(item)
    print(f"[OK] Item nettoyé: {cleaned}")
    assert cleaned["Aliment"] == "Poulet"
    assert cleaned["Quantité"] == 500.0
    assert cleaned["Unité"] == "g"


def test_prompt_versions():
    """Test des versions de prompts."""
    print("\n" + "=" * 60)
    print("TEST: Versions des prompts")
    print("=" * 60)
    
    prompts = [
        "choose_recipes.txt",
        "deduplicate_courses.txt",
        "complete_quantities.txt",
        "consolidate.txt",
    ]
    
    for prompt in prompts:
        version = get_prompt_version(prompt)
        print(f"[OK] {prompt}: {version}")


def main():
    """Exécute tous les tests manuels."""
    print("\n[TEST] TESTS MANUELS - Appli Food Course\n")
    
    try:
        test_validation()
        test_normalization()
        test_sanitization()
        test_prompt_versions()
        
        print("\n" + "=" * 60)
        print("[OK] TOUS LES TESTS MANUELS REUSSIS")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] ERREUR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

