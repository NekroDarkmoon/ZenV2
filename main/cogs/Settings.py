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
class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Cog check
    async def cog_check(self, ctx):
        owners = [563066232593448990, 431499845644320770, 157433182331863040]
        return True if ctx.author.id in owners else False

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               Load Cog
    @commands.command(name="load", pass_context="True")
    async def load(self, ctx, extension):
        try:
            self.bot.load_extension(f"main.cogs.{extension}")
            print(f"{extension} loaded")
            response = emb.gen_embed_orange("System Alert", f"{extension} loaded")
            await ctx.send(embed=response)
        except Exception as e:
            log.error(e)
            response = emb.gen_embed_orange("System Alert", f"{extension} failed to load")
            await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                              Unlaod Cog
    @commands.command(name="unload", pass_context="True")
    async def unload(self, ctx, extension):
        try:
            self.bot.unload_extension(f"main.cogs.{extension}")
            print(f"{extension} unloaded")
            response = emb.gen_embed_orange("System Alert", f"{extension} unloaded")
            await ctx.send(embed=response)
        except Exception as e:
            log.error(e)
            response = emb.gen_embed_orange("System Alert", f"{extension} failed to load")
            await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               Reload Cog
    @commands.command(name="reload", pass_context="True")
    async def reload(self, ctx, extension):
        try:
            self.bot.unload_extension(f"main.cogs.{extension}")
            self.bot.load_extension(f"main.cogs.{extension}")
            print(f"{extension} reloaded")
            response = emb.gen_embed_orange("System Alert", f"{extension} reloaded")
            await ctx.send(embed=response)
        except Exception as e:
            log.error(e)
            response = emb.gen_embed_orange("System Alert", f"{extension} failed to load")
            await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                       Setting up channel restrictions
    @commands.command()
    async def users(self, ctx):
        try:
            users = self.bot.users
            for user in users:
                print(user.name + ": " + str(user.id))
        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                              Drop tables
    @commands.command(name="drop")
    async def drop(self, ctx, db: str):

        conn = self.bot.pool

        try:
            if (db == "lb"):
                await conn.execute("""DROP TABLE lb;""")
                response = emb.gen_embed_red("Warning!", "Table lb deleted.")
                await ctx.send(embed=response)

            elif (db == "roles"):

                fetchrole = await conn.fetch("""SELECT * FROM roles""")

                print(fetchrole)
                for fetched in fetchrole:
                    await self.bot.get_guild(fetched["server_id"]).get_role(fetched["role_id"]).delete()

                await conn.execute("""DROP TABLE roles;""")
                response = emb.gen_embed_red("Warning!", "Table roles deleted.")
                await ctx.send(embed=response)

            else:
                response = emb.gen_embed_red("Warning!", "That's not a table.")
                await ctx.send(embed=response)

        except Exception as e:
            log.error(e)


def setup(bot):
    bot.add_cog(Owner(bot))
