import logging
import socket
import time
from typing import Union
from urllib.parse import urlparse

import redis
from elasticsearch import Elasticsearch
from redis import ResponseError as RedisResponseError
from uiclasses import DataBag

from scraper_engine.config import config
from scraper_engine.exceptions import UserFriendlyException
from scraper_engine.util import (
    dict_of_strings,
    json_encode,
    load_json,
    slugify,
    unpacked_dict_of_strings,
)

logger = logging.getLogger(__name__)

BUILD_QUEUE_REDIS_KEY = "ci-butler:sortedset:build-info"
BUILD_MONITOR_REDIS_KEY = "ci-butler:sortedset:build-monitor"


def es_index_name_for_github_repo(owner: str, repo: str):
    owner = slugify(owner, "_")
    repo = slugify(repo, "_")
    return f"drone_builds_{owner}_{repo}"


def get_elasticsearch_hostname():
    return config.elasticsearch_host


def get_redis_hostname():
    return resolve_hostname(config.REDIS_HOST)


def resolve_hostname(hostname) -> str:
    try:
        return socket.gethostbyname(hostname)
    except Exception:
        logger.warning(f"could not resolve hostname {repr(hostname)}")
        return hostname


def resolve_zmq_address(address, listen=False) -> str:
    default = address

    parsed = urlparse(address)

    if parsed.scheme != "tcp":
        # prevent resolving inproc://name, etc
        return address

    items = parsed.netloc.split(":")
    port = None
    if len(items) == 2:
        hostname, port = items
    else:
        hostname = parsed.netloc

    if listen:
        host = "0.0.0.0"
    elif port:
        host = resolve_hostname(hostname)
    else:
        host = hostname

    netloc = host
    if port:
        netloc += f":{port}"

    return f"{parsed.scheme}://{netloc}"


def check_elasticsearch_is_reachable(verbose=True) -> bool:
    params = get_elasticsearch_params()
    params["verbose"] = verbose
    if check_tcp_can_connect(**params):
        return True

    if verbose:
        logger.error(f"Elasticsearch is not reachable via {params}")
    return False


def connect_to_elasticsearch(
    verbose=True,
    pool_size: int = config.elasticsearch_pool_size,
    check_reachability: bool = True,
) -> Elasticsearch:
    if check_reachability:
        reachable = check_elasticsearch_is_reachable(verbose=verbose)
        if not reachable:
            return None

    hosts = [get_elasticsearch_hostname()]
    return Elasticsearch(hosts, maxsize=pool_size)


def get_redis_params() -> dict:
    return {
        "host": get_redis_hostname(),
        "port": config.REDIS_PORT,
        "db": config.REDIS_DB,
    }


def get_elasticsearch_params():
    return {
        "host": get_elasticsearch_hostname(),
        "port": config.elasticsearch_port,
    }


def get_redis_pool() -> redis.ConnectionPool:
    params = get_redis_params()
    return redis.ConnectionPool(**params)


def check_redis_is_reachable(verbose=True) -> bool:
    params = get_redis_params()
    params["verbose"] = verbose
    if check_tcp_can_connect(**params):
        return True

    if verbose:
        logger.error(f"Redis is not reachable via {params}")
    return False


def connect_to_redis(pool=None, verbose=True, **kw) -> redis.StrictRedis:
    if isinstance(pool, redis.ConnectionPool):
        if verbose:
            logger.info(f"connecting to redis via pool {pool}")
        return redis.StrictRedis(connection_pool=pool)

    params = get_redis_params()
    params.update(kw)
    return redis.StrictRedis(**params)


def check_sqlalchemy_connection(engine, verbose=True):
    url = engine.url
    if verbose:
        logger.debug(f"Trying to connect to DB: {str(url)!r}")
    result = engine.connect()
    if verbose:
        logger.debug(f"SUCCESS: {url}")
    result.close()


def check_database_is_reachable(verbose=True) -> bool:
    return check_tcp_can_connect(
        config.database_hostname, config.database_port, verbose=verbose
    )


def check_tcp_can_connect(host: str, port: int, verbose=True, **kw) -> bool:
    hostname = host
    try:
        host = socket.gethostbyname(hostname)
        if verbose and host != hostname:
            logger.info(f"Check ability to resolve name {hostname!r} => {host!r}")
    except Exception as e:
        if verbose:
            logger.error(f"cannot resolve hostname {hostname!r}: {e}")

        return False

    if not port:
        if verbose:
            logger.error(
                f"cannot check tcp connection to {hostname} ({host}) because port was not provided {port}"
            )
        return False

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if verbose:
            logger.info(f"Checking TCP connection to {host}:{port}")
        sock.connect((host, port))
        return True
    except Exception as e:
        if verbose:
            logger.error(f"failed to connect to tcp address {host}:{port}")

    finally:
        sock.close()

    return False


class RedisQueueManager(object):
    def __init__(
        self,
        redis: redis.StrictRedis,
        name: str,
        group_name: str = "butler",
        verbose: bool = True,
    ):
        if not isinstance(name, str):
            raise UserFriendlyException(
                "missing `name` in RedisQueueManager constructor"
            )
        self.verbose = verbose
        self.streams = {}
        self.group_name = group_name
        self.name = name
        self.redis = redis
        self.logger = logging.getLogger(f"redis-streams")

    def consume_job(self, key: str, block_ms: int = 1000) -> dict:
        if isinstance(key, bytes):
            key = key.decode("utf-8")

        if not isinstance(key, str):
            raise UserFriendlyException(
                f"cannot call consume_job() with invalid key: {repr(key)}"
            )

        result = self.redis.zpopmin(key, 1)
        if not result:
            return {}

        data, score = result[0]
        return load_json(data)

    def add_job(self, key: str, job: dict, verbose: bool = False):
        verbose = verbose or self.verbose
        weight = time.time()
        if key == BUILD_MONITOR_REDIS_KEY:
            weight += 10000
        stream_id = self.redis.zadd(key, {json_encode(job): weight}, nx=True)
        if verbose:
            self.logger.info(
                f"added job to sorted set {key}: {stream_id}", extra=dict(job=job)
            )
        return stream_id

    def job_count(self, key: str, verbose: bool = False):
        verbose = verbose or self.verbose
        count = self.redis.zcard(key)
        if verbose:
            self.logger.info(f"job count {count} in sorted set {key}")
        return count

    def list_jobs(self, key: str):
        result = map(load_json, self.redis.zrange(key, 0, -1))
        return list(result)

    def close(self):
        self.redis.close()


class RedisJob(DataBag):
    def __init__(self, queue_name: str, job: Union[dict, int]):
        super().__init__(job)
        self.__queue_name__ = queue_name
        self.__build_number__ = self.job.get("build_number") or self.job.get("build_id")

    def allows_requeing(self):
        return self.__queue_name__ == BUILD_MONITOR_REDIS_KEY

    @property
    def build_number(self):
        return self.__build_number__
