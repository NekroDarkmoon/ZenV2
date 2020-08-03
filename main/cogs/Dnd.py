#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
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
from utils import npc_gen as npcgen # noqa

# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Dnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gnpc", pass_context=True)
    async def gnpc(self, ctx, *args):
        response = emb.gen_embed_cobalt('NPC Generator', npcgen.main("", ""))
        await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Dnd(bot))
