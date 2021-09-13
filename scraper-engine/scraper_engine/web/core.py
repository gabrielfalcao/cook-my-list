from decimal import Decimal
from typing import List, Optional

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from scraper_engine.sql.models import ScrapedRecipe

app = FastAPI()


class Ingredient(BaseModel):
    name: str
    step: str


class Direction(BaseModel):
    description: str
    step: str


class Picture(BaseModel):
    description: str
    url: str
    width: int
    height: int


class Recipe(BaseModel):
    id: str
    url: str
    title: str

    author_name: str
    total_cooking_time: str
    total_cooking_time_value: Decimal
    total_cooking_time_unit: str
    servings: str
    servings_value: Decimal
    servings_unit: str

    ingredients: List[Ingredient]
    directions: List[Direction]
    pictures: List[Picture]

    total_ratings: int
    rating: Decimal


@app.get("/recipes/{recipe_id}", status_code=200)
async def get_recipe_by_id(recipe_id: int):
    recipe = ScrapedRecipe.find_one_by(id=recipe_id)
    if recipe:
        return recipe.to_ui_dict()


@app.post("/recipes/", status_code=200)
async def create_recipe(recipe: Recipe):
    return recipe.dict()


@app.get("/recipes/", status_code=200)
async def get_recipes(offset: int = 0, limit: int = 10):
    recipes = ScrapedRecipe.find_by(
        limit_by=limit,
        offset_by=offset,
        order_by="-id",
    )
    return [model.to_ui_dict() for model in recipes]


@app.get("/")
async def index():
    return RedirectResponse("/docs")
