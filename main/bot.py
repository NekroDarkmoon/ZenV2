#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
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
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from cogs.utils import context # noqa
# from cogs.utils import embed_help as EmbedHelpCommand # noqa

# --------------------------------------------------------------------------
#                                  Bot.py
# --------------------------------------------------------------------------
description = """
Hello! I am a bot for DnD severs.
"""

# Load config settings form json
with open("settings/config.json") as conf:
    configs = json.load(conf)


# --------------------------------------------------------------------------
#                                  Logging Setup
# --------------------------------------------------------------------------
def setup_logging():
    try:
        # __enter__
        logging.getLogger('discord').setLevel(logging.INFO)
        logging.getLogger('discord.http').setLevel(logging.WARNING)

        log = logging.getLogger()
        log.setLevel(logging.INFO)
        handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
        dt_fmt = '%Y-%m-%d %H:%M:%S'
        fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


# --------------------------------------------------------------------------
#                                  Load Cogs
# --------------------------------------------------------------------------
def load_cogs(client):
    for cog in [file.split('.')[0] for file in os.listdir("cogs") if file.endswith(".py")]:
        try:
            if cog != "__init__":
                client.load_extension(f"cogs.{cog}")
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

                embed.add_field(name=name, value=value)

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

        self.client_id = configs['client_id']

    # On ready Function
    async def on_ready(self):
        load_cogs(self)

        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(f'Ready: {self.user} (ID: {self.user.id})')

        setup_logging()
        print('Logging setup Complete')

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


if __name__ == "__main__":
    bot = Zen()
    bot.run(configs["token"])
