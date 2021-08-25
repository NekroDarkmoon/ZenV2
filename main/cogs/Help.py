#!/usr/bin/env python3
# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import asyncio
import inspect
import itertools
import logging
import os
import sys
import traceback
from typing import Any, Dict, List, Optional, Union

# Third party imports
import discord
from discord import colour
from discord.ext import commands
from discord.ext import menus
from discord.ext.commands.core import command

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from main.cogs.utils.paginator import Pages


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                               Help Menu
# --------------------------------------------------------------------------
class HelpMenu(Pages):
    def __init__(self, source: menus.PageSource, *, ctx: commands.Context):
        super().__init__(source, ctx=ctx, comapct=True)
    

    def add_categories(self, commands: Dict[commands.Cog, List[commands.Command]]) -> None:
        self.clear_items()
        self.add_item(HelpSelectMenu(commands, self.ctx.bot))
        self.fill_items()
    

    async def rebind(self, source: menus.PageSource, interaction: discord.Interaction) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)


# --------------------------------------------------------------------------
#                              Help Select Menu
# --------------------------------------------------------------------------
class HelpSelectMenu(discord.ui.Select['HelpMenu']):
    def __init__(self, commands: Dict[commands.Cog, List[commands.Command]], bot: commands.AutoShardedBot) -> None:
        super().__init__(
            placeholder = "`Select a category`",
            min_values = 1,
            max_values = 1,
            row = 0
        )

        self.commands: Dict[commands.Cog, List[commands.Command]] = commands
        self.bot: commands.AutoShardedBot = bot
        self.__fill_options()


    def __fill_options(self) -> None:
        self.add_option(
            label="Index",
            emoji="\N{WAVING HAND SIGN}",
            value="__index",
            description="The help page showing how to use the bot."
        )

        for cog, commands in self.commands.items():
            if not commands:
                continue
            
            description = cog.description.split("\n", 1)[0] or None
            emoji = getattr(cog, 'display_emoji', None)
            self.add_option(
                label=cog.qualified_name,
                value=cog.qualified_name,
                description=description,
                emoji=emoji
            )
    

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        if value == "__index":
            await self.view.rebind(FrontPageSource(), interaction)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message("`This Category does not exist...?`", ephemeral=True)
                return
            
            commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message('`This category has no commands for you.`', ephemeral=True)
                return
            
            source = GroupHelpPageSource(cog, commands, prefix=self.view.ctx.clean_prefix)
            await self.view.rebind(source, interaction)


# --------------------------------------------------------------------------
#                          Group Help PageSource
# --------------------------------------------------------------------------
class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self, group: Union[commands.Group, commands.Cog], commands: List[commands.Command], *, prefix: str) -> None:
        super().__init__(entries=commands, per_page=6)
        self.group: Union[commands.Group, commands.Cog] = group
        self.prefix: str = prefix
        self.title: str = f'{self.group.qualified_name} Commands'
        self.description: str = self.group.description
    

    async def fromat_page(self, menu, commands):
        embed = discord.Embed(title=self.title, description=self.description, color=discord.Colour(0xA8B9CD))

        for command in commands:
            signature: str = f'{command.qualified_name} {command.signature}'
            embed.add_field(name=signature, value=command.short_doc or 'No help given...', inline=False)
        
        max: int = self.get_max_pages()
        if max > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{max} ({len(self.entries)} commands)')
        
        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed


# --------------------------------------------------------------------------
#                               Front Page Source
# --------------------------------------------------------------------------
class FrontPageSource(menus.PageSource):
    def is_paginating(self) -> bool:
        return True
    

    def get_mex_pages(self) -> Optional[int]:
        return 2
    

    async def get_page(self, page_num: int) -> Any:
        self.index = page_num
        return self

    def format_page(self, menu: HelpMenu, page):
        embed = discord.Embed(title="Zen Help", colour=discord.Colour(0xA8B9CD))
        embed.description = inspect.cleandoc(
            f"""
            Hello! Welcome to the help page.
            Use "{menu.ctx.clean_prefix}help command" for more info on a command.
            Use "{menu.ctx.clean_prefix}help category" for more info on a category.
            Use the dropdown menu below to select a category.
        """
        )

        embed.add_field(
            name = "Support Sever",
            value='No Official Support Server yet',
            inline=False,
        )

        return embed


# --------------------------------------------------------------------------
#                            Paginated Help Command
# --------------------------------------------------------------------------
class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self,) -> None:
        super().__init__(
            command_attrs={
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category',
            }
        )

    
    async def on_help_command_error(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.HTTPException) and error.original.code == 50013:
                return
            
            await ctx.send(f'`{str(error.original)}`')
    

    def get_command_signature(self, command) -> str:
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases: str = '|'.join(command.aliases)
            fmt: str = f'[{command.name}|{aliases}]'

            if parent:
                fmt: str = f'{parent} {fmt}'
            
            alias: str = fmt

        else:
            alias: str = command.name if not parent else f'{parent} {command.name}'
        
        return f'{alias} {command.signature}'


    async def send_bot_help(self, mapping: Any) -> None:
        bot = self.context.bot

        def key(command) -> str:
            cog = command.cog
            return cog.qualified_name if cog else '\U0010ffff'
        
        entries: List[commands.Command] = await self.filter_commands(bot.commands, sort=True, key=key)

        all_commands: Dict[commands.Cog, List[commands.Command]] = {}
        for name, children in itertools.groupby(entries, key=key):
            if name == '\U0010ffff':
                continue

            cog = bot.get_cog(name)
            all_commands[cog] = sorted(children, key=lambda c: c.qualified_name)
        
        menu = HelpMenu(FrontPageSource(), ctx=self.context)
        menu.add_categories(all_commands)
        
        await self.context.release()
        await menu.start()


    def common_command_formatting(self, embed_like, command: commands.Command) -> None:
        embed_like.title = self.get_command_signature(command)

        if command.description:
            embed_like.description = f'{command.description}\n\n{command.help}'
        else:
            embed_like.description = command.help or 'No help found...'
        

    async def send_command_help(self, command: commands.Command) -> None:
        embed = discord.Embed(colour=discord.Colour(0xA8B9CD))
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)
    
    
    async def send_group_help(self, group) -> None:
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)
        
        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group, entries, prefix=self.context.clean_prefix)
        self.common_command_formatting(source, group)
        menu = HelpMenu(source, ctx=self.context)
        await self.context.release()
        await menu.start()


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Help(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self



def setup(bot) -> None:
    bot.add_cog(Help(bot))