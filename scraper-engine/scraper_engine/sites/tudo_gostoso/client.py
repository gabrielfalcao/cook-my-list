from scraper_engine.logs import get_logger
from scraper_engine.http.client import HttpClient

from .models import Recipe
from .scrapers import RecipeScraper


logger = get_logger("TudoGostosoClient")


class TudoGostosoClient(HttpClient):
    def get_recipe(self, url):
        response = self.request("GET", url)
        scraper = RecipeScraper(url, response)
        return scraper.get_recipe()
