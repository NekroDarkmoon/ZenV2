#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import asyncio

from click.decorators import option
import asyncpg
import click
import importlib
import contextlib
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
import traceback
# Third party imports


# Local application imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
import main.settings.config as config
from main.bot import Zen # noqa
from main.cogs.utils.db import DB # noqa


# --------------------------------------------------------------------------
#                                  Setup UVLOOP
# --------------------------------------------------------------------------
try:
    import uvloop 
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


# --------------------------------------------------------------------------
#                                  Logging Setup
# --------------------------------------------------------------------------
class RemoveNoise(logging.Filter):
    def __init__(self) -> None:
        super().__init__(name='discord.state')
    
    def filter(self, record) -> bool:
        if record.levelname == 'WARNING' and 'referencing an unknown' in record.msg:
            return False
        
        return True


@contextlib.contextmanager
def setup_logging() -> None:
    try:
        #__enter__
        max_bytes: int = 32 * 1024 * 1024
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)
        logging.getLogger('discord.state').addFilter(RemoveNoise())

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename='Zen.log', encoding='utf-8', mode='w', maxBytes=max_bytes, backupCount=5)
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
#                                    Run Bot
# --------------------------------------------------------------------------
def run_bot() -> None:
    loop = asyncio.get_event_loop()
    log = logging.getLogger()

    kwargs = {
        'command_timeout': 60,
        'max_size': 20,
        'min_size': 20,
    }

    try:
        pool = loop.run_until_complete(DB.create_pool(config.db, **kwargs))
    except Exception as e:
        click.echo("Could not set up postgres. Exiting.", file=sys.stderr)
        log.exception("Could not set up postress. Exiting.")
        return

    bot = Zen()
    bot.pool = pool
    bot.run()


# --------------------------------------------------------------------------
#                                     Main
# --------------------------------------------------------------------------
@click.group(invoke_without_command=True, options_metavar='[options]')
@click.pass_context
def main(ctx) -> None:
    """Launch Bot"""
    if (ctx.invoked_subcommand is None):
        loop = asyncio.get_event_loop()
        with setup_logging():
            run_bot()

# --------------------------------------------------------------------------
#                                     INIT
# --------------------------------------------------------------------------
if __name__ == "__main__":
    main()