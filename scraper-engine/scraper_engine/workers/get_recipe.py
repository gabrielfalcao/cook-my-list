from .puller import PullerWorker


class GetRecipeWorker(PullerWorker):
    __log_name__ = "recipe-scraper"

    def process_job(self, info: dict):
        recipe_url = info.get("recipe_url")

        missing_fields = []

        if not recipe_url:
            missing_fields.append("recipe_url")

        if missing_fields:
            self.logger.error(f"missing fields: {missing_fields} in {info}")
            return

        self.fetch_data(recipe_url)

    def fetch_data(self, url: str):
        try:
            recipe = self.api.get_recipe(owner, repo, recipe_url)
        except Exception as e:
            self.logger.exception(
                f"failed to retrieve recipe {owner}/{repo} {recipe_url}"
            )
            return

        self.logger.info(f"retrieved recipe {recipe}")
