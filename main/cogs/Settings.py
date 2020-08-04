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
class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", pass_context="True")
    @commands.has_permissions(administrator=True)
    async def load(self, ctx, extension):
        try:
            self.bot.load_extension(f"main.cogs.{extension}")
            print(f"{extension} loaded")
            response = emb.gen_embed_orange("System Alert", f"{extension} loaded")
            await ctx.send(embed=response)
        except Exception as e:
            print(e)
            response = emb.gen_embed_orange("System Alert", f"{extension} failed to load")
            await ctx.send(embed=response)

    @commands.command(name="unload", pass_context="True")
    @commands.has_permissions(administrator=True)
    async def unload(self, ctx, extension):
        try:
            self.bot.unload_extension(f"main.cogs.{extension}")
            print(f"{extension} unloaded")
            response = emb.gen_embed_orange("System Alert", f"{extension} unloaded")
            await ctx.send(embed=response)
        except Exception as e:
            print(e)
            response = emb.gen_embed_orange("System Alert", f"{extension} failed to load")
            await ctx.send(embed=response)

    @commands.command(name="reload", pass_context="True")
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx, extension):
        try:
            self.bot.unload_extension(f"main.cogs.{extension}")
            self.bot.load_extension(f"main.cogs.{extension}")
            print(f"{extension} reloaded")
            response = emb.gen_embed_orange("System Alert", f"{extension} reloaded")
            await ctx.send(embed=response)
        except Exception as e:
            print(e)
            response = emb.gen_embed_orange("System Alert", f"{extension} failed to load")
            await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Settings(bot))
