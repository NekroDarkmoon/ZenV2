#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import random
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

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Creating an lfg
    @commands.command(name="clfg", help="Create a post for a game.",
                      usage="d/p Description")
    async def clfg(self, ctx, post_type, *, msg):
        await ctx.message.delete()

        # validation
        if post_type.lower() == 'p':
            post_type = "Player"
        elif post_type.lower() == 'd':
            post_type = "DM"
        else:
            response = emb.gen_embed_yellow('Error', 'Usage: &clfg p/d Description')
            await ctx.send(embed=response)
            return

        if len(msg) < 5:
            response = emb.gen_embed_yellow('Error', 'Description must be longer than 5 words.')
            await ctx.send(embed=response)
            return

        # Getting variables
        author = ctx.author.name + '#' + ctx.author.discriminator
        post_id = random.randint(0, 10000000)
        server_id = ctx.guild.id

        # data_tuple = (server_id, post_id, author, post_type, msg)

        sql = """INSERT INTO quest(server_id, quest_id, author, quest_type, msg)
                 VALUES($1, $2, $3, $4, $5)"""

        try:
            await self.bot.pool.execute(sql, server_id, post_id, author, post_type, msg)
            response = emb.gen_embed_green(
                                        f'Looking for game - {post_id} ',
                                        f'Entry successfully created.\n\n{msg}')
            await ctx.send(embed=response)
        except Exception as e:
            print("Failed to enter data", e)
            await ctx.send(embed=emb.gen_embed_orange("Error", "Internal Error Occured"))

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Creating an lfg
    @commands.command(name="lfg", help="List all lfg quests", usage="d/p Description")
    async def lfg(self, ctx, quest_id=None):

        sql = """SELECT * FROM quest WHERE server_id=$1"""
        try:
            rows = await self.bot.pool.fetch(sql, ctx.guild.id)
        except Exception as e:
            print(e)

        for record in rows:
            entry = f"{record[2]}: **{record[3]}** - {record[4]}"
            response = emb.gen_embed_green(f"Quest ID: {record[1]}", f"{entry}")
            await ctx.send(embed=response)


def setup(bot):
    bot.add_cog(Wildemount(bot))