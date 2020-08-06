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
        self.vc_conn = []

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                Join
    @commands.command(name='join')
    async def join(self, ctx):
        # Get variables
        member = ctx.author
        voice = getattr(member, 'voice', None)

        if voice is not None:
            vc = voice.channel
            conn = await vc.connect()
            self.vc_conn.append(conn)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                Leave
    @commands.command(name='leave')
    async def leave(self, ctx):
        # Get variables
        member = ctx.author
        guild = ctx.guild
        voice = getattr(member, 'voice', None)

        if voice is not None:
            conns = self.vc_conn
            for conn in conns:
                if conn.guild == guild:
                    await conn.disconnect()
                    self.vc_conn.remove(conn)

        print(self.vc_conn)


def setup(bot):
    bot.add_cog(Music(bot))
