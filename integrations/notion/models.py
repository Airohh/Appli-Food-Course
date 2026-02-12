"""Modèles Pydantic pour les données Notion."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Recipe(BaseModel):
    """Modèle pour une recette."""

    name: str = Field(..., description="Nom de la recette")
    time_minutes: Optional[int] = Field(None, description="Temps de préparation en minutes")
    calories: Optional[float] = Field(None, description="Calories")
    protein: Optional[float] = Field(None, description="Protéines en grammes")
    image_url: Optional[str] = Field(None, description="URL de l'image")
    tags: List[str] = Field(default_factory=list, description="Tags (multi_select)")
    link: Optional[str] = Field(None, description="Lien vers la recette")
    ingredients_text: Optional[str] = Field(None, description="Texte des ingrédients")


class GroceryItem(BaseModel):
    """Modèle pour un article de course."""

    name: str = Field(..., description="Nom de l'article")
    unit: Optional[str] = Field(None, description="Unité (g, ml, pièces, etc.)")
    quantity_needed: Optional[float] = Field(None, description="Quantité nécessaire")
    category: Optional[str] = Field(None, description="Catégorie")
    to_buy: bool = Field(True, description="À acheter ?")
    recipes: Optional[str] = Field(None, description="Recettes qui utilisent cet ingrédient")


class MealPlanEntry(BaseModel):
    """Modèle pour une entrée de plan de repas."""

    model_config = ConfigDict(populate_by_name=True)
    
    meal_date: date = Field(..., description="Date du repas", alias="date")
    meal_type: str = Field(..., description="Type de repas (Petit-déjeuner/Déjeuner/Dîner)")
    recipe_name: str = Field(..., description="Nom de la recette")
    recipe_page_id: Optional[str] = Field(None, description="ID de la page recette dans Notion")
    portions: Optional[int] = Field(None, description="Nombre de portions")

