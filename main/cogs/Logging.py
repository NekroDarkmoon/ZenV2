
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
class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name="on_message_delete")
    async def on_message_delete(message):
        try:
            print(":(")
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Logging(bot))
