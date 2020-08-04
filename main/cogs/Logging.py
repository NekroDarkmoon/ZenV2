
# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import sys
import os
import datetime as dt
import re
# Third party imports
import discord # noqa
from discord import utils
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
        regex = "^[^\"\'\.\w]"
        try:
            if re.search(regex, message.content):
                return
            if message.author.bot:
                return

            author = message.author
            oc = message.channel
            content = message.content
            guild = message.guild
            attachment = message.attachments
            if attachment != []:
                attachment = message.attachments[0].proxy_url

            cat = utils.get(guild.categories, name='logs')
            if cat is None:
                cat = await guild.create_category('logs')

            send_channel = utils.get(guild.text_channels, name='msg-logs')
            if send_channel is None:
                send_channel = await guild.create_text_channel('msg-logs', category=cat)
            # Creating Embed
            response = emb.gen_embed_orange("Deleted Message Log",
                                            f"""Channel: {oc}
                                            Author: {author}
                                            Content:{content}
                                            Attachments: {attachment}""")

            await send_channel.send(embed=response)
        except Exception as e:
            print(e)

    @commands.Cog.listener(name="on_message_edit")
    async def on_message_edit(self, before, after):
        try:
            if before.author.bot:
                return

            author = before.author
            oc = before.channel
            bContent = before.content
            aContent = after.content
            guild = after.guild
            attachment = after.attachments
            if attachment != []:
                attachment = after.attachments[0].proxy_url

            cat = utils.get(guild.categories, name='logs')
            if cat is None:
                cat = await guild.create_category('logs')

            send_channel = utils.get(guild.text_channels, name='msg-logs')
            if send_channel is None:
                send_channel = await guild.create_text_channel('msg-logs', category=cat)
            # Creating Embed
            response = emb.gen_embed_orange("Edited Message Log",
                                            f"""Channel: {oc}
                                            Author: {author}
                                            Before: {bContent}
                                            After: {aContent}
                                            Attachments: {attachment}""")

            await send_channel.send(embed=response)
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Logging(bot))
