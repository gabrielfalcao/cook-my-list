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
    record_mode="new_episodes",
)


def prepare_client(context):
    sql.context.set_default_uri(sql.config.SQLALCHEMY_URI)
    context.client = TudoGostosoClient()


def disconnect_client(context):
    context.client.close()


with_client = scenario(prepare_client, disconnect_client)

# TODO:
# - https://tudogostoso.com.br/receita/137721-molho-verde-delicioso-para-churrasco.html - missing picture
# - https://www.tudogostoso.com.br/receita/2649-torta-de-abacaxi.html - missing ingredient and video
# - https://www.tudogostoso.com.br/receita/2525-panetone-de-doce-de-leite.html
# - https://www.tudogostoso.com.br/receita/2442-aperitivo-de-caranguejo.html
# - https://www.tudogostoso.com.br/receita/2320-pao-de-panela-de-pressao.html
# - https://www.tudogostoso.com.br/receita/2278-bolo-de-sorvete-caseiro.html


@vcr.use_cassette
@with_client
def test_recipe_with_h3_for_direction_steps(context):
    "TudoGostosoClient.get_recipe() with a recipe that uses <h3> for direction titles"

    # Given that I request a single recipe
    recipe = context.client.get_recipe(
        "https://www.tudogostoso.com.br/receita/235-mousse-tentacao.html"
    )

    recipe.servings.should.equal("20 porções")
    recipe.servings_value.should.equal(Decimal("20"))
    recipe.servings_unit.should.equal("porções")
    recipe.total_cooking_time.should.equal("120 min")
    recipe.total_cooking_time_value.should.equal(Decimal(120))
    recipe.total_cooking_time_unit.should.equal("min")
    recipe.ingredients.should.have.length_of(6)
    recipe.directions.should.have.length_of(4)

    ingredients = [i.to_dict() for i in recipe.ingredients]
    ingredients.should.equal(
        [
            {
                "step": "Mousse tentação",
                "name": "1/2 garrafa de suco concentrado de maracujá",
            },
            {"step": "Mousse tentação", "name": "3 latas leite moça"},
            {"step": "Mousse tentação", "name": "4 latas creme de leite"},
            {"step": "Mousse tentação", "name": "2 caixas de brigadeirão"},
            {"step": "Mousse tentação", "name": "2 colheres de maisena"},
            {"step": "Mousse tentação", "name": "1 litro de leite"},
        ]
    )
    directions = [i.to_dict() for i in recipe.directions]
    directions.should.equal(
        [
            {
                "step": "Mousse de maracujá",
                "name": "Junte 2 leite moça, 2 creme de leite e o suco de maracujá, bata tudo no liquidificador, e reserve.",
            },
            {
                "step": "Mousse de chocolate",
                "name": "Leve o leite para esquentar, junte 1 leite moça, 2 colheres de maisena, e as caixas de pudim com um pouco de leite e misture com o leite quase fervido.",
            },
            {
                "step": "Mousse de chocolate",
                "name": "Mexa sempre até engrossar, quando estiver frio, bata na batedeira com os 2 creme de leite, e reserve.",
            },
            {
                "step": "Montagem",
                "name": "Faça camadas com os dois mousses, enfeite com sementes de maracujá ou raspas de chocolate, sirva gelado.",
            },
        ]
    )


@vcr.use_cassette
@with_client
def test_recipe_with_links_in_directions(context):
    "TudoGostosoClient.get_recipe() with a recipe that contains <a> for direction step"

    # Given that I request a single recipe
    recipe = context.client.get_recipe(
        "https://www.tudogostoso.com.br/receita/125-cuca-da-tia-dalila.html"
    )
    # TODO: Fix parsing of ingredients and directions that contain links
    recipe.ingredients.should.have.length_of(10)
    recipe.directions.should.have.length_of(4)

    recipe.servings.should.equal("12 porções")
    recipe.servings_value.should.equal(Decimal("12"))
    recipe.servings_unit.should.equal("porções")
    recipe.total_cooking_time.should.equal("60 min")
    recipe.total_cooking_time_value.should.equal(Decimal(60))
    recipe.total_cooking_time_unit.should.equal("min")
    recipe.ingredients.should.have.length_of(10)
    recipe.directions.should.have.length_of(4)

    ingredients = [i.to_dict() for i in recipe.ingredients]
    ingredients.should.equal(
        [
            {"step": "Cuca da tia Dalila", "name": "4 xícaras de farinha de trigo"},
            {"step": "Cuca da tia Dalila", "name": "2 xícaras de açúcar"},
            {"step": "Cuca da tia Dalila", "name": "1 xícara de leite"},
            {"step": "Cuca da tia Dalila", "name": "4 ovos"},
            {"step": "Cuca da tia Dalila", "name": "2 colheres (sopa) de"},
            {"step": "Cuca da tia Dalila", "name": "2 colheres (sopa)"},
            {"step": "Farofa", "name": "1 xícara de açúcar"},
            {"step": "Farofa", "name": "1/2 xícara de farinha de trigo"},
            {"step": "Farofa", "name": "canela em pó"},
            {"step": "Farofa", "name": "1 ou 2 colheres de"},
        ]
    )
    directions = [i.to_dict() for i in recipe.directions]
    directions.should.equal(
        [
            {
                "step": "Cuca da tia Dalila",
                "name": "Bata os ovos com o açúcar e misture os outros ingredientes até formar uma massa homogênea.",
            },
            {
                "step": "Cuca da tia Dalila",
                "name": "Para a farofa: basta colocar tudo em uma tigelona e amassar até ficar com cara de farofa.",
            },
            {"step": "Cuca da tia Dalila", "name": "Unte uma forma com margarina"},
            {
                "step": "Cuca da tia Dalila",
                "name": "Leve ao forno preaquecido para assar por aproximadamente 40 minutos.",
            },
        ]
    )


@vcr.use_cassette
@with_client
def test_recipe_with_h3_for_ingredient_steps(context):
    "TudoGostosoClient.get_recipe() with a recipe that uses <h3> for ingredient titles"

    # Given that I request a single recipe
    recipe = context.client.get_recipe(
        "https://www.tudogostoso.com.br/receita/17-torta-alema-de-maca.html"
    )

    recipe.ingredients.should.have.length_of(8)
    recipe.directions.should.have.length_of(2)
    ingredients = [i.to_dict() for i in recipe.ingredients]
    ingredients.should.equal(
        [
            {"step": "MASSA", "name": "300 gr de farinha"},
            {"step": "MASSA", "name": "200 gr de manteiga"},
            {"step": "MASSA", "name": "100 gr de açúcar"},
            {"step": "MASSA", "name": "1 gema"},
            {"step": "MASSA", "name": "1 colher (sopa) de vinho tinto"},
            {"step": "RECHEIO", "name": "6 maçãs vermelhas ácidas (1kg)"},
            {"step": "RECHEIO", "name": "1 colher (sopa) de vinho tinto"},
            {"step": "RECHEIO", "name": "100 gr de uva passa branca sem semente"},
        ]
    )
    directions = [i.to_dict() for i in recipe.directions]
    directions.should.equal(
        [
            {
                "step": "MASSA",
                "name": "Misture bem a manteiga com o açúcar, junte a gema e acrescente o vinho. Adicione a farinha e amasse até obter uma massa homogênea, mas gordurosa e pegajosa. Divida a massa em duas porções na proporção 2/3 e 1/3. Leve à geladeira, por ½ hora.",
            },
            {
                "step": "RECHEIO",
                "name": "Descasque as maçãs e corte em fatias médias. Misture as maçãs, o vinho e a uva-passa. Cozinhe no vapor até amolecer. Forre o fundo e as laterais de uma forma desmontável com os 2/3 da massa. Coloque o recheio. Com o restante da massa, faça rolinhos bem finos e monte uma grade sobre o recheio. Asse, em forno médio, até a massa estar dourada.",
            },
        ]
    )


@vcr.use_cassette
@with_client
def test_recipe_without_steps(context):
    "TudoGostosoClient.get_recipe() with a recipe without steps"

    # Given that I request a single recipe
    recipe = context.client.get_recipe(
        "https://www.tudogostoso.com.br/receita/1542-peras-ao-vinho.html"
    )

    # Then it should return a Recipe
    recipe.should.be.a(Recipe)

    # And it should have an id and url
    recipe.id.should.equal("1542")
    recipe.url.should.equal(
        "https://www.tudogostoso.com.br/receita/1542-peras-ao-vinho.html"
    )
    recipe.title.should.equal("Pêras ao vinho")
    recipe.ingredients.should.have.length_of(4)
    recipe.directions.should.have.length_of(1)


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
