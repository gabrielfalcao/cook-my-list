from decimal import Decimal
from typing import List, Optional

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from scraper_engine.sql.models import ScrapedRecipe

app = FastAPI()


class Ingredient(BaseModel):
    name: Optional[str]
    step: Optional[str]


class Direction(BaseModel):
    description: Optional[str]
    step: Optional[str]


class Picture(BaseModel):
    description: Optional[str]
    url: Optional[str]
    width: Optional[int]
    height: Optional[int]


class Recipe(BaseModel):
    id: str
    url: str
    title: str

    author_name: Optional[str]
    total_cooking_time: Optional[str]
    total_cooking_time_value: Optional[Decimal]
    total_cooking_time_unit: Optional[str]
    servings: Optional[str]
    servings_value: Optional[Decimal]
    servings_unit: Optional[str]

    ingredients: List[Ingredient]
    directions: List[Direction]
    pictures: List[Picture]

    total_ratings: Optional[int]
    rating: Optional[Decimal]


@app.get("/recipes/{recipe_id}", status_code=200, response_model=Recipe)
async def get_recipe_by_id(recipe_id: int) -> Optional[Recipe]:
    recipe = ScrapedRecipe.find_one_by(id=recipe_id)
    if recipe:
        return recipe.to_ui_dict()


@app.post("/recipes/", status_code=200, response_model=Recipe)
async def create_recipe(recipe: Recipe) -> Recipe:
    return recipe.dict()


@app.get("/recipes/", status_code=200, response_model=List[Recipe])
async def get_recipes(offset: int = 0, limit: int = 10) -> List[Recipe]:
    recipes = ScrapedRecipe.find_by(
        limit_by=limit,
        offset_by=offset,
        order_by="-id",
    )
    return [model.to_ui_dict() for model in recipes]


@app.get("/")
async def index():
    return RedirectResponse("/docs")
