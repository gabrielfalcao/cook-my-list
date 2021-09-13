import hashlib
import json
from typing import Dict, List, Optional, Union

import requests

from scraper_engine import events
from scraper_engine.sql import HttpInteraction


def hash_dict(data: dict, algo: callable) -> str:
    parts = list(filter(sorted(data.items(), lambda args: args[0]), bool))
    if not parts:
        return ""
    result = algo()
    for k, v in parts:
        result.update(f"{key}={value}")

    return result.hexdigest()


def generate_cache_key(
    url: str,
    method: str,
    json_body: str = None,
    params: dict = None,
    headers: dict = None,
    algo=hashlib.sha1,
):
    params = hash_dict(params or {}, algo)
    headers = hash_dict(headers or {}, algo)
    json_body = hash_dict(json_body or {}, algo)

    parts = [
        f"{key}={value}"
        for key, value in filter(
            [
                algo(method).hexdigest(),
                algo(url).hexdigest(),
                headers,
                params,
                json_body,
            ],
            bool,
        )
    ]

    return ".".join(parts)


class DummyCache(object):
    def get(self, request: requests.Request) -> Optional[HttpInteraction]:
        return None

    def get_by_url_and_method(self, url: str, method: str) -> Optional[HttpInteraction]:
        return None

    def set(
        self, request: requests.Request, response: requests.Response
    ) -> Optional[HttpInteraction]:
        return


class HttpCache(object):
    def get(self, request: requests.Request) -> Optional[HttpInteraction]:
        found = HttpInteraction.get_by_requests_request(request)
        if found:
            events.http_cache_hit.send(
                self, request=found.request(), response=found.response()
            )

        return found

    def get_by_url_and_method(self, url: str, method: str) -> Optional[HttpInteraction]:
        return HttpInteraction.get_by_url_and_method(url=url, method=method)

    def set(
        self, request: requests.Request, response: requests.Response
    ) -> Optional[HttpInteraction]:
        if request.method != "GET":
            return

        interaction = HttpInteraction.upsert(request, response)
        events.http_cache_miss.send(
            self, request=interaction.request(), response=interaction.response()
        )

        return interaction
