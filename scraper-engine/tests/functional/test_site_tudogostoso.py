import httpretty

from vcr import VCR
from sure import scenario
from pathlib import Path
from decimal import Decimal

from scraper_engine import sql
from scraper_engine.sql.models import ScrapedRecipe
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient
from scraper_engine.sites.tudo_gostoso import (
    Recipe,
    Ingredient,
    Direction,
    Picture,
    SiteMap,
)


functional_tests_path = Path(__file__).parent.absolute()
vcr = VCR(
    cassette_library_dir=str(functional_tests_path.joinpath(".cassetes")),
    # record_mode="once",
)


def prepare_client(context):
    sql.context.set_default_uri("postgresql://scraper_engine@localhost/scraper_engine")
    context.client = TudoGostosoClient()


def disconnect_client(context):
    context.client.close()


with_client = scenario(prepare_client, disconnect_client)

# TODO:
# - recipe without pictures "https://tudogostoso.com.br/receita/137721-molho-verde-delicioso-para-churrasco.html"


@vcr.use_cassette
@with_client
def test_tudogostoso_get_single_recipe(context):
    "TudoGostosoClient.get_recipe() with a basic recipe"

    # Given that I request a single recipe
    recipe = context.client.get_recipe(
        "https://www.tudogostoso.com.br/receita/80799-almondega-ao-molho-de-tomate-rapida-pratica-e-gostosa.html"
    )

    # Then it should return a Recipe
    recipe.should.be.a(Recipe)

    # And it should have an id and url
    recipe.id.should.equal("80799")
    recipe.url.should.equal(
        "https://www.tudogostoso.com.br/receita/80799-almondega-ao-molho-de-tomate-rapida-pratica-e-gostosa.html"
    )
    recipe.title.should.equal(
        "Almôndega ao molho de tomate - rápida, prática e gostosa"
    )

    recipe.rating.should.equal(Decimal("4.5"))
    recipe.total_ratings.should.equal(200)

    recipe.total_cooking_time.should.equal("20 min")
    recipe.servings.should.equal("4 porções")
    recipe.author_name.should.equal("Carol Ariat")

    recipe.ingredients.should.be.an(Ingredient.List)
    recipe.ingredients.should.have.length_of(13)

    ingredients = [i.to_dict() for i in recipe.ingredients]
    ingredients.should.equal(
        [
            {"step": "Almôndega", "name": "500g de carne moída (coxão mole)"},
            {"step": "Almôndega", "name": "2 ovos"},
            {"step": "Almôndega", "name": "3 colheres (sopa) de farinha de rosca"},
            {"step": "Almôndega", "name": "1/2 cebola picada"},
            {"step": "Almôndega", "name": "sal e pimenta a gosto"},
            {"step": "Molho", "name": "1/2 cebola picada"},
            {"step": "Molho", "name": "1/2 alho picado"},
            {"step": "Molho", "name": "3 colheres (sopa) óleo"},
            {"step": "Molho", "name": "1 lata de molho de tomate"},
            {"step": "Molho", "name": "1/2 lata de água"},
            {"step": "Molho", "name": "1 cubo de caldo de galinha"},
            {"step": "Molho", "name": "1 pitada de açúcar"},
            {"step": "Molho", "name": "sal, pimenta, salsinha a gosto"},
        ]
    )

    recipe.directions.should.be.an(Direction.List)
    recipe.directions.should.have.length_of(8)

    directions = [i.to_dict() for i in recipe.directions]
    directions.should.equal(
        [
            {
                "step": "Almôndegas",
                "name": "Junte todos os ingredientes em uma vasilha e misture bem.",
            },
            {
                "step": "Almôndegas",
                "name": "Pegue uma colher de sobremesa como medida e faça as bolinhas (rende em torno de umas 45 unidades).",
            },
            {
                "step": "Almôndegas",
                "name": "Esquente uma panela com 2 a 3 dedos de óleo e frite as almôndegas até que fiquem levemente douradas (dentro poderá ficar crú, pois elas terminarão de cozinhar junto ao molho de tomate e ficarão mais suculentas).",
            },
            {"step": "Almôndegas", "name": "Reserve-as."},
            {"step": "Molho", "name": "Refogue a cebola e o alho no óleo."},
            {
                "step": "Molho",
                "name": "Junte o molho de tomate, a água, o caldo de galinha, os temperos a gosto e deixe ferventar em fogo médio.",
            },
            {
                "step": "Molho",
                "name": "Assim que o molho começar a borbulhar, junte as almôndegas (coloque também o caldinho que elas devem ter soltado no recipiente em que ficaram reservadas), tampe a panela e deixe em fogo baixo/médio por mais 5 minutos.",
            },
            {
                "step": "Molho",
                "name": "Coloque em um prato, decore com salsinha desidratada e bom apetite!",
            },
        ]
    )
    recipe.pictures.should.be.an(Picture.List)
    recipe.pictures.should.have.length_of(6)

    pictures = [i.to_dict() for i in recipe.pictures]
    pictures.should.equal(
        [
            {
                "description": "Imagem enviada por TudoGostoso",
                "url": "https://img.itdg.com.br/tdg/images/recipes/000/080/799/98762/98762_original.jpg?mode=crop&width=710&height=400",
                "width": 710,
                "height": 400,
            },
            {
                "description": "Imagem enviada por Thayna",
                "url": "https://img.itdg.com.br/tdg/images/recipes/000/080/799/92787/92787_original.jpg?mode=crop&width=710&height=400",
                "width": 710,
                "height": 400,
            },
            {
                "description": "Imagem enviada por Tiago Veras Falangola",
                "url": "https://img.itdg.com.br/tdg/images/recipes/000/080/799/86896/86896_original.jpg?mode=crop&width=710&height=400",
                "width": 710,
                "height": 400,
            },
            {
                "description": "Imagem enviada por Isabel Kede",
                "url": "https://img.itdg.com.br/tdg/images/recipes/000/080/799/60081/60081_original.jpg?mode=crop&width=710&height=400",
                "width": 710,
                "height": 400,
            },
            {
                "description": "Imagem enviada por Cíntia Aparecida de Souza",
                "url": "https://img.itdg.com.br/tdg/images/recipes/000/080/799/78053/78053_original.jpg?mode=crop&width=710&height=400",
                "width": 710,
                "height": 400,
            },
            {
                "description": "Imagem enviada por Isabel Kede",
                "url": "https://img.itdg.com.br/tdg/images/recipes/000/080/799/60080/60080_original.jpg?mode=crop&width=710&height=400",
                "width": 710,
                "height": 400,
            },
        ]
    )
    scraped = recipe.save()
    scraped.should.be.a(ScrapedRecipe)


@vcr.use_cassette
@with_client
def test_tudogostoso_get_recipe_urls_from_sitemap(context):
    "TudoGostosoClient.get_recipe_urls() from a valid sitemap url"

    # Given that I request the list of recipes
    recipe_urls = context.client.get_recipe_urls(
        "https://www.tudogostoso.com.br/sitemap-42.xml"
    )

    # When it should contain a list of strings with valid urls
    recipe_urls.should.have.length_of(2000)


@vcr.use_cassette
@with_client
def test_tudogostoso_get_sitemap(context):
    "TudoGostosoClient.get_sitemap() paginates"

    # Given that I get the root sitemap
    sitemaps = context.client.get_sitemap(max_pages=5)

    # Then it should return a list of urls
    sitemaps.should.be.a(SiteMap.List.Type)

    sitemaps.should.have.length_of(5)


@vcr.use_cassette
@with_client
def test_tudogostoso_crawl_sitemap(context):
    "TudoGostosoClient.crawl_sitemap() retrieves thousands of recipes"

    # Given that I crawl the root sitemap
    recipe_urls = context.client.crawl_sitemap(max_pages=5)

    # Then it should return a list of urls
    recipe_urls.should.be.a(list)
    recipe_urls.should.have.length_of(10_000)
