import logging
import colorlog
from cmreslogging.handlers import CMRESHandler
from .config import get_elasticsearch_hostname

# fmt = "%(asctime)s %(log_color)s%(levelname)s%(reset)s %(name)s %(message)s"
fmt = "%(log_color)s%(levelname)s%(blue)s %(name)s %(reset)s%(message)s"
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(fmt))  # , "%Y-%m-%d %H:%M:%S"))


eshandler = CMRESHandler(
    hosts=[{"host": get_elasticsearch_hostname(), "port": 9200}],
    auth_type=CMRESHandler.AuthType.NO_AUTH,
    es_index_name="logs_scraper_engine",
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = [handler, eshandler]


def get_logger(name=None):
    return logging.getLogger(name)


logger = get_logger("scraper_engine")
