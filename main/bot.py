#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import json
import logging
import os
import sys
import traceback

# Third party imports
from discord.ext import commands
import discord # noqa

# Local application imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


# --------------------------------------------------------------------------
#                                  Bot.py
# --------------------------------------------------------------------------
description = """
Hello! I am a bot for DnD severs.
"""


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
        except Exception as e:
            print(e)


# --------------------------------------------------------------------------
#                                  Bot Class
# --------------------------------------------------------------------------
 class Zen(commands.Bot):
     def __init__(self, command_prefix):
         super().__init__(command_prefix)
