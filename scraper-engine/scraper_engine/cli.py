import asyncio
import json
import logging
import multiprocessing
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
import requests
import tqdm.asyncio
import uvicorn
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from uiclasses import Model

from scraper_engine import sql
from scraper_engine.config import config
from scraper_engine.logs import get_logger, logger
from scraper_engine.networking import (
    check_database_is_reachable,
    check_elasticsearch_is_reachable,
    check_redis_is_reachable,
    check_sqlalchemy_connection,
    connect_to_elasticsearch,
    connect_to_redis,
    RedisQueueManager,
)
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient
from scraper_engine.sites.tudo_gostoso.models import Recipe
from scraper_engine.web.core import app
from scraper_engine.workers import GetRecipeWorker, QueueClient, QueueServer

DEFAULT_QUEUE_ADDRESS = "tcp://127.0.0.1:5000"
DEFAULT_PUSH_ADDRESS = "tcp://127.0.0.1:6000"
DEFAULT_MAX_WORKERS = multiprocessing.cpu_count()
alembic_ini_path = Path(__file__).parent.joinpath("alembic.ini").absolute()


@click.group()
@click.pass_context
def main(ctx):
    print("Cook-My-List Scraper Engine")
    sql.context.set_default_uri(config.sqlalchemy_uri)
    ctx.obj = {}


@main.command("upgrade-db")
@click.option("--target", default="head")
@click.option("--alembic-ini", default=alembic_ini_path)
@click.option("--retry-seconds", type=int, default=0)
@click.pass_context
def upgrade_db(ctx, target, alembic_ini, retry_seconds):
    "runs the migrations"

    started = time.time()
    seconds_passed = time.time() - started
    if retry_seconds:
        while not check_database_is_reachable(verbose=True):
            seconds_passed = time.time() - started
            if seconds_passed < retry_seconds:
                logger.info("waiting for database server")
                time.sleep(1)
            else:
                break

    if not check_database_is_reachable(verbose=False):
        logger.error(f"cannot migrate db because database server is unreachable")
        raise SystemExit(1)

    sql.upgrade_db(config, target=target)
    ensure_known_github_users_exist()


@main.command("workers")
@click.option("-s", "--queue-address", default=DEFAULT_QUEUE_ADDRESS)
@click.option("-m", "--max-workers", default=DEFAULT_MAX_WORKERS, type=int)
@click.pass_context
def workers(ctx, queue_address, max_workers):
    async def main():
        loop = asyncio.get_event_loop()

        queue_server = QueueServer(queue_address, "inproc://recipe-info")

        tasks = [asyncio.create_task(queue_server.run())]
        for worker_id in range(max_workers):
            recipe_info_worker = GetRecipeWorker(
                "inproc://recipe-info", worker_id, **ctx.obj
            )
            tasks.append(asyncio.create_task(recipe_info_worker.run()))

        asyncio.gather(*tasks, loop=loop)

    asyncio.run(main())


@main.command("worker:get_recipe")
@click.option("-c", "--pull-connect-address", default=DEFAULT_PUSH_ADDRESS)
@click.pass_context
def worker_get_recipe(ctx, pull_connect_address):
    worker_id = "1"
    worker = GetRecipeWorker(pull_connect_address, worker_id)
    asyncio.run(worker.run())


@main.command("worker:queue")
@click.option("-s", "--rep-bind-address", default=DEFAULT_QUEUE_ADDRESS)
@click.option("-p", "--push-bind-address", default=DEFAULT_PUSH_ADDRESS)
@click.pass_context
def worker_queue(ctx, rep_bind_address, push_bind_address):
    queue_server = QueueServer(rep_bind_address, push_bind_address)
    asyncio.run(queue_server.run())


@main.command("crawler")
@click.option("-m", "--max-pages", default=100, type=int)
@click.option("-f", "--urls-file", default=f"recipe-urls.json")
@click.option("-c", "--rep-connect-address", default=DEFAULT_QUEUE_ADDRESS)
@click.pass_context
def crawl_sitemap_for_recipes(ctx, rep_connect_address, max_pages, urls_file):
    client = TudoGostosoClient()
    urls_file = Path(urls_file)
    recipe_urls = []

    if urls_file.is_file():
        with urls_file.open("r") as fd:
            try:
                recipe_urls = json.load(fd)
                print(f"loaded recipe urls from {urls_file}")
            except Exception as e:
                print(f"failed to load recipe urls from {urls_file}: {e}")

    if not recipe_urls:
        recipe_urls = client.crawl_sitemap(max_pages=max_pages)

        with urls_file.open("w") as fd:
            json.dump(recipe_urls, fd)
            print(f"stored recipe urls in {urls_file}")

    count = len(recipe_urls)
    print(f"found {count} failed recipes")
    worker = QueueClient(rep_connect_address)
    worker.connect()

    for i, url in enumerate(recipe_urls, start=1):
        print(f" -> enqueing recipe {i} of {count} -> {url}")
        worker.send({"recipe_url": url})

    worker.close()


@main.command("web")
@click.option("-p", "--port", default=3000, type=int)
@click.option("-h", "--host", default="0.0.0.0")
@click.option("-d", "--debug", is_flag=True, default=False)
@click.pass_context
def web_server(ctx, host, port, debug):
    uvicorn.run(app, host=host, port=port, debug=debug)


@main.command("purge")
def purge_elasticsearch():
    es = connect_to_elasticsearch()
    try:
        print(es.indices.delete(index="recipes"))
    except Exception as e:
        logger.error(f'failed to purge index "recipes": {e}')


@main.command("env")
@click.option("-d", "--docker", is_flag=True)
@click.pass_context
def print_env_declaration(ctx, docker):
    if docker:
        print(config.to_docker_env_declaration())
    else:
        print(config.to_shell_env_declaration())


@main.command("cleanup-workflows")
def cleanup_workflows():
    get_logger("requests").setLevel(logging.DEBUG)
    http = requests.Session()
    GITHUB_API_TOKEN = os.environ["GITHUB_API_TOKEN"]
    http.headers = {
        "Authorization": f"Bearer {GITHUB_API_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    runs = http.get(
        "https://api.github.com/repos/gabrielfalcao/cook-my-list/actions/runs"
    ).json()["workflow_runs"]
    for failure in [r for r in runs if "failure" in (r["conclusion"] or "")]:
        url = f"https://api.github.com/repos/gabrielfalcao/cook-my-list/actions/runs/{failure['id']}"

        res = http.delete(url)
        logger.warning(f"DELETE {url}: {res}")
