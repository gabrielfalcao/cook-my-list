import logging
import sys
from datetime import datetime

import colorlog

# from cmreslogging.handlers import CMRESHandler
from elasticsearch.exceptions import ElasticsearchWarning
from pythonjsonlogger import jsonlogger

from scraper_engine.config import config
from scraper_engine.networking import (
    check_elasticsearch_is_reachable,
    get_elasticsearch_params,
)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


CHATTY_LOGGER_NAMES = [
    "parso",
    "asyncio",
    "filelock",
    "requests",
    "urllib3",
    "elasticsearch",
    "werkzeug",
]

handler = logging.StreamHandler()

if not sys.stdout.isatty():
    handler.setFormatter(
        CustomJsonFormatter("%(message)s %(levelname)s %(name)s %(timestamp)s")
    )
else:
    # fmt = "%(asctime)s %(log_color)s%(levelname)s%(reset)s %(name)s %(message)s"
    fmt = "%(log_color)s%(levelname)s%(blue)s %(name)s %(reset)s%(message)s"
    handler.setFormatter(colorlog.ColoredFormatter(fmt))  # , "%Y-%m-%d %H:%M:%S"))


logger = logging.getLogger()

eshandler = None
# if (
#     not config.running_in_test_mode
#     and not config.in_dev_mode
#     and config.elasticsearch_host
#     and check_elasticsearch_is_reachable(verbose=False)
# ):
#     warnings.simplefilter("ignore", category=ElasticsearchWarning)
#     try:
#         eshandler = CMRESHandler(
#             hosts=[get_elasticsearch_params()],
#             auth_type=CMRESHandler.AuthType.NO_AUTH,
#             es_index_name=config.elastic_search_logs_index,
#         )
#         eshandler.setFormatter(jsonlogger.JsonFormatter())
#     except Exception:
#         pass


def get_default_level():
    return getattr(logging, config.logging_level_default, logging.DEBUG)


def silence_chatty_loggers(next_level=logging.WARNING):
    for name in CHATTY_LOGGER_NAMES:
        get_logger(name).setLevel(next_level)


def reset_level(target_level=config.logging_level_default):
    if target_level in dir(logging):
        level = getattr(logging, target_level)
    else:
        level = get_default_level()

    if eshandler:
        logger.handlers = [handler, eshandler]
    else:
        logger.handlers = [handler]

    logger.setLevel(level)
    silence_chatty_loggers()
    apply_mapping()


def apply_mapping():
    try:
        for logger_name, level_name in config.logging_mapping.items():
            logging.getLogger(logger_name).setLevel(
                getattr(logging, level_name, get_default_level())
            )
    except Exception as e:
        logger.exception(f"failed to map log levels to logger names: {e}")


def get_logger(name=None):
    return logging.getLogger(name)


get_logger("elasticsearch").setLevel(logging.WARNING)

reset_level()
logger = get_logger("scraper_engine")
