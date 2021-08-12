from datetime import datetime
from decimal import Decimal
from itertools import chain
from typing import Optional, Union

from dateutil.parser import parse as parse_date
from defusedxml.lxml import RestrictedElement
from lxml import html
from scraper_engine import events
from scraper_engine.sql.models import ScrapedRecipe, ScrapedSiteMap
from uiclasses import Model
from uiclasses.typing import Property


def try_parse_date(value: str) -> Optional[datetime]:
    try:
        return parse_date(value)
    except Exception:
        return value


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

    author_name: str
    total_cooking_time: str
    total_cooking_time_value: Decimal
    total_cooking_time_unit: str
    servings: str
    servings_value: Decimal
    servings_unit: str

    ingredients: Ingredient.List
    directions: Direction.List
    pictures: Picture.List

    total_ratings: int
    rating: Decimal

    @classmethod
    def from_sql_model(cls, model: ScrapedRecipe):
        return cls(**model.to_ui_dict())

    def __ui_attributes__(self):
        return {
            "id": self.id,
            "title": self.title,
        }

    def to_sql_data(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "servings": self.servings,
            "servings_value": self.servings_value,
            "servings_unit": self.servings_unit,
            "author_name": self.author_name,
            "picture_count": len(self.pictures),
            "directions_count": len(self.directions),
            "ingredients_count": len(self.ingredients),
            "total_ratings": self.total_ratings,
            "rating": self.rating,
            "total_cooking_time": self.total_cooking_time,
            "total_cooking_time_value": self.total_cooking_time_value,
            "total_cooking_time_unit": self.total_cooking_time_unit,
            "json_data": self.to_json(),
        }

    def save(self) -> ScrapedRecipe:
        if not self.url or not self.title:
            logger.warning(
                f"cannot save recipe {self} because it does not have enough data"
            )
            return

        sql = ScrapedRecipe.get_or_create(url=self.url)
        data = self.to_sql_data()
        sql.update_and_save(updated_at=datetime.utcnow(), **data)
        return sql


class SiteMap(Model):
    url: str
    last_modified: datetime

    @classmethod
    def from_element(cls, element: RestrictedElement):
        lastmod = element.xpath("lastmod")
        loc = element.xpath("loc")
        url = len(loc) and loc[0].text.strip() or None
        last_modified = (
            len(lastmod)
            and try_parse_date(lastmod[0].text.strip())
            or datetime.utcnow().date()
        )
        return cls(url=url, last_modified=last_modified)

    def sql(self) -> Optional[ScrapedSiteMap]:
        if self.url:
            return ScrapedSiteMap.get_or_create(url=self.url)
