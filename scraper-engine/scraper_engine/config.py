import logging
import multiprocessing
import sys
from pathlib import Path
from typing import Dict, Iterator, List
from urllib.parse import urlparse

import redis
import yaml
from sqlalchemy.engine.url import make_url
from uiclasses import DataBag, DataBagChild, UserFriendlyObject

from scraper_engine.exceptions import (
    ConfigMissing,
    InvalidYamlConfig,
    UserFriendlyException,
)
from scraper_engine.meta import BaseConfig, ConfigProperty
from scraper_engine.util import load_yaml, parse_bool

logger = logging.getLogger(__name__)

HOUR = 60 * 60
DAY = HOUR * 24
WEEK = DAY * 7
MONTH = WEEK * 4 + DAY * 2


class Config(BaseConfig):
    REDIS_HOST = ConfigProperty(
        "redis",
        "host",
        env="REDIS_HOST",
        default_value="localhost",
    )
    running_in_test_mode = ConfigProperty(
        "test-mode", "enabled", env="SCRAPER_ENGINE_TEST_MODE", deserialize=parse_bool
    )
    SESSION_FILE_DIR = ConfigProperty(
        "session",
        "file_dir",
        env="SESSION_FILE_DIR",
        default_value="/tmp/",
    )
    PREFERRED_URL_SCHEME = ConfigProperty(
        "web",
        "scheme",
        env="SCRAPER_ENGINE_URL_SCHEME",
        default_value="https",
    )
    REDIS_PORT = ConfigProperty(
        "redis",
        "port",
        env="REDIS_PORT",
        default_value=6379,
        deserialize=int,
    )
    REDIS_DB = ConfigProperty(
        "redis",
        "db",
        env="REDIS_DB",
        default_value=0,
        deserialize=int,
    )
    SECRET_KEY = ConfigProperty(
        "auth",
        "flask_secret",
        env="SECRET_KEY",
    )
    database_hostname = ConfigProperty(
        "postgres",
        "host",
        default_value="localhost",
        env="POSTGRES_HOST",
    )
    database_name = ConfigProperty(
        "postgres",
        "db",
        default_value="scraper_engine",
        env="POSTGRES_DB",
    )
    database_user = ConfigProperty(
        "postgres",
        "user",
        default_value="scraper_engine",
        env="POSTGRES_USER",
    )
    database_password = ConfigProperty(
        "postgres",
        "password",
        default_value="scraper_engine",
        env="POSTGRES_PASSWORD",
    )
    database_port = ConfigProperty(
        "postgres",
        "port",
        env="POSTGRES_PORT",
        default_value=5432,
        deserialize=int,
    )
    database_auth_method = ConfigProperty(
        "postgres",
        "host_auth_method",
        default_value="trust",
        env="POSTGRES_HOST_AUTH_METHOD",
    )
    drone_url = ConfigProperty(
        "drone",
        "server",
        env="DRONE_SERVER_URL",
    )
    drone_access_token = ConfigProperty(
        "drone",
        "access_token",
        env="DRONE_ACCESS_TOKEN",
    )

    auth_jwt_secret = ConfigProperty(
        "auth",
        "jwt_secret",
        env="SCRAPER_ENGINE_JWT_SECRET",
    )
    auth_token_timeout = ConfigProperty(
        "auth",
        "token_timeout",
        env="SCRAPER_ENGINE_TOKEN_TIMEOUT",
        default_value=1 * MONTH,
    )

    worker_queue_rep_address = ConfigProperty(
        "workers",
        "queue_rep_address",
        env="SCRAPER_ENGINE_QUEUE_REP_ADDRESS",
        default_value="tcp://127.0.0.1:5555",
    )

    worker_requeue_pending = ConfigProperty(
        "workers",
        "requeue_pending",
        env="SCRAPER_ENGINE_WORKER_REQUEUE_PENDING",
        default_value=True,
        deserialize=int,
    )

    worker_queue_pull_address = ConfigProperty(
        "workers",
        "queue_pull_address",
        env="SCRAPER_ENGINE_QUEUE_PULL_ADDRESS",
        default_value="tcp://127.0.0.1:6666",
    )
    worker_queue_push_address = ConfigProperty(
        "workers",
        "queue_push_address",
        env="SCRAPER_ENGINE_QUEUE_PUSH_ADDRESS",
        default_value="tcp://127.0.0.1:7777",
    )

    worker_monitor_address = ConfigProperty(
        "workers",
        "queue_monitor_address",
        env="SCRAPER_ENGINE_MONITOR_ADDRESS",
        default_value="tcp://127.0.0.1:7772",
    )

    web_host = ConfigProperty(
        "web",
        "hostname",
        env="SCRAPER_ENGINE_WEB_HOSTNAME",
        default_value="0.0.0.0",
    )
    web_port = ConfigProperty(
        "web",
        "port",
        env="SCRAPER_ENGINE_WEB_PORT",
        default_value=4000,
    )
    web_api_max_page_result = ConfigProperty(
        "web",
        "api",
        "max_page_results",
        default_value=20,
    )

    max_workers_per_process = ConfigProperty(
        "workers",
        "max_per_process",
        env="SCRAPER_ENGINE_MAX_GREENLETS_PER_PROCESS",
        default_value=multiprocessing.cpu_count(),
        deserialize=int,
    )

    drone_api_max_pages = ConfigProperty(
        "drone",
        "api",
        "max_pages",
        env="DRONE_API_MAX_PAGES",
        default_value=100000,
        deserialize=int,
    )
    drone_api_initial_page = ConfigProperty(
        "drone",
        "api",
        "initial_page",
        env="DRONE_API_INITIAL_PAGE",
        default_value=0,
        deserialize=int,
    )
    drone_api_max_builds = ConfigProperty(
        "drone",
        "api",
        "max_builds",
        env="DRONE_API_MAX_BUILDS",
        default_value=250000,
        deserialize=int,
    )
    elasticsearch_host = ConfigProperty(
        "elasticsearch",
        "host",
        env="SCRAPER_ENGINE_ELASTICSEARCH_HOST",
        default_value="localhost",
    )
    elasticsearch_port = ConfigProperty(
        "elasticsearch",
        "port",
        env="SCRAPER_ENGINE_ELASTICSEARCH_PORT",
        default_value=9200,
        deserialize=int,
    )
    elasticsearch_pool_size = ConfigProperty(
        "elasticsearch",
        "pool_size",
        env="SCRAPER_ENGINE_ELASTICSEARCH_POOL_SIZE",
        default_value=multiprocessing.cpu_count(),
        deserialize=int,
    )

    elastic_search_logs_index = ConfigProperty(
        "elasticsearch",
        "logs_index",
        env="SCRAPER_ENGINE_ELASTICSEARCH_LOGS_INDEX",
        default_value="scraper_engine_logs",
    )

    logging_level_default = ConfigProperty(
        "logging",
        "default_level",
        env="SCRAPER_ENGINE_DEFAULT_LOGLEVEL",
        default_value="DEBUG",
        deserialize=lambda x: str(x).upper(),
    )
    enable_json_logging = ConfigProperty(
        "logging",
        "enable_json",
        env="SCRAPER_ENGINE_ENABLE_JSON_LOGGING",
        deserialize=parse_bool,
    )
    enable_error_tracebacks = ConfigProperty(
        "logging",
        "error_tracebacks",
        env="SCRAPER_ENGINE_ENABLE_ERROR_TRACEBACKS",
        deserialize=parse_bool,
    )

    ngrok_auth_token = ConfigProperty(
        "ngrok",
        "auth_token",
        env="NGROK_AUTH",
    )

    http_cache_enabled = ConfigProperty(
        "cache",
        "http",
        "enabled",
        env="SCRAPER_ENGINE_HTTP_CACHE",
        deserialize=parse_bool,
    )

    web_client_url = ConfigProperty(
        "web",
        "client_url",
        env="SCRAPER_ENGINE_WEB_CLIENT_URL",
        default_value="http://localhost:3000/",
    )

    web_server_url = ConfigProperty(
        "web",
        "server_url",
        env="SCRAPER_ENGINE_WEB_SERVER_URL",
        default_value="http://localhost:4000/",
    )

    @property
    def in_dev_mode(self) -> bool:
        # this flag serves primarily as indication that the web server is running locally so that it serves the index html by proxying to the local webpack server
        return sys.platform == "darwin"

    def get_security_role(self, name: str) -> List[str]:
        users = self.traverse("auth", "roles", name)
        if not isinstance(users, list):
            raise InvalidYamlConfig(
                f"auth.roles should be a list of strings but instead got {repr(users)}"
            )
        return users

    @property
    def web_server_host(self):
        return urlparse(self.web_server_url).hostname

    @property
    def sqlalchemy_uri(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_hostname}:{self.database_port}/{self.database_name}"

    @property
    def SESSION_REDIS(self):
        if hasattr(self, "__session_redis__"):
            if isinstance(getattr(self, "__session_redis__"), redis.Redis):
                return getattr(self, "__session_redis__")

        if self.REDIS_HOST and self.REDIS_PORT:
            self.__session_redis__ = redis.Redis(
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                db=self.REDIS_DB,
            )
            return self.__session_redis__

    @property
    def SESSION_TYPE(self) -> str:
        if self.REDIS_HOST and self.REDIS_PORT:
            return "redis"
        else:
            return "filesystem"

    @property
    def logging_mapping(self) -> Dict[str, str]:

        try:
            mapping = dict(self.traverse("logging", "mapping") or {})
        except Exception as e:
            raise UserFriendlyException(
                f"Invalid logging mapping, not a dict: {repr(mapping)}"
            )

        if not isinstance(mapping, dict):
            raise UserFriendlyException(
                f"Invalid logging mapping, not a dict: {repr(mapping)}"
            )
            return {}

        return mapping


config = Config()
