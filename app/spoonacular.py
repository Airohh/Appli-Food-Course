# Client pour l'API Spoonacular, avec mode mock si pas de clé API

from __future__ import annotations

from typing import Any, Dict, List

import requests

from .config import (
    DIET,
    MAX_READY_MIN,
    N_RECIPES_CANDIDATES,
    SPOONACULAR_API_KEY,
    SPOONACULAR_API_KEY2,
    SPOONACULAR_API_KEY3,
    USE_MOCK_DATA,
)
from .retry import retry_http


BASE_URL = "https://api.spoonacular.com"


class AllAPIKeysExhaustedError(RuntimeError):
    """Exception levée quand toutes les clés API Spoonacular ont épuisé leurs crédits."""
    pass


def complex_search(
    query: str | None = None,
    number: int = N_RECIPES_CANDIDATES,
    diet: str = DIET,
    max_ready_time: int = MAX_READY_MIN,
    api_key: str | None = None,
    offset: int = 0,
) -> Dict[str, Any]:
    # Appelle l'API Spoonacular pour chercher des recettes

    key_to_use = api_key or SPOONACULAR_API_KEY
    if not key_to_use:
        raise RuntimeError(
            "[ERROR] Aucune cle API Spoonacular disponible."
            " Configure SPOONACULAR_API_KEY dans ton .env."
        )

    params = {
        "apiKey": key_to_use,
        "addRecipeInformation": "true",
        "fillIngredients": "true",
        "addRecipeNutrition": "true",
        "instructionsRequired": "true",
        "number": number,
        "diet": diet,
        "maxReadyTime": max_ready_time,
        "sort": "popularity",
        "offset": offset,  # Pour avoir des recettes différentes à chaque fois
    }
    if query:
        params["query"] = query

    @retry_http(max_attempts=3, base_delay=1.0)
    def _make_request():
        return requests.get(f"{BASE_URL}/recipes/complexSearch", params=params, timeout=30)
    
    response = _make_request()

    if response.status_code == 402:
        # Plus de crédits, on essaie les clés de secours si elles existent
        if api_key is None or api_key == SPOONACULAR_API_KEY:
            # Si on était sur la 1ère clé (ou None), essayer la 2ème
            if SPOONACULAR_API_KEY2:
                print(f"   [WARN] Plus de crédits sur la clé 1, bascule vers la clé 2...")
                return complex_search(query=query, number=number, diet=diet, max_ready_time=max_ready_time, api_key=SPOONACULAR_API_KEY2)
            # Sinon, essayer la 3ème
            elif SPOONACULAR_API_KEY3:
                print(f"   [WARN] Plus de crédits sur la clé 1, bascule vers la clé 3...")
                return complex_search(query=query, number=number, diet=diet, max_ready_time=max_ready_time, api_key=SPOONACULAR_API_KEY3)
        elif api_key == SPOONACULAR_API_KEY2:
            # Si on était sur la 2ème clé, essayer la 3ème
            if SPOONACULAR_API_KEY3:
                print(f"   [WARN] Plus de crédits sur la clé 2, bascule vers la clé 3...")
                return complex_search(query=query, number=number, diet=diet, max_ready_time=max_ready_time, api_key=SPOONACULAR_API_KEY3)
        raise RuntimeError(
            "[ERROR] Erreur Spoonacular : quota atteint (402 Payment Required)."
            " Verifie ton abonnement ou change de cle API."
        )
    if response.status_code == 401:
        raise RuntimeError(
            "[ERROR] Erreur Spoonacular : cle API invalide ou absente (401 Unauthorized)."
            " Verifie SPOONACULAR_API_KEY dans ton .env."
        )

    response.raise_for_status()
    return response.json()


def normalize(recipe: Dict[str, Any]) -> Dict[str, Any]:
    # Simplifie une recette Spoonacular pour garder juste ce qu'on a besoin

    title = recipe.get("title", "Recette")
    ready_minutes = recipe.get("readyInMinutes")
    source_url = recipe.get("sourceUrl")
    image = recipe.get("image")
    servings = recipe.get("servings", 1)
    recipe_id = recipe.get("id")  # Préserver l'ID Spoonacular

    calories = proteins = carbs = fat = None
    for nutrient in recipe.get("nutrition", {}).get("nutrients", []):
        name = (nutrient.get("name") or "").lower()
        amount = nutrient.get("amount")
        if name == "calories":
            calories = amount
        elif name == "protein":
            proteins = amount
        elif name == "carbohydrates":
            carbs = amount
        elif name == "fat":
            fat = amount

    ingredients: List[Dict[str, Any]] = []
    for ingredient in recipe.get("extendedIngredients", []):
        name = ingredient.get("nameClean") or ingredient.get("name") or ""
        measures = ingredient.get("measures", {}).get("metric") or {}
        amount = measures.get("amount")
        unit = measures.get("unitShort") or measures.get("unit")
        ingredients.append(
            {
                "name": name.strip(),
                "amount": amount,
                "unit": unit,
            }
        )

    result = {
        "title": title,
        "readyMinutes": ready_minutes,
        "servings": servings,
        "sourceUrl": source_url,
        "image": image,
        "ingredients": ingredients,
        "nutrition": {
            "calories": calories,
            "protein": proteins,
            "carbs": carbs,
            "fat": fat,
        },
    }
    
    # Ajouter l'ID si présent
    if recipe_id is not None:
        result["id"] = recipe_id
    
    # Si sourceUrl est manquant mais qu'on a un ID, construire l'URL Spoonacular
    if not source_url and recipe_id:
        result["sourceUrl"] = f"https://spoonacular.com/recipes/{recipe_id}"
    
    # Si image est manquante mais qu'on a un ID, construire l'URL de l'image Spoonacular
    if not image and recipe_id:
        result["image"] = f"https://img.spoonacular.com/recipes-{recipe_id}-312x231.jpg"
    
    return result


def get_mock_recipes() -> List[Dict[str, Any]]:
    """Renvoie un jeu de recettes factices pour tester sans API."""

    mock_data = [
        {
            "id": 123456,
            "title": "Poulet grillé aux légumes",
            "readyInMinutes": 30,
            "servings": 4,
            "sourceUrl": "https://spoonacular.com/recipes/123456",
            "image": "https://img.spoonacular.com/recipes-123456-312x231.jpg",
            "extendedIngredients": [
                {
                    "name": "chicken breasts",
                    "nameClean": "chicken breast",
                    "measures": {"metric": {"amount": 500, "unitShort": "g"}},
                },
                {
                    "name": "olive oil",
                    "nameClean": "olive oil",
                    "measures": {"metric": {"amount": 2, "unitShort": "tbsp"}},
                },
                {
                    "name": "bell peppers",
                    "nameClean": "bell pepper",
                    "measures": {"metric": {"amount": 2, "unitShort": "pieces"}},
                },
                {
                    "name": "onion",
                    "nameClean": "onion",
                    "measures": {"metric": {"amount": 1, "unitShort": "medium"}},
                },
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 450},
                    {"name": "Protein", "amount": 45},
                    {"name": "Carbohydrates", "amount": 15},
                    {"name": "Fat", "amount": 20},
                ]
            },
        },
        {
            "id": 234567,
            "title": "Saumon aux asperges et riz",
            "readyInMinutes": 25,
            "servings": 2,
            "sourceUrl": "https://spoonacular.com/recipes/234567",
            "image": "https://img.spoonacular.com/recipes-234567-312x231.jpg",
            "extendedIngredients": [
                {
                    "name": "salmon",
                    "nameClean": "salmon",
                    "measures": {"metric": {"amount": 300, "unitShort": "g"}},
                },
                {
                    "name": "asparagus",
                    "nameClean": "asparagus",
                    "measures": {"metric": {"amount": 250, "unitShort": "g"}},
                },
                {
                    "name": "rice",
                    "nameClean": "rice",
                    "measures": {"metric": {"amount": 200, "unitShort": "g"}},
                },
                {
                    "name": "lemon",
                    "nameClean": "lemon",
                    "measures": {"metric": {"amount": 1, "unitShort": "piece"}},
                },
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 520},
                    {"name": "Protein", "amount": 38},
                    {"name": "Carbohydrates", "amount": 45},
                    {"name": "Fat", "amount": 18},
                ]
            },
        },
        {
            "id": 345678,
            "title": "Salade de quinoa et poulet",
            "readyInMinutes": 20,
            "servings": 3,
            "sourceUrl": "https://spoonacular.com/recipes/345678",
            "image": "https://img.spoonacular.com/recipes-345678-312x231.jpg",
            "extendedIngredients": [
                {
                    "name": "quinoa",
                    "nameClean": "quinoa",
                    "measures": {"metric": {"amount": 150, "unitShort": "g"}},
                },
                {
                    "name": "chicken breast",
                    "nameClean": "chicken breast",
                    "measures": {"metric": {"amount": 300, "unitShort": "g"}},
                },
                {
                    "name": "cucumber",
                    "nameClean": "cucumber",
                    "measures": {"metric": {"amount": 1, "unitShort": "medium"}},
                },
                {
                    "name": "tomatoes",
                    "nameClean": "tomato",
                    "measures": {"metric": {"amount": 200, "unitShort": "g"}},
                },
                {
                    "name": "feta cheese",
                    "nameClean": "feta cheese",
                    "measures": {"metric": {"amount": 100, "unitShort": "g"}},
                },
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 420},
                    {"name": "Protein", "amount": 35},
                    {"name": "Carbohydrates", "amount": 40},
                    {"name": "Fat", "amount": 12},
                ]
            },
        },
        {
            "id": 456789,
            "title": "Curry de légumes et pois chiches",
            "readyInMinutes": 35,
            "servings": 4,
            "sourceUrl": "https://spoonacular.com/recipes/456789",
            "image": "https://img.spoonacular.com/recipes-456789-312x231.jpg",
            "extendedIngredients": [
                {
                    "name": "chickpeas",
                    "nameClean": "chickpea",
                    "measures": {"metric": {"amount": 400, "unitShort": "g"}},
                },
                {
                    "name": "coconut milk",
                    "nameClean": "coconut milk",
                    "measures": {"metric": {"amount": 400, "unitShort": "ml"}},
                },
                {
                    "name": "curry powder",
                    "nameClean": "curry powder",
                    "measures": {"metric": {"amount": 2, "unitShort": "tbsp"}},
                },
                {
                    "name": "sweet potato",
                    "nameClean": "sweet potato",
                    "measures": {"metric": {"amount": 500, "unitShort": "g"}},
                },
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 380},
                    {"name": "Protein", "amount": 15},
                    {"name": "Carbohydrates", "amount": 55},
                    {"name": "Fat", "amount": 12},
                ]
            },
        },
        {
            "id": 567890,
            "title": "Omelette aux champignons",
            "readyInMinutes": 10,
            "servings": 2,
            "sourceUrl": "https://spoonacular.com/recipes/567890",
            "image": "https://img.spoonacular.com/recipes-567890-312x231.jpg",
            "extendedIngredients": [
                {
                    "name": "eggs",
                    "nameClean": "egg",
                    "measures": {"metric": {"amount": 4, "unitShort": "pieces"}},
                },
                {
                    "name": "mushrooms",
                    "nameClean": "mushroom",
                    "measures": {"metric": {"amount": 150, "unitShort": "g"}},
                },
                {
                    "name": "cheese",
                    "nameClean": "cheese",
                    "measures": {"metric": {"amount": 50, "unitShort": "g"}},
                },
                {
                    "name": "butter",
                    "nameClean": "butter",
                    "measures": {"metric": {"amount": 1, "unitShort": "tbsp"}},
                },
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 320},
                    {"name": "Protein", "amount": 22},
                    {"name": "Carbohydrates", "amount": 5},
                    {"name": "Fat", "amount": 22},
                ]
            },
        },
        {
            "id": 678901,
            "title": "Pâtes aux légumes et parmesan",
            "readyInMinutes": 15,
            "servings": 2,
            "sourceUrl": "https://spoonacular.com/recipes/678901",
            "image": "https://img.spoonacular.com/recipes-678901-312x231.jpg",
            "extendedIngredients": [
                {
                    "name": "pasta",
                    "nameClean": "pasta",
                    "measures": {"metric": {"amount": 200, "unitShort": "g"}},
                },
                {
                    "name": "zucchini",
                    "nameClean": "zucchini",
                    "measures": {"metric": {"amount": 2, "unitShort": "medium"}},
                },
                {
                    "name": "cherry tomatoes",
                    "nameClean": "cherry tomato",
                    "measures": {"metric": {"amount": 200, "unitShort": "g"}},
                },
                {
                    "name": "parmesan cheese",
                    "nameClean": "parmesan cheese",
                    "measures": {"metric": {"amount": 50, "unitShort": "g"}},
                },
                {
                    "name": "garlic",
                    "nameClean": "garlic",
                    "measures": {"metric": {"amount": 2, "unitShort": "cloves"}},
                },
            ],
            "nutrition": {
                "nutrients": [
                    {"name": "Calories", "amount": 480},
                    {"name": "Protein", "amount": 18},
                    {"name": "Carbohydrates", "amount": 65},
                    {"name": "Fat", "amount": 15},
                ]
            },
        },
    ]

    return [normalize(item) for item in mock_data]


def get_candidate_recipes(
    query: str | None = None,
    n_candidates: int | None = None,
    offset: int | None = None,
) -> List[Dict[str, Any]]:
    # Récupère des recettes, utilise les données mock si pas de clé API
    # offset: permet d'avoir des recettes différentes (basé sur la semaine par exemple)

    n = n_candidates or N_RECIPES_CANDIDATES
    
    # Si pas d'offset fourni, utiliser le numéro de semaine pour varier les recettes
    if offset is None:
        from datetime import date
        _, week_num, _ = date.today().isocalendar()
        offset = (week_num - 1) * n  # Offset basé sur la semaine

    if USE_MOCK_DATA:
        print("   Mode MOCK (données locales)")
        return get_mock_recipes()

    if not SPOONACULAR_API_KEY and not SPOONACULAR_API_KEY2 and not SPOONACULAR_API_KEY3:
        print("   (Pas de clé API, bascule en mode MOCK)")
        return get_mock_recipes()

    try:
        payload = complex_search(query=query, number=n, offset=offset)
        results = payload.get("results", [])
        print(f"   📊 API Spoonacular : {len(results)} recette(s) retournée(s) (demandé: {n})")
        normalized = [normalize(recipe) for recipe in results]
        # Vérifier que toutes les recettes ont une image
        for recipe in normalized:
            if not recipe.get("image"):
                print(f"   ⚠️  Recette '{recipe.get('title', 'Sans nom')}' sans image")
        return normalized
    except (RuntimeError, requests.RequestException) as exc:
        print(f"   [WARN] Erreur Spoonacular : {exc}")
        print("   [INFO] Bascule automatique vers le mode MOCK")
        return get_mock_recipes()


def get_mock_recipe_ingredients(spoon_id: int, desired_portions: int = 2) -> List[Dict[str, Any]] | None:
    """
    Récupère les ingrédients d'une recette MOCK par son ID.
    
    Returns:
        Liste d'ingrédients au format attendu, ou None si l'ID n'est pas un ID MOCK
    """
    # Récupérer les recettes MOCK
    mock_recipes = get_mock_recipes()
    
    # Trouver la recette avec cet ID
    for recipe in mock_recipes:
        if recipe.get("id") == spoon_id:
            # Récupérer les ingrédients depuis extendedIngredients (format original)
            # On doit reconstruire le format original car normalize() les transforme
            # Pour les MOCK, on va utiliser les données brutes
            mock_data = [
                {
                    "id": 123456,
                    "title": "Poulet grillé aux légumes",
                    "servings": 4,
                    "extendedIngredients": [
                        {"name": "chicken breasts", "nameClean": "chicken breast", "measures": {"metric": {"amount": 500, "unitShort": "g"}}, "aisle": "Meat", "originalString": "500g chicken breasts"},
                        {"name": "olive oil", "nameClean": "olive oil", "measures": {"metric": {"amount": 2, "unitShort": "tbsp"}}, "aisle": "Oil, Vinegar, Salad Dressing", "originalString": "2 tbsp olive oil"},
                        {"name": "bell peppers", "nameClean": "bell pepper", "measures": {"metric": {"amount": 2, "unitShort": "pieces"}}, "aisle": "Produce", "originalString": "2 bell peppers"},
                        {"name": "onion", "nameClean": "onion", "measures": {"metric": {"amount": 1, "unitShort": "medium"}}, "aisle": "Produce", "originalString": "1 medium onion"},
                    ],
                },
                {
                    "id": 234567,
                    "title": "Saumon aux asperges et riz",
                    "servings": 2,
                    "extendedIngredients": [
                        {"name": "salmon", "nameClean": "salmon", "measures": {"metric": {"amount": 300, "unitShort": "g"}}, "aisle": "Seafood", "originalString": "300g salmon"},
                        {"name": "asparagus", "nameClean": "asparagus", "measures": {"metric": {"amount": 250, "unitShort": "g"}}, "aisle": "Produce", "originalString": "250g asparagus"},
                        {"name": "rice", "nameClean": "rice", "measures": {"metric": {"amount": 200, "unitShort": "g"}}, "aisle": "Pasta and Rice", "originalString": "200g rice"},
                        {"name": "lemon", "nameClean": "lemon", "measures": {"metric": {"amount": 1, "unitShort": "piece"}}, "aisle": "Produce", "originalString": "1 lemon"},
                    ],
                },
                {
                    "id": 345678,
                    "title": "Salade de quinoa et poulet",
                    "servings": 3,
                    "extendedIngredients": [
                        {"name": "quinoa", "nameClean": "quinoa", "measures": {"metric": {"amount": 150, "unitShort": "g"}}, "aisle": "Pasta and Rice", "originalString": "150g quinoa"},
                        {"name": "chicken breast", "nameClean": "chicken breast", "measures": {"metric": {"amount": 300, "unitShort": "g"}}, "aisle": "Meat", "originalString": "300g chicken breast"},
                        {"name": "cucumber", "nameClean": "cucumber", "measures": {"metric": {"amount": 1, "unitShort": "medium"}}, "aisle": "Produce", "originalString": "1 medium cucumber"},
                        {"name": "tomatoes", "nameClean": "tomato", "measures": {"metric": {"amount": 200, "unitShort": "g"}}, "aisle": "Produce", "originalString": "200g tomatoes"},
                        {"name": "feta cheese", "nameClean": "feta cheese", "measures": {"metric": {"amount": 100, "unitShort": "g"}}, "aisle": "Cheese", "originalString": "100g feta cheese"},
                    ],
                },
                {
                    "id": 456789,
                    "title": "Curry de légumes et pois chiches",
                    "servings": 4,
                    "extendedIngredients": [
                        {"name": "chickpeas", "nameClean": "chickpea", "measures": {"metric": {"amount": 400, "unitShort": "g"}}, "aisle": "Canned and Jarred", "originalString": "400g chickpeas"},
                        {"name": "coconut milk", "nameClean": "coconut milk", "measures": {"metric": {"amount": 400, "unitShort": "ml"}}, "aisle": "Canned and Jarred", "originalString": "400ml coconut milk"},
                        {"name": "curry powder", "nameClean": "curry powder", "measures": {"metric": {"amount": 2, "unitShort": "tbsp"}}, "aisle": "Spices and Seasonings", "originalString": "2 tbsp curry powder"},
                        {"name": "sweet potato", "nameClean": "sweet potato", "measures": {"metric": {"amount": 500, "unitShort": "g"}}, "aisle": "Produce", "originalString": "500g sweet potato"},
                    ],
                },
                {
                    "id": 567890,
                    "title": "Omelette aux champignons",
                    "servings": 2,
                    "extendedIngredients": [
                        {"name": "eggs", "nameClean": "egg", "measures": {"metric": {"amount": 4, "unitShort": "pieces"}}, "aisle": "Milk, Eggs, Other Dairy", "originalString": "4 eggs"},
                        {"name": "mushrooms", "nameClean": "mushroom", "measures": {"metric": {"amount": 150, "unitShort": "g"}}, "aisle": "Produce", "originalString": "150g mushrooms"},
                        {"name": "cheese", "nameClean": "cheese", "measures": {"metric": {"amount": 50, "unitShort": "g"}}, "aisle": "Cheese", "originalString": "50g cheese"},
                        {"name": "butter", "nameClean": "butter", "measures": {"metric": {"amount": 1, "unitShort": "tbsp"}}, "aisle": "Milk, Eggs, Other Dairy", "originalString": "1 tbsp butter"},
                    ],
                },
                {
                    "id": 678901,
                    "title": "Pâtes aux légumes et parmesan",
                    "servings": 2,
                    "extendedIngredients": [
                        {"name": "pasta", "nameClean": "pasta", "measures": {"metric": {"amount": 200, "unitShort": "g"}}, "aisle": "Pasta and Rice", "originalString": "200g pasta"},
                        {"name": "zucchini", "nameClean": "zucchini", "measures": {"metric": {"amount": 2, "unitShort": "medium"}}, "aisle": "Produce", "originalString": "2 medium zucchini"},
                        {"name": "cherry tomatoes", "nameClean": "cherry tomato", "measures": {"metric": {"amount": 200, "unitShort": "g"}}, "aisle": "Produce", "originalString": "200g cherry tomatoes"},
                        {"name": "parmesan cheese", "nameClean": "parmesan cheese", "measures": {"metric": {"amount": 50, "unitShort": "g"}}, "aisle": "Cheese", "originalString": "50g parmesan cheese"},
                        {"name": "garlic", "nameClean": "garlic", "measures": {"metric": {"amount": 2, "unitShort": "cloves"}}, "aisle": "Produce", "originalString": "2 cloves garlic"},
                    ],
                },
            ]
            
            for mock_recipe in mock_data:
                if mock_recipe["id"] == spoon_id:
                    base_servings = mock_recipe.get("servings", 1)
                    multiplier = desired_portions / base_servings if base_servings > 0 else desired_portions
                    
                    ingredients = []
                    for ing in mock_recipe.get("extendedIngredients", []):
                        name = ing.get("nameClean") or ing.get("name") or ""
                        measures = ing.get("measures", {}).get("metric") or {}
                        amount = measures.get("amount", 0) * multiplier
                        unit = measures.get("unitShort") or measures.get("unit") or ""
                        aisle = ing.get("aisle", "Divers")
                        original_string = ing.get("originalString", name)
                        
                        ingredients.append({
                            "raw_name": original_string,
                            "name": name,
                            "amount": amount,
                            "unit": unit,
                            "aisle": aisle,
                            "recipe_id": spoon_id,
                            "recipe_title": mock_recipe.get("title", ""),
                        })
                    
                    return ingredients
    
    return None


def get_recipe_ingredients_with_quantities(
    spoon_id: int,
    portions_multiplier: float = 1.0,
    desired_portions: int | None = None
) -> List[Dict[str, Any]]:
    """
    Récupère les ingrédients d'une recette avec quantités depuis Spoonacular.
    
    Args:
        spoon_id: ID de la recette Spoonacular
        portions_multiplier: Multiplicateur pour les portions (défaut: 1.0)
                          Si desired_portions est fourni, ce paramètre est ignoré
        desired_portions: Nombre de portions désirées (optionnel)
                         Si fourni, calcule automatiquement le multiplicateur
                         en fonction des servings de base de la recette
    
    Returns:
        Liste d'ingrédients avec quantités multipliées
    """
    # Pour le 2ème script (génération des courses), on privilégie la clé 2 ou 3 si disponible
    # pour préserver la clé 1 pour le Widget 1
    if not SPOONACULAR_API_KEY and not SPOONACULAR_API_KEY2 and not SPOONACULAR_API_KEY3:
        raise RuntimeError(
            "[ERROR] Aucune clé API Spoonacular disponible."
            " Configure au moins une clé API dans ton .env."
        )
    
    # Priorité : Clé 2 > Clé 3 > Clé 1
    if SPOONACULAR_API_KEY2:
        key_to_use = SPOONACULAR_API_KEY2
        key_name = "clé 2"
    elif SPOONACULAR_API_KEY3:
        key_to_use = SPOONACULAR_API_KEY3
        key_name = "clé 3"
    else:
        key_to_use = SPOONACULAR_API_KEY
        key_name = "clé 1"
    
    url = f"{BASE_URL}/recipes/{spoon_id}/information"
    params = {
        "apiKey": key_to_use,
        "includeNutrition": "false",
    }
    
    @retry_http(max_attempts=3, base_delay=1.0)
    def _make_request():
        return requests.get(url, params=params, timeout=30)
    
    try:
        response = _make_request()
        
        if response.status_code == 402:
            # Plus de crédits, on essaie toutes les autres clés disponibles de manière systématique
            initial_key_name = key_name
            tried_keys = [key_to_use]
            all_keys = [
                ("clé 1", SPOONACULAR_API_KEY),
                ("clé 2", SPOONACULAR_API_KEY2),
                ("clé 3", SPOONACULAR_API_KEY3),
            ]
            
            # Lister les clés disponibles pour debug
            available_keys = [k[0] for k in all_keys if k[1]]
            print(f"   [INFO] Clés API disponibles : {', '.join(available_keys) if available_keys else 'aucune'}")
            
            # Essayer toutes les clés disponibles jusqu'à ce qu'une fonctionne
            for next_key_name, next_key_value in all_keys:
                if next_key_value and next_key_value not in tried_keys:
                    print(f"   [WARN] Plus de crédits sur la {key_name}, bascule vers la {next_key_name}...")
                    key_to_use = next_key_value
                    key_name = next_key_name
                    params["apiKey"] = key_to_use
                    response = _make_request()
                    tried_keys.append(key_to_use)
                    
                    # Si cette clé fonctionne, sortir de la boucle
                    if response.status_code != 402:
                        break
                    # Sinon, continuer avec la clé suivante
            
            # Si après tous les fallbacks on a toujours une erreur 402
            if response.status_code == 402:
                tried_key_names = [k[0] for k in all_keys if k[1] and k[1] in tried_keys]
                print(f"   [WARN] Toutes les clés API ont été essayées ({', '.join(tried_key_names)})")
                raise AllAPIKeysExhaustedError(
                    "[ERROR] Erreur Spoonacular : quota atteint (402 Payment Required) sur toutes les clés disponibles."
                    " Vérifie ton abonnement ou recharge tes crédits."
                )
        
        if response.status_code == 401:
            raise RuntimeError(
                f"[ERROR] Erreur Spoonacular : clé API invalide ou absente (401 Unauthorized) sur la {key_name}."
                " Vérifie tes clés API dans ton .env."
            )
        
        response.raise_for_status()
        recipe = response.json()
    except (RuntimeError, requests.RequestException) as exc:
        raise RuntimeError(f"Erreur lors de la récupération de la recette {spoon_id}: {exc}")
    
    # Calculer le multiplicateur correct
    if desired_portions is not None:
        # Si desired_portions est fourni, calculer le multiplicateur en fonction des servings de base
        base_servings = recipe.get("servings", 1)
        multiplier = desired_portions / base_servings if base_servings > 0 else desired_portions
    else:
        # Sinon, utiliser portions_multiplier directement
        multiplier = portions_multiplier
    
    ingredients = []
    for ing in recipe.get("extendedIngredients", []):
        name = ing.get("nameClean") or ing.get("name") or ""
        measures = ing.get("measures", {}).get("metric") or {}
        amount = measures.get("amount", 0) * multiplier
        unit = measures.get("unitShort") or measures.get("unit") or ""
        aisle = ing.get("aisle", "Divers")
        
        ingredients.append({
            "raw_name": ing.get("originalString", name),
            "name": name,
            "amount": amount,
            "unit": unit,
            "aisle": aisle,
            "recipe_id": spoon_id,
            "recipe_title": recipe.get("title", ""),
        })
    
    return ingredients

