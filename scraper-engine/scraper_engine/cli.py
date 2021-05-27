import gevent.monkey

gevent.monkey.patch_all()

import time
import click
from gevent.pool import Pool
from typing import Optional
from uiclasses import Model
from pathlib import Path
from datetime import datetime, timedelta
from scraper_engine.sites.tudo_gostoso import TudoGostosoClient
from scraper_engine import sql
from scraper_engine.logs import logger
from scraper_engine.sites.tudo_gostoso.models import Recipe

from scraper_engine.workers import GetRecipeWorker
from scraper_engine.workers import QueueServer, QueueClient


DEFAULT_QUEUE_ADDRESS = "tcp://127.0.0.1:5000"
DEFAULT_PUSH_ADDRESS = "tcp://127.0.0.1:6000"


@click.group()
@click.pass_context
def main(ctx):
    print("Cook-My-List Scraper Engine")
    sql.context.set_default_uri("postgresql://scraper_engine@localhost/scraper_engine")
    ctx.obj = {}


@main.command("workers")
@click.option("-s", "--queue-address", default=DEFAULT_QUEUE_ADDRESS)
@click.option("-m", "--max-workers", default=2, type=int)
@click.pass_context
def workers(ctx, queue_address, max_workers):
    pool = Pool()
    queue_server = QueueServer(queue_address, "inproc://recipe-info")

    pool.spawn(queue_server.run)
    for worker_id in range(max_workers):
        recipe_info_worker = GetRecipeWorker(
            "inproc://recipe-info", worker_id, **ctx.obj
        )
        pool.spawn(recipe_info_worker.run)

    while True:
        try:
            pool.join(1)
        except KeyboardInterrupt:
            pool.kill()
            raise SystemExit(1)


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


@main.command("recipes")
@click.option("-d", "--days", default=5, type=int)
@click.option("-c", "--rep-connect-address", default=DEFAULT_QUEUE_ADDRESS)
@click.pass_context
def get_recipes(ctx, rep_connect_address, days):
    client = TudoGostosoClient(
        url=ctx.obj["drone_url"],
        access_token=ctx.obj["access_token"],
    )
    recipes = client.get_recipes()
    count = len(recipes)
    print(f"found {count} failed recipes in the last {days} days")
    for i, recipe in enumerate(recipes, start=1):
        worker = QueueClient(rep_connect_address)
        worker.connect()
        print(
            f" -> enqueing recipe {i} of {count} for output analysis (#{recipe.number} by {recipe.author_login})"
        )
        worker.send({"recipe_id": recipe.number})
        worker.close()
    return
