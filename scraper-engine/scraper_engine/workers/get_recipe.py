from datetime import datetime, timedelta

from scraper_engine.sql.models import ScrapedRecipe

from .puller import PullerWorker


class GetRecipeWorker(PullerWorker):
    __log_name__ = "recipe-scraper"

    async def process_job(self, info: dict):
        recipe_url = info.get("recipe_url")

        missing_fields = []

        if not recipe_url:
            missing_fields.append("recipe_url")

        if missing_fields:
            self.logger.error(f"missing fields: {missing_fields} in {info}")
            return

        await self.fetch_data(recipe_url)

    async def fetch_data(self, url: str):
        existing_recipe = ScrapedRecipe.find_one_by(url=url)
        some_time_ago = datetime.utcnow() - timedelta(days=1)
        if existing_recipe and existing_recipe.last_updated > some_time_ago:
            self.logger.info(
                f"skipping recipe {existing_recipe.id} already downloaded: {url}"
            )
            return

        try:
            self.logger.info(f"scraping recipe {url}")
            recipe = self.api.get_recipe(url)
        except Exception as e:
            self.logger.exception(f"failed to retrieve recipe {url}")
            return

        recipe.save()
        self.logger.info(f"saved recipe {recipe}")
