import os
import socket
import multiprocessing
from elasticsearch import Elasticsearch
from scraper_engine.logs import get_logger


logger = get_logger(__name__)


def get_elasticsearch_hostname():
    return os.getenv("ELASTICSEARCH_HOST") or "localhost"


def resolve_hostname(hostname, default="localhost") -> str:
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        logger.warning(
            f"could not resolve hostname {hostname}. Defaulting to {default}"
        )
        return default


def connect_to_elasticsearch() -> Elasticsearch:
    hosts = [resolve_hostname(get_elasticsearch_hostname())]
    return Elasticsearch(hosts, maxsize=multiprocessing.cpu_count())
