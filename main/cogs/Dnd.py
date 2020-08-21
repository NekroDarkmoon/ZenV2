#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys

# Third party imports
import discord # noqa
from discord.ext import commands

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from settings import embeds as emb # noqa
from utils import npc_gen as npcgen # noqa


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Dnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gnpc", pass_context=True, help="Generating a random npc.",
                      usage="m/f/t[Optional], race[Optional]")
    async def gnpc(self, ctx, *args):
        sex = None
        race = None

        for arg in args:
            if len(arg) == 1:
                sex = arg
            else:
                race = arg
        response = npcgen.main(sex, race)
        response = emb.gen_embed_cobalt('NPC Generator', response)
        await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Dnd(bot))
