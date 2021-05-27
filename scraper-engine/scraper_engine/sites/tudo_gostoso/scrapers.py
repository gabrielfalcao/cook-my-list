import re
from requests import Response
from urllib.parse import urlparse
from collections import defaultdict
from lxml import html

from datetime import datetime

from uiclasses import Model
from .models import Recipe, Ingredient

from scraper_engine.http.exceptions import ElementNotFound
from scraper_engine.http.exceptions import TooManyElementsFound

recipe_id_regex = re.compile(r"[/](?P<id>\d+)[-][^/]+")


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
            data["attributes"] = attributes

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

    def get_recipe_id(self):
        parsed = urlparse(self.url)
        found = recipe_id_regex.search(parsed.path)
        if not found:
            logger.warning(f"could not parse recipe id from {self.url}")
            return 0

        return found.group("id")

    def get_title(self):
        h1 = self.dom.query_one(".recipe-title h1")
        return h1.text.strip()

    def get_ingredients(self):
        ul = self.dom.query_one(".ingredients-card ul")
        ingredients = Ingredient.List([])
        current_step = None
        index = 0
        for li in ul.getchildren():
            strong = li.query_one("strong")
            if strong:
                # remove trailing colon (e.g.: "Molho:" becomes "Molho")
                current_step = strong.text.rstrip(":")
                continue
            paragraph = li.query_one("p")
            if paragraph:
                ingredients.append(
                    Ingredient(
                        step=current_step,
                        name=paragraph.text,
                    )
                )

        return ingredients

    def get_recipe(self) -> Recipe:
        data = {
            "id": self.get_recipe_id(),
            "title": self.get_title(),
            "url": self.url,
            "ingredients": self.get_ingredients(),
        }
        return Recipe(**data)
