#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import argparse
import logging
import random
import re
import shlex
import sys
import os
import traceback

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
#                                 ArgeParse
# --------------------------------------------------------------------------
class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class PersonalChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    # Cog check
    async def cog_check(self, ctx):
        guilds = []
        return True if ctx.guild.id in guilds else False
    
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                   CPC
    @staticmethod
    def __get_playchn_arguments(args):
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('users', nargs='+')
        parser.add_argument('-d', '--delete', action='store_true')
        parser.add_argument('-r', '--remove', action='store_true')

        if args is not None:
            return parser.parse_args(shlex.split(args))
        else:
            return parser.parse_args([])
    

    @commands.command(name="newplaychn")
    async def newplaychn(self, ctx, *, args: str = None):
        """Creates a channel for you and your friends to use.
        
        Usage: To create - `&playchn @user1 @user2 ... @user10`
        To delete - `&playchn @yourself -d`
               To add - `&playchn @user1 ... @user10`
               To remove = `&playchn -r @user1 ... @user 10`

        **Note:** You can only have one channel.
        **Note:** Max limit is 10. When adding or removing users you don't need to mention yourself."""

        try:
            args = self.__get_playchn_arguments(args)
        except RuntimeError as e:
            return await ctx.send(f"`{e}`")

        
        # Get Vars
        server = ctx.guild
        author = ctx.author

        # Validation
        

def setup(bot):
    bot.add_cog(PersonalChannels(bot))