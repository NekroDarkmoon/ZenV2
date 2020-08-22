#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import numpy as np
import random
import os
import sys

# Third party imports
import asyncio
import discord # noqa
from discord.ext import commands

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from settings import embeds as emb # noqa
from utils import npc_gen as npcgen # noqa


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Dnd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                       Npc Gen
    @commands.command(name="gnpc", pass_context=True, help="Generating a random npc.",
                      usage="m/f/t[Optional], race[Optional]")
    async def gnpc(self, ctx, *args):
        sex = None
        race = None

        for arg in args:
            if len(arg) == 1:
                sex = arg
            else:
                race = arg
        response = npcgen.main(sex, race)
        response = emb.gen_embed_cobalt('NPC Generator', response)
        await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                   Weather Gen
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

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                   Letter gen
    @commands.command(name="gletter")
    async def gletter(self, ctx):
        """ Creates a letter handout."""
        from utils import letter_gen as lettergen # noqa

        # Get variables
        author = ctx.author

        def check(message):
            return author == message.author

        # Create initial embeds
        msg = "Let's begin the process. Please type the title on the letter or c to cancel"
        msg += "\n(Note: Title and Signature can be left empty by typing None.)\n"
        msg += "(Note: Every section has a 30 secs time limit.)"

        # Send inital embed
        e = emb.gen_embed_cobalt('Creating Letter', "")
        preview = await ctx.send(msg, embed=e)

        # Getting the title
        try:
            title = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('Timed out. 👎')
            return

        if title.content == 'c':
            return
        elif title.content.lower() == 'none':
            title.content = None
        else:
            title.content = str(title.content)

        # Getting Content
        msg = 'Next type in the content or enter c to cancel...'
        e = emb.gen_embed_cobalt('Creating Letter', "")
        e.set_thumbnail(url=ctx.author.avatar_url)
        e.add_field(name='Title', value=title.content, inline=False)

        await preview.edit(content=msg, embed=e)

        try:
            content = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('Timed out. 👎')
            return

        if content.content == 'c':
            return
        else:
            content.content = str(content.content)
            if len(content.content) > 770:
                content.content = content.content[:770]
                val = f'{content.content[:500]}...'
            val = content.content

        e.add_field(name='Content', value=val, inline=False)

        # Getting the signature
        await preview.edit(content="Next enter the signature", embed=e)

        try:
            signature = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.channel.send('Timed out. 👎')
            return

        if signature.content == 'c':
            return
        elif signature.content.lower() == 'none':
            signature.content = None
        else:
            signature.content = str(signature.content)

        e.add_field(name='Signature', value=signature.content, inline=False)
        await preview.edit(content='Generating...', embed=e)

        async with ctx.typing():
            image = lettergen.main(title.content, content.content, signature.content)
            file = discord.File(filename="circle.png", fp=image)
        await preview.delete()

        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Dnd(bot))
