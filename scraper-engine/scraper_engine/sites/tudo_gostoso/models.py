from typing import Union, Optional
from itertools import chain
from uiclasses import Model
from uiclasses.typing import Property
from lxml import html

from datetime import datetime
from scraper_engine import events


class Ingredient(Model):

    name: str
    step: str


class Recipe(Model):
    __id_attributes__ = ["id", "url"]

    id: str
    url: str
    title: str

    ingredients: Ingredient.List

    def __ui_attributes__(self):
        return {
            "id": self.id,
            "title": self.title,
        }
