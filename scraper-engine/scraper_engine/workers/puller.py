import asyncio
from collections import defaultdict

import zmq
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
        wait_timeout: int = 5,
    ):
        self.logger = get_logger(f"{self.__log_name__}:{worker_id}")

        self.pull_connect_address = pull_connect_address
        self.should_run = True
        self.wait_timeout = wait_timeout
        self.poller = zmq.asyncio.Poller()
        self.queue = context.socket(zmq.PULL)
        self.queue.set_hwm(high_watermark)

        self.poller.register(self.queue, zmq.POLLIN)
        self.api = TudoGostosoClient()

    def handle_exception(self, e):
        self.logger.exception(f"{self.__class__.__name__} interrupted by error")

    def connect(self):
        self.logger.info(f"Connecting to pull address: {self.pull_connect_address}")
        self.queue.connect(self.pull_connect_address)

    async def run(self):
        self.connect()
        self.logger.info(f"Starting worker")
        while self.should_run:
            try:
                await self.loop_once()
            except Exception as e:
                self.handle_exception(e)
                break

    async def loop_once(self):
        await self.process_queue()

    async def pull_queue(self):
        self.logger.debug(f"Waiting for job")
        socks = dict(await self.poller.poll(1000 * self.wait_timeout))
        if self.queue in socks and socks[self.queue] == zmq.POLLIN:
            return await self.queue.recv_json()

    async def process_queue(self):
        info = await self.pull_queue() or {}
        if not info:
            return

        self.logger.debug(f"processing job")
        try:
            await self.process_job(info)
        except Exception:
            self.logger.exception(f"failed to process job {info}")

    async def process_job(self, job):
        raise NotImplementedError
