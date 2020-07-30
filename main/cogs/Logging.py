
# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import sys
import os
import codecs
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
    async def on_message_delete(self, message):
        try:
            with open("delete_log.txt", "a+", encoding="utf-8") as f:
                f.write(str(message.channel) + ":\t" + str(message.author) + " - " + message.content + "\n")
            f.close()
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Logging(bot))
