from blinker import signal
from requests import Request, Response
from humanfriendly.text import pluralize

from scraper_engine.logs import get_logger
from scraper_engine.sites.tudo_gostoso.models import Recipe
from scraper_engine.es import connect_to_elasticsearch

es = connect_to_elasticsearch()

http_cache_hit = signal("http-cache-hit")
http_cache_miss = signal("http-cache-miss")

get_recipe_info = signal("get-recipe-info")
get_recipes = signal("get-recipes")


logger = get_logger("system-events")


@http_cache_miss.connect
def log_cache_miss(cache, request: Request, response: Response):
    logger.debug(f"cache miss: {request} {response}")


@http_cache_hit.connect
def log_cache_hit(cache, request: Request, response: Response):
    logger.debug(f"cache hit: {request} {response}")


@get_recipes.connect
def log_get_recipes(client, limit: int, page: int, recipes: Recipe.List.Type):
    count = len(recipes)
    logger.debug(f'found {pluralize(count, "recipe")} for page={page} limit={limit}')


@get_recipe_info.connect
def log_get_recipe_info(client, recipe_id: int, recipe: Recipe):
    logger.debug(f"retrieved recipe {recipe_id} {recipe.link}")
