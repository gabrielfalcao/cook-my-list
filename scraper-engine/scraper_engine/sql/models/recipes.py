import json
import io
import requests
from chemist import Model, db
from dateutil.parser import parse as parse_date
from datetime import datetime
from .base import metadata


class ScrapedRecipe(Model):
    table = db.Table(
        "scraped_recipe",
        metadata,
        db.Column("id", db.Integer, primary_key=True),
        db.Column("url", db.String(255), nullable=False, unique=True),
        db.Column("json_data", db.UnicodeText()),
        db.Column("title", db.Unicode(255)),
        db.Column("servings", db.Unicode(50)),
        db.Column("total_cooking_time", db.Unicode(50)),
        db.Column("author_name", db.Unicode(50)),
        db.Column("picture_count", db.Integer),
        db.Column("directions_count", db.Integer),
        db.Column("ingredients_count", db.Integer),
        db.Column("total_ratings", db.Integer),
        db.Column("rating", db.Numeric),
        db.Column("created_at", db.DateTime, default=datetime.utcnow),
        db.Column("updated_at", db.DateTime, default=datetime.utcnow),
    )

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
