import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin

from requests import Response, Session

from scraper_engine import events
from scraper_engine.http.cache import DummyCache, HttpCache
from scraper_engine.http.exceptions import ClientError, invalid_response
from scraper_engine.logs import get_logger
from scraper_engine.version import version

logger = get_logger(__name__)


class HttpClient(object):
    def __init__(self, user_agent: str = "AdsBot-Google"):
        self.http = Session()
        self.user_agent = user_agent
        self.http.headers = {
            "User-Agent": user_agent,
        }
        self.cache = DummyCache()

    def request(
        self,
        method: str,
        url: str,
        data=None,
        headers=None,
        skip_cache: bool = False,
        **kwargs,
    ):
        headers = headers or {}
        if not skip_cache:
            interaction = self.cache.get_by_url_and_method(method=method, url=url)
            if interaction and interaction.response:
                return interaction.response()

        response = self.http.request(method, url, data=data, headers=headers, **kwargs)
        if response.status_code != 200:
            raise invalid_response(response)

        if skip_cache:
            return response

        interaction = self.cache.set(response.request, response)
        if not interaction:
            return response

        return interaction.response()

    def close(self):
        self.http.close()

    def __del__(self):
        self.close()
