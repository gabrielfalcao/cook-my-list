import gevent
import zmq.green as zmq
from collections import defaultdict

from scraper_engine.logs import get_logger
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient

from .base import context


class PullerWorker(object):
    __log_name__ = "puller-worker"

    def __init__(
        self,
        pull_connect_address: str,
        worker_id: str,
        high_watermark: int = 1,
    ):
        self.logger = get_logger(f"{self.__log_name__}:{worker_id}")

        self.pull_connect_address = pull_connect_address
        self.should_run = True
        self.poller = zmq.Poller()
        self.queue = context.socket(zmq.PULL)
        self.queue.set_hwm(high_watermark)

        self.poller.register(self.queue, zmq.POLLIN)
        self.api = TudoGostosoClient()

    def handle_exception(self, e):
        self.logger.exception(f"{self.__class__.__name__} interrupted by error")

    def connect(self):
        self.logger.info(f"Connecting to pull address: {self.pull_connect_address}")
        self.queue.connect(self.pull_connect_address)

    def run(self):
        self.connect()
        self.logger.info(f"Starting worker")
        while self.should_run:
            try:
                self.loop_once()
            except Exception as e:
                self.handle_exception(e)
                break

    def loop_once(self):
        self.process_queue()

    def pull_queue(self):
        self.logger.debug(f"Waiting for job")
        socks = dict(self.poller.poll())
        if self.queue in socks and socks[self.queue] == zmq.POLLIN:
            return self.queue.recv_json()

    def process_queue(self):
        info = self.pull_queue()
        self.logger.debug(f"processing job")
        self.process_job(info)
