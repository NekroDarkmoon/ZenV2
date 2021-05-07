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

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                  Introduction filter 
    @commands.command(name="intro")
    async def intro(self, ctx, *message):
        # Variables
        guild = ctx.guild
        author = ctx.message.author
        roles = author.roles
        is_guest = False
        guest = None

        # Validation
        for role in roles:
            if role.name == "Guest":
                is_guest = True
                guest = role

        if (guest is None) or (is_guest == False):
            return

        try:
            await author.remove_roles(role)
            await ctx.add_reaction('<:upvote:741279182109147286>')
        except Exception:
            log.error(traceback.format_exc())


def setup(bot):
    bot.add_cog(Mod(bot))
