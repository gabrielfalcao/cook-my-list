import multiprocessing
from elasticsearch import Elasticsearch
from scraper_engine.logs import get_logger
from scraper_engine.config import get_elasticsearch_hostname

logger = get_logger(__name__)


def connect_to_elasticsearch() -> Elasticsearch:
    hosts = [get_elasticsearch_hostname()]
    return Elasticsearch(hosts, maxsize=multiprocessing.cpu_count())
