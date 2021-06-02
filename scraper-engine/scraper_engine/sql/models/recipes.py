import json
import io
import requests
from chemist import Model, db
from dateutil.parser import parse as parse_date
from datetime import datetime
from elasticsearch import Elasticsearch
from .base import metadata

es = Elasticsearch()


class ScrapedRecipe(Model):
    table = db.Table(
        "scraped_recipe",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("url", db.String(255), nullable=False, unique=True),
        db.Column("json_data", db.UnicodeText()),
        db.Column("title", db.Unicode(255), index=True),
        db.Column("servings", db.UnicodeText()),
        db.Column("servings_value", db.Numeric),
        db.Column("servings_unit", db.UnicodeText()),
        db.Column("total_cooking_time", db.Unicode(50), index=True),
        db.Column("total_cooking_time_value", db.Numeric),
        db.Column("total_cooking_time_unit", db.UnicodeText()),
        db.Column("author_name", db.UnicodeText()),
        db.Column("picture_count", db.Integer),
        db.Column("directions_count", db.Integer),
        db.Column("ingredients_count", db.Integer, index=True),
        db.Column("total_ratings", db.Integer),
        db.Column("rating", db.Numeric),
        db.Column("created_at", db.DateTime, default=datetime.utcnow),
        db.Column("updated_at", db.DateTime, default=datetime.utcnow),
    )

    def pre_save(self):
        self.updated_at = datetime.utcnow()

    def post_save(self):
        """called right after executing a save.
        This method can be overwritten by subclasses in order to take any domain-related action
        """
        data = self.to_ui_dict()
        data.update(self.to_dict())
        data.pop("json_data", None)
        es.index(index="recipes", id=self.id, body=data)

    def to_ui_dict(self):
        if self.json_data:
            return json.loads(self.json_data) or {}
        return {}

    @property
    def last_updated(self):
        return parse_date(self.updated_at)


class ScrapedSiteMap(Model):
    table = db.Table(
        "scraped_sitemap",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("url", db.String(255), nullable=False, unique=True),
        db.Column("last_modified", db.DateTime),
    )
