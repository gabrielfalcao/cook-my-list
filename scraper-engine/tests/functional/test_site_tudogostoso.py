import httpretty

from vcr import VCR
from sure import scenario
from pathlib import Path

from scraper_engine import sql
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient
from scraper_engine.sites.tudo_gostoso import Recipe, Ingredient


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


# @vcr.use_cassette
# @with_client
# def test_tudogostoso_get_empty_recipe(context):
#     "TudoGostosoClient.get_recipe() with a recipe pending submission"

#     # Given that I request the list of recipes
#     recipe = context.client.get_recipe(
#         "https://tudogostoso.com.br/receita/137721-molho-verde-delicioso-para-churrasco.html"
#     )

#     # Then it should return a Recipe
#     recipe.should.be.a(Recipe)

#     # And it should have an id and url
#     recipe.should.have.property("id").being.equal("137721")
#     recipe.should.have.property("url").being.equal(
#         "https://tudogostoso.com.br/receita/137721-molho-verde-delicioso-para-churrasco.html"
#     )


@vcr.use_cassette
@with_client
def test_tudogostoso_get_single_recipe(context):
    "TudoGostosoClient.get_recipe() with a basic recipe"

    # Given that I request the list of recipes
    recipe = context.client.get_recipe(
        "https://www.tudogostoso.com.br/receita/80799-almondega-ao-molho-de-tomate-rapida-pratica-e-gostosa.html"
    )

    # Then it should return a Recipe
    recipe.should.be.a(Recipe)

    # And it should have an id and url
    recipe.should.have.property("id").being.equal("80799")
    recipe.should.have.property("url").being.equal(
        "https://www.tudogostoso.com.br/receita/80799-almondega-ao-molho-de-tomate-rapida-pratica-e-gostosa.html"
    )
    recipe.title.should.equal(
        "Almôndega ao molho de tomate - rápida, prática e gostosa"
    )
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
