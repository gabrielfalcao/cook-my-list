from typing import List, Optional

from defusedxml.lxml import RestrictedElement
from lxml import html as xml
from scraper_engine.http.client import HttpClient
from scraper_engine.logs import get_logger

from .models import Recipe, SiteMap
from .scrapers import RecipeScraper

logger = get_logger("TudoGostosoClient")


class TudoGostosoClient(HttpClient):
    def get_recipe(self, url):
        response = self.request("GET", url)
        scraper = RecipeScraper(url, response)
        return scraper.get_recipe()

    def get_sitemap_element(self, sitemap_url, **kw) -> Optional[RestrictedElement]:
        logger.info(f"retrieving sitemap {sitemap_url}")
        try:
            response = self.request("GET", sitemap_url, **kw)
        except Exception:
            logger.exception(f"failed request {sitemap_url}")

        try:
            return xml.fromstring(bytes(response.text, "utf-8"))
        except Exception:
            logger.exception(f"failed to parse xml from url {sitemap_url}")

    def get_recipe_urls(self, sitemap_url: str, skip_cache: bool = True) -> List[str]:
        element = self.get_sitemap_element(sitemap_url, skip_cache=skip_cache)
        return [x.text.strip() for x in element.xpath("//url/loc") if x.text]

    def get_sitemap(self, max_pages=2) -> SiteMap.List:
        root_element = self.get_sitemap_element(
            "https://tudogostoso.com.br/sitemap.xml"
        )
        if len(root_element) == 0:
            return []

        items = []
        for i, element in enumerate(root_element.xpath("//sitemap")):
            if i == max_pages:
                break
            sitemap = SiteMap.from_element(element)
            items.append(sitemap)
        return SiteMap.List(items)

    def crawl_sitemap(self, max_pages: int = 2) -> List[str]:
        recipe_urls = []
        for sitemap in self.get_sitemap(max_pages=max_pages):
            recipe_urls.extend(self.get_recipe_urls(sitemap.url))

        return sorted(recipe_urls, reverse=True)
