import os
import socket
import multiprocessing
from elasticsearch import Elasticsearch


hosts = [
    socket.gethostbyname(
        os.getenv("ELASTICSEARCH_HOST") or "localhost",
    )
]


def connect_to_elasticsearch() -> Elasticsearch:
    return Elasticsearch(hosts, maxsize=multiprocessing.cpu_count())
