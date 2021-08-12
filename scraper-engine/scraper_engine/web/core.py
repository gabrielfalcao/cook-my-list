from decimal import Decimal
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

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
    return {"id": recipe_id}


@app.post("/recipes/", status_code=200)
async def create_recipe(recipe: Recipe):
    return recipe.dict()


@app.get("/recipes/", status_code=200)
async def get_recipes(skip: int = 0, limit: int = 10):
    return locals()
