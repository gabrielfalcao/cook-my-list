import os
import multiprocessing
from elasticsearch import Elasticsearch


hosts = [
    os.getenv("ELASTICSEARCH_HOST") or "localhost",
]


def connect_to_elasticsearch() -> Elasticsearch:
    return Elasticsearch(hosts, maxsize=multiprocessing.cpu_count())
