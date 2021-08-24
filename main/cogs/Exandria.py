#!/usr/bin/env python3
# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys
import traceback

# Third party imports
import discord # noqa
from discord.ext import commands
from discord.ext.commands.core import Command

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Exandria(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    # Restrict to server
    async def cog_check(self, ctx):
        return True if ctx.guild.id in [719063399148814418, 739684323141353597] else False


    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                  Channel Restrictions
    @commands.Cog.listener()
    async def on_message(self, msg) -> None:
        # Validations
        if msg.author.bot:
            return
        
        try:
            roles: list = msg.author.roles
        except Exception:
            logging.warn(f"User {msg.author} has no roles.")
            return

        for role in roles:
            if role.name == 'Exceptions':
                return
        
        if (msg.channel.id in [719063951442313307, 719070160014803045, 877310663591096340]):
            content: str = msg.content

            if "[" in content and "]" in content:
                pass
            else:
                await msg.delete(delay=10)
                await msg.reply("`Please add relevant tags to your post. Example tags can be found in pinned messages.`",
                                delete_after=15)
                

        


def setup(bot):
    bot.add_cog(Exandria(bot))
