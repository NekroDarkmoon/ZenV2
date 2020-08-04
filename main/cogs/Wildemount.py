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


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Wildemount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Cog check
    async def cog_check(self, ctx):
        return ctx.guild.id == 739684323141353597

    @commands.command(name="beep", pass_context="True")
    async def beep(self, ctx):
        await ctx.message.delete()
        response = emb.gen_embed_green('Beep', 'Boop')
        await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Wildemount(bot))
