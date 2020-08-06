#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import sys
import os

# Third party imports
import discord # noqa
from discord.ext import commands

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from settings import embeds as emb # noqa


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                Join
    @commands.command(name='join')
    async def join(self, ctx):
        member = ctx.author
        voice = getattr(member, 'voice', None)

        if voice is not None:
            vc = voice.channel
            await vc.connect()

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                Leave
    @commands.command(name='leave')
    async def leave(self, ctx):
        member = ctx.author
        voice = getattr(member, 'voice', None)

        if voice is not None:
            vc = voice.channel
            await vc.connect()


def setup(bot):
    bot.add_cog(Music(bot))
