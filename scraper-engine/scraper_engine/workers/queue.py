import asyncio
import logging
import time
from collections import defaultdict

import zmq
import zmq.asyncio
from scraper_engine.logs import get_logger
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient

from .base import context

# QueueServer is inspired by
# https://zguide.zeromq.org/docs/chapter5/#High-Speed-Subscribers-Black-Box-Pattern
# except that it uses a REP socket instead of a subscriber socket,
# this way it can block clients from enqueueing more jobs that can be
# processed.


class QueueClient(object):
    __connected__ = False

    def __init__(
        self,
        rep_connect_address: str,
        rep_high_watermark: int = 1,
    ):
        self.logger = get_logger("queue-client")
        self.rep_connect_address = rep_connect_address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.set_hwm(rep_high_watermark)
        self.__connected__ = False

    def connect(self):
        self.logger.debug(f"connecting to {self.rep_connect_address}")
        self.socket.connect(self.rep_connect_address)
        self.__connected__ = True

    def close(self):
        self.__connected__ = False
        self.socket.disconnect(self.rep_connect_address)

    def send(self, job: dict):
        if not self.__connected__:
            raise RuntimeError(f"{self} is not connected")

        self.socket.send_json(job)
        response = self.socket.recv_json()
        self.logger.debug(f"{response}")
        return response

    def __del__(self):
        if self.__connected__:
            self.close()


class QueueServer(object):
    def __init__(
        self,
        rep_bind_address: str,
        push_bind_address: str,
        rep_high_watermark: int = 1,
        push_high_watermark: int = 1,
        sleep_timeout: float = 0.1,
        log_level: int = logging.WARNING,
    ):
        self.logger = get_logger("queue-server")
        self.log_level = log_level
        self.rep_bind_address = rep_bind_address
        self.push_bind_address = push_bind_address
        self.should_run = True
        self.sleep_timeout = sleep_timeout
        self.poller = zmq.asyncio.Poller()
        self.push = context.socket(zmq.PUSH)
        self.rep = context.socket(zmq.REP)
        self.poller.register(self.push, zmq.POLLOUT)
        self.poller.register(self.rep, zmq.POLLIN | zmq.POLLOUT)

        self.rep.set_hwm(rep_high_watermark)
        self.push.set_hwm(push_high_watermark)

    def handle_exception(self, e):
        self.logger.exception(f"{self.__class__.__name__} interrupted by error")

    def listen(self):
        self.logger.info(f"Listening on REP address: {self.rep_bind_address}")
        self.rep.bind(self.rep_bind_address)
        self.logger.info(f"Listening on PUSH address: {self.push_bind_address}")
        self.push.bind(self.push_bind_address)
        self.logger.setLevel(self.log_level)

    def disconnect(self):
        self.rep.disconnect(self.rep_bind_address)
        self.push.disconnect(self.push_bind_address)

    async def run(self):
        self.listen()
        self.logger.info(f"Starting {self.__class__.__name__}")
        while self.should_run:
            try:
                await self.loop_once()
                await asyncio.sleep(self.sleep_timeout)
            except Exception as e:
                self.handle_exception(e)
                break
        self.disconnect()

    async def loop_once(self):
        await self.process_queue()

    async def push_job(self, data: dict):
        self.logger.info(f"Waiting for socket to become available to push job")
        socks = dict(await self.poller.poll(1000 * self.sleep_timeout))
        if self.push in socks and socks[self.push] == zmq.POLLOUT:
            await self.push.send_json(data)
            return True

    async def handle_request(self):
        socks = dict(await self.poller.poll(1000 * self.sleep_timeout))
        if self.rep in socks and socks[self.rep] == zmq.POLLIN:
            data = await self.rep.recv_json()
            if data:
                await self.rep.send_json(data)
                return data

    async def process_queue(self):
        data = await self.handle_request()
        if not data:
            await asyncio.sleep(self.sleep_timeout)
            return
        self.logger.info(f"forwarding job {data}")
        await self.push_job(data)
