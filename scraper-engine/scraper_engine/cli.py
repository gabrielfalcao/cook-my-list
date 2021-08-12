import json
import logging
import multiprocessing
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
import requests
from uiclasses import Model

from scraper_engine import sql
from scraper_engine.es import connect_to_elasticsearch
from scraper_engine.logs import get_logger, logger
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient
from scraper_engine.sites.tudo_gostoso.models import Recipe
from scraper_engine.sql import config
from scraper_engine.web.core import app
from scraper_engine.workers import GetRecipeWorker, QueueClient, QueueServer

DEFAULT_QUEUE_ADDRESS = "tcp://127.0.0.1:5000"
DEFAULT_PUSH_ADDRESS = "tcp://127.0.0.1:6000"
DEFAULT_MAX_WORKERS = multiprocessing.cpu_count()


@click.group()
@click.pass_context
def main(ctx):
    print("Cook-My-List Scraper Engine")
    sql.context.set_default_uri(config.SQLALCHEMY_URI)
    ctx.obj = {}


@main.command("workers")
@click.option("-s", "--queue-address", default=DEFAULT_QUEUE_ADDRESS)
@click.option("-m", "--max-workers", default=DEFAULT_MAX_WORKERS, type=int)
@click.pass_context
def workers(ctx, queue_address, max_workers):
    pool = ThreadPoolExecutor()
    loop = asyncio.get_running_loop()

    queue_server = QueueServer(queue_address, "inproc://recipe-info")

    loop.run_in_executor(pool, recipe_info_worker.run)
    for worker_id in range(max_workers):
        recipe_info_worker = GetRecipeWorker(
            "inproc://recipe-info", worker_id, **ctx.obj
        )
        loop.run_in_executor(pool, recipe_info_worker.run)
    import ipdb;ipdb.set_trace()  # fmt: skip


@main.command("worker:get_recipe")
@click.option("-c", "--pull-connect-address", default=DEFAULT_PUSH_ADDRESS)
@click.pass_context
def worker_get_recipe(ctx, pull_connect_address):
    worker = GetRecipeWorker(pull_connect_address)
    worker.run()


@main.command("worker:queue")
@click.option("-s", "--rep-bind-address", default=DEFAULT_QUEUE_ADDRESS)
@click.option("-p", "--push-bind-address", default=DEFAULT_PUSH_ADDRESS)
@click.pass_context
def worker_queue(ctx, rep_bind_address, push_bind_address):
    worker.run()


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
    app.run(host=host, port=port, debug=debug)


@main.command("purge")
def purge_elasticsearch():
    es = connect_to_elasticsearch()
    try:
        print(es.indices.delete(index="recipes"))
    except Exception as e:
        logger.error(f'failed to purge index "recipes": {e}')


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
