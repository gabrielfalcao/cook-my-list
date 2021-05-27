from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

from scraper_engine.sql.models import ScrapedRecipe


app = Flask(__name__)
api = Api(app)


class RecipesList(Resource):
    def get(self):
        return [m.to_ui_dict() for m in ScrapedRecipe.all()]


api.add_resource(RecipesList, "/api/recipes")
