#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import datetime
import json
import logging
import os
import sys
import traceback

# Third party imports
import discord # noqa
from discord.ext import commands

# Local application imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


# --------------------------------------------------------------------------
#                                  Bot.py
# --------------------------------------------------------------------------
description = """
Hello! I am a bot for DnD severs.
"""

# Load config settings form json
with open("settings/config.json") as conf:
    configs = json.load(conf)


# --------------------------------------------------------------------------
#                                  Logging Setup
# --------------------------------------------------------------------------
def setup_logging():
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
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


# --------------------------------------------------------------------------
#                                  Load Cogs
# --------------------------------------------------------------------------
def load_cogs(client):
    for cog in [file.split('.')[0] for file in os.listdir("cogs") if file.endswith(".py")]:
        try:
            if cog != "__init__":
                client.load_extension(f"cogs.{cog}")
                print(f"{cog} Loaded...")
        except Exception as e:
            print(e)
            traceback.print_exc()


# --------------------------------------------------------------------------
#                                 _prefix_callable
# --------------------------------------------------------------------------
def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('?')
        base.append('~')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['?', '~']))
    return base


# --------------------------------------------------------------------------
#                                  Bot Class
# --------------------------------------------------------------------------
class Zen(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable, description=description, pm_help=None,
                         help_attrs=dict(hidden=True), fetch_offline_members=True,
                         heartbeat_timeout=150.0)

        self.client_id = configs['client_id']

    # On ready Function
    async def on_ready(self):
        load_cogs(self)

        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(f'Ready: {self.user} (ID: {self.user.id})')

        setup_logging()
        print('Logging setup Complete')


if __name__ == "__main__":
    bot = Zen()
    bot.run(configs["token"])
