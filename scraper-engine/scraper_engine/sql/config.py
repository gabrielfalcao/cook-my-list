import os

DEFAULT_SQLALCHEMY_URI = (
    "postgresql://scraper_engine:scraper_engine@localhost/scraper_engine"
)

SQLALCHEMY_URI = os.getenv("SQLALCHEMY_URI") or DEFAULT_SQLALCHEMY_URI
