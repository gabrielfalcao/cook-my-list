from scraper_engine.sites.tudo_gostoso import RecipeScraper, extract_image_size_from_url


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


def test_extract_image_size_from_url_ok():
    "extract_image_size_from_url() should work with a valid url"

    url = "https://img.itdg.com.br/tdg/images/recipes/000/080/799/86896/86896_original.jpg?mode=crop&width=710&height=400"

    result = extract_image_size_from_url(url)

    result.should.be.a(tuple)
    result.should.have.length_of(2)

    result.should.equal((710, 400))
