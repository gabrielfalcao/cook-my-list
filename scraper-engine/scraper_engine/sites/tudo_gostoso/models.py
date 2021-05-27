from typing import Union, Optional
from decimal import Decimal
from itertools import chain
from uiclasses import Model
from uiclasses.typing import Property
from lxml import html

from datetime import datetime
from scraper_engine import events


class Ingredient(Model):

    name: str
    step: str


class Direction(Model):

    description: str
    step: str


class Picture(Model):

    description: str
    url: str
    width: int
    height: int


class Recipe(Model):
    __id_attributes__ = ["id", "url"]

    id: str
    url: str
    title: str

    ingredients: Ingredient.List
    directions: Direction.List
    pictures: Picture.List

    total_ratings: int
    rating: Decimal

    def __ui_attributes__(self):
        return {
            "id": self.id,
            "title": self.title,
        }
