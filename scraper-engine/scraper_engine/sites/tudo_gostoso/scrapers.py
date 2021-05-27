import re
from typing import Tuple, Optional
from requests import Response
from functools import lru_cache
from decimal import Decimal
from urllib.parse import urlparse, parse_qsl
from collections import defaultdict
from lxml import html

from datetime import datetime

from uiclasses import Model
from .models import Recipe, Ingredient, Direction, Picture

from scraper_engine.logs import get_logger
from scraper_engine.http.exceptions import ElementNotFound
from scraper_engine.http.exceptions import TooManyElementsFound

recipe_id_regex = re.compile(r"[/](?P<id>\d+)[-][^/]+")


logger = get_logger(__name__)


class Element(Model):

    tag: str
    attributes: dict

    def __init__(self, dom):
        if isinstance(dom, Element):
            data = dom.to_dict()
            self.dom = dom.dom
        else:
            self.dom = dom
            data = dict(tag=dom.tag, attributes=dict(dom.attrib))

        super().__init__(**data)

    def __ui_attributes__(self):
        data = {
            "tag": self.tag,
        }
        if self.attributes:
            data["attributes"] = self.attributes

        return data

    def to_html(self) -> str:
        return str(html.tostring(self.dom), "utf-8")

    @property
    def text(self):
        if self.dom.text:
            return self.dom.text.strip()
        return self.dom.text

    @property
    def attrib(self):
        return self.dom.attrib

    def getchildren(self):
        return Element.List(map(Element, self.dom.getchildren()))

    def getprevious(self):
        element = self.dom.getprevious()
        if element is not None:
            return Element(element)

    def query_many(self, selector, fail: bool = False):
        found = self.dom.cssselect(selector)
        if not found and fail:
            raise ElementNotFound(f"{selector} in {self}")
        elif not found:
            return Element.List([])

        return Element.List(map(Element, found))

    def query_one(self, selector, fail: bool = False):
        found = self.query_many(selector, fail=fail)
        count = len(found)
        if count > 1 and fail:
            raise TooManyElementsFound(
                f"{count} elements matching {selector} in {self}"
            )

        if count > 0:
            return found[0]


class RecipeScraper(object):
    def __init__(self, url: str, response: Response):
        self.url = url
        self.response = response
        self.dom = Element(html.fromstring(response.text))

    @lru_cache()
    def get_recipe_id(self):
        parsed = urlparse(self.url)
        found = recipe_id_regex.search(parsed.path)
        if not found:
            logger.warning(f"could not parse recipe id from {self.url}")
            return 0

        return found.group("id")

    @lru_cache()
    def get_title(self):
        h1 = self.dom.query_one(".recipe-title h1")
        return h1.text.strip()

    def get_ingredients(self):
        ingredients = Ingredient.List([])
        current_step = self.get_title()

        for ol in self.dom.query_many(".ingredients-card ol") or self.dom.query_many(
            ".ingredients-card ul"
        ):
            h3 = ol.getprevious()
            if h3 and h3.text:
                # remove trailing colon (e.g.: "Molho:" becomes "Molho")
                current_step = h3.text.rstrip(":")

            index = 0
            for li in ol.getchildren():

                strong = li.query_one("strong")
                if strong:
                    # remove trailing colon (e.g.: "Molho:" becomes "Molho")
                    current_step = strong.text.rstrip(":")
                    continue
                paragraph = li.query_one("p") or li.query_one("span")
                if not paragraph.text:
                    logger.warning(
                        f"failed to parse ingredient from {paragraph.to_html()}"
                    )

                if paragraph:
                    ingredients.append(
                        Ingredient(
                            step=current_step,
                            name=paragraph.text,
                        )
                    )
        if len(ingredients) == 0:
            logger.warning(f"could not find ingredients in recipe {self.url}")

        return ingredients

    def get_directions(self):
        directions = Direction.List([])
        current_step = self.get_title()

        for ol in self.dom.query_many(".directions-card ol") or self.dom.query_many(
            ".directions-card ul"
        ):
            h3 = ol.getprevious()
            if h3 and h3.text:
                # remove trailing colon (e.g.: "Molho:" becomes "Molho")
                current_step = h3.text.rstrip(":")

            index = 0
            for li in ol.getchildren():
                strong = li.query_one("strong")
                if strong:
                    # remove trailing colon (e.g.: "Molho:" becomes "Molho")
                    current_step = strong.text.rstrip(":")
                    continue
                paragraph = li.query_one("p") or li.query_one("span")
                if not paragraph.text:
                    logger.warning(
                        f"failed to parse direction from {paragraph.to_html()}"
                    )

                if paragraph:
                    directions.append(
                        Direction(
                            step=current_step,
                            name=paragraph.text,
                        )
                    )
        if len(directions) == 0:
            logger.warning(f"could not find ingredients in recipe {self.url}")
        return directions

    def get_pictures(self):
        pictures = Picture.List([])
        for img in self.dom.query_many("picture img.pic"):
            url = img.attrib.get("src")
            width, height = extract_image_size_from_url(url)
            pictures.append(
                Picture(
                    description=img.attrib.get("alt"),
                    url=url,
                    width=width,
                    height=height,
                )
            )
        return pictures

    @lru_cache()
    def get_rating_tuple(self) -> Tuple[int, Decimal]:
        parts = [x.text for x in self.dom.query_many("#rating-average span")]
        if not parts:
            return -1, Decimal("-1")

        return int(parts[0]), Decimal(parts[-1])

    @lru_cache()
    def get_total_ratings(self) -> int:
        return self.get_rating_tuple()[0]

    @lru_cache()
    def get_rating(self) -> Decimal:
        return self.get_rating_tuple()[-1]

    def get_data_item(self, prop: str) -> str:
        element = self.dom.query_one(f'[itemprop="{prop}"]')
        if element:
            return re.sub(r"\s+", " ", element.text)

        return ""

    @lru_cache()
    def get_servings(self) -> str:
        return self.get_data_item("recipeYield")

    @lru_cache()
    def get_total_cooking_time(self) -> str:
        return self.get_data_item("totalTime").lower()

    @lru_cache()
    def get_author_name(self) -> str:
        return self.get_data_item("name")

    def get_recipe(self) -> Recipe:
        data = {
            "id": self.get_recipe_id(),
            "title": self.get_title(),
            "url": self.url,
            "ingredients": self.get_ingredients(),
            "directions": self.get_directions(),
            "pictures": self.get_pictures(),
            "total_ratings": self.get_total_ratings(),
            "rating": self.get_rating(),
            "servings": self.get_servings(),
            "total_cooking_time": self.get_total_cooking_time(),
            "author_name": self.get_author_name(),
        }
        return Recipe(**data)


def parse_url_params(url):
    result = urlparse(url)
    qsl = parse_qsl(result.query)
    return dict(qsl)


def try_int(value) -> int:
    try:
        return int(value)
    except ValueError:
        return -1


def extract_image_size_from_url(url):
    params = parse_url_params(url)
    width = try_int(params.get("width"))
    height = try_int(params.get("height"))
    return width, height
