#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import random
import sys
import traceback
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
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", pass_context=True)
    async def ping(self, ctx):
        """Replies with the latency to the bot.

        Usage: `ping`"""

        description = f'Pong! {round(self.bot.latency *1000)} ms'
        response = emb.gen_embed_green('Ping!', description)
        await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                   Source code
    @commands.command(name='source')
    async def source(self, ctx, *args):
        """Gets the bot's source code and trello page.

        Usage: `source -t[Optional]`"""

        trello = ''
        github = 'https://github.com/NekroDarkmoon/Zen-Public/'

        for arg in args:
            if arg == '-t':
                trello = 'https://trello.com/b/rej22uVl/zen'

        try:
            await ctx.send(github + '\n' + trello)
        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                   Inator
    @commands.command(name='inator')
    async def inator(self, ctx, *, noun):
        """ Create an inator! \n\nUsage: `inator word`"""
        number = random.randint(1000, 3000)
        response = "I’ve come up with the best plan to take over the Tri-State Area!!! "
        response += f"Behold the {noun}inator{number}"
        response = emb.gen_embed_green('Inator3000', response)
        await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               Invite Generator
    @commands.command(name="invite")
    async def invite(self, ctx):
        """ Get an invite for your server

        Usage: `invite`"""

        link = "https://discord.com/api/oauth2/authorize?client_id=607734719853101066&permissions=8&scope=bot"
        e = discord.Embed(
            title='Invite Link',
            url=link,
            color=0x63ddff
        )
        e.set_thumbnail(url=self.bot.get_user(607734719853101066).avatar_url)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(General(bot))
