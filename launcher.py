#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import asyncio
import asyncpg
import click
import importlib
import contextlib
import logging
import json
import os
import sys
# Third party imports


# Local application imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from main.bot import Zen # noqa
from main.cogs.utils import db # noqa


# --------------------------------------------------------------------------
#                                  Logging Setup
# --------------------------------------------------------------------------
# Setting up the logging file
@contextlib.contextmanager
def setup_logging():
    """Setting the logger"""
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='Zen.log', encoding='utf-8', mode='w')
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


# --------------------------------------------------------------------------
#                                   Run Bot
# --------------------------------------------------------------------------
def run_bot():
    loop = asyncio.get_event_loop()
    log = logging.getLogger()

    # Getting config files
    with open("main/settings/config.json") as conf:
        configs = json.load(conf)

    # Setup db here
    try:
        pool = loop.run_until_complete(db.create_db(configs))
    except Exception as e:
        click.echo('Could not set up PostgreSQL. Exiting.', file=sys.stderr)
        log.exception('Could not set up PostgreSQL. Exiting.')
        print(e)
        return

    bot = Zen()
    bot.pool = pool
    bot.configs = configs
    bot.run()


# --------------------------------------------------------------------------
#                                   Main
# --------------------------------------------------------------------------
@click.group(invoke_without_command=True, options_metavar='[options]')
@click.pass_context
def main(ctx):
    """Launches the bot"""
    if ctx.invoked_subcommand is None:
        loop = asyncio.get_event_loop()
        with setup_logging():
            run_bot()


if __name__ == '__main__':
    main()
