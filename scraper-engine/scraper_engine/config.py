import os
import socket


def get_elasticsearch_hostname():
    return resolve_hostname(os.getenv("ELASTICSEARCH_HOST") or "localhost")


def resolve_hostname(hostname, default="localhost") -> str:
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        logger.warning(
            f"could not resolve hostname {hostname}. Defaulting to {default}"
        )
        return default
