from scraper_engine.sites.tudo_gostoso import RecipeScraper


class ResponseStub(object):
    def __init__(self, text=None):
        self.text = text or "<html></html>"


def test_parse_recipe_id_from_path():
    "RecipeScraper.get_recipe_id() should extract recipe id from url"

    scraper = RecipeScraper(
        "https://tudogostoso.com.br/receita/137725-rondelli-quatro-queijos.html",
        ResponseStub(),
    )

    result = scraper.get_recipe_id()
    result.should.equal("137725")
