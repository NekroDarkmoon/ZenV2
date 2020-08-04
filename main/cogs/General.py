#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import numpy as np
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


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", pass_context=True, help="Replies with the latency to the bot.")
    async def ping(self, ctx):
        description = f'Pong! {round(self.bot.latency *1000)} ms'
        response = emb.gen_embed_green('Ping!', description)
        await ctx.send(embed=response)

    @commands.command(name='source', help="Gets the bot's source code and trello page.")
    async def source(self, ctx, *args):
        trello = ''
        github = 'https://github.com/NekroDarkmoon/Zen-Public/'

        for arg in args:
            if arg == '-t':
                trello = 'https://trello.com/b/rej22uVl/zen'

        try:
            await ctx.send(github + '\n' + trello)
        except Exception as e:
            print(e)

    @commands.command(name='weather', help="Generates the weather for the world")
    async def weather(self, ctx):
        # Create embed
        e = emb.gen_embed_cobalt('Weather Generator', None)

        # Generate Precipitation
        precip = ['No Precipitation', 'Light rain or snowfall', 'Heavy rain or snowfall']
        precip = np.random.choice(precip, p=[0.6, 0.25, 0.15])
        e.add_field(name='Precipitation', value=precip, inline=False)

        # Generate Temps
        roll = random.randint(1, 4)
        temp = ['Normal for the season', f'{roll*10} degrees Fahrenheit colder than normal',
                f'{roll*10} degrees Fahrenheit colder than normal']
        temp = np.random.choice(temp, p=[0.7, 0.15, 0.15])
        e.add_field(name='Temperature', value=temp, inline=False)

        # Generate Wind
        wind = ['No Wind', 'Light Wind', 'Medium Wind', 'Heavy/Strong Wind']
        wind = np.random.choice(wind, p=[0.1, 0.55, 0.2, 0.15])
        e.add_field(name='Wind', value=wind, inline=False)

        # Generate speeds
        roll = random.randint(1, 6) + random.randint(1, 6)
        direction = ['North', 'North-East', 'East', 'South-East', 'South',
                     'South-West', 'West', 'North-West']

        if wind == 'Medium Wind':
            speed = [50, 40, 30, 20, 10, 0, 0, 10, 20, 30, 40, 50]
            speed = str(speed[roll-1]) + ' feet'
            e.add_field(name='Speed', value=speed, inline=False)
            direction = np.random.choice(direction)
            e.add_field(name='Direction', value=direction, inline=False)

        elif wind == 'Heavy/Strong Wind':
            speed = [110, 100, 90, 80, 70, 60, 60, 70, 80, 90, 100, 110]
            speed = str(speed[roll-1]) + ' feet'
            e.add_field(name='Speed', value=speed, inline=True)
            direction = np.random.choice(direction)
            e.add_field(name='Direction', value=direction, inline=False)

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(General(bot))
