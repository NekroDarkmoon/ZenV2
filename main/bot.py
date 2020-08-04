#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import contextlib
import datetime
import json
import logging
import os
import sys
import traceback

# Third party imports
import discord # noqa
from discord.ext import commands

# Local application imports
from main.cogs.utils import context # noqa
# from cogs.utils import embed_help as EmbedHelpCommand # noqa

# --------------------------------------------------------------------------
#                                  Bot.py
# --------------------------------------------------------------------------
description = """
Hello! I am a bot for DnD severs.
"""

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                  Load Cogs
# --------------------------------------------------------------------------
def load_cogs(bot):
    for cog in [file.split('.')[0] for file in os.listdir("main/cogs") if file.endswith(".py")]:
        try:
            if cog != "__init__":
                bot.load_extension(f"main.cogs.{cog}")
                print(f"{cog} Loaded...")
        except Exception as e:
            print(e)
            traceback.print_exc()


# --------------------------------------------------------------------------
#                                 _prefix_callable
# --------------------------------------------------------------------------
def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('?')
        base.append('~')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['?', '~']))
    return base


# --------------------------------------------------------------------------
#                               Help Command
# --------------------------------------------------------------------------
class EmbedHelpCommand(commands.HelpCommand):
    """Overriding the basic help command with an embed."""
    COLOR = discord.Color.blurple()

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.'.format(self.clean_prefix,
                                                                         self.invoked_with)

    def get_command_signature(self, command):
        return '{0.qualified_name} {0.signature}'.format(command)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Bot Commands', colour=self.COLOR)
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog, commands in mapping.items():
            name = 'No Category' if cog is None else cog.qualified_name
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = '\u2002'.join(c.name for c in commands)
                if cog and cog.description:
                    value = '{0}\n{1}'.format(cog.description, value)

                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title='{0.qualified_name} Commands'.format(cog), colour=self.COLOR)
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command),
                            value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name, colour=self.COLOR)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command),
                                value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    send_command_help = send_group_help


# --------------------------------------------------------------------------
#                                  Bot Class
# --------------------------------------------------------------------------
class Zen(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='~', description=description, pm_help=None,
                         help_attrs=dict(hidden=True), fetch_offline_members=True,
                         heartbeat_timeout=150.0, help_command=EmbedHelpCommand())

        # self.client_id = self.configs['client_id']

    # On ready Function
    async def on_ready(self):
        load_cogs(self)

        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(f'Ready: {self.user} (ID: {self.user.id})')

    # Command Error handler
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.send(error)

    # async def close(self):
    #     await super().close()
    #     await self.session.close()

    def run(self):
        try:
            super().run(self.configs["token"], reconnect=True)
        except Exception as e:
            print(e)

# if __name__ == "__main__":
#     bot = Zen()
#     bot.run(configs["token"])
