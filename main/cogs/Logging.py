# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import re
import sys
import os

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

    # Cog Check
    # async def cog_check(self, ctx):
    #     pass

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               On delete query
    @commands.Cog.listener(name="on_message_delete")
    async def on_message_delete(self, message):
        # Validation
        regex = "^[^\"\'\.\w]"
        if re.search(regex, message.content):
            return
        if message.author.bot:
            return

        # Getting Variables
        author = message.author
        oc = message.channel
        content = message.content
        guild = message.guild
        attachment = message.attachments
        if attachment != []:
            attachment = message.attachments[0].proxy_url

        # Sending to log channel
        try:
            cat = utils.get(guild.categories, name='Moderation')
            if cat is None:
                cat = await guild.create_category('Moderation')

            send_channel = utils.get(guild.text_channels, name='modlog')
            if send_channel is None:
                send_channel = await guild.create_text_channel('modlog', category=cat)

            # Creating Embed
            response = emb.gen_embed_orange("Deleted Message Log",
                                            f"""Channel: {oc}
                                            Author: {author}
                                            Content:{content}
                                            Attachments: {attachment}""")

            await send_channel.send(embed=response)

        except Exception as e:
            print(e)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               On edit query
    @commands.Cog.listener(name="on_message_edit")
    async def on_message_edit(self, before, after):
        # Validation
        if before.author.bot:
            return
        if (after.edited_at - before.created_at).total_seconds() < 60:
            return

        # Getting Variables
        author = before.author
        oc = before.channel
        oldContent = before.content
        newContent = after.content
        guild = after.guild
        attachment = after.attachments
        if attachment != []:
            attachment = after.attachments[0].proxy_url

        # Logging to channel
        try:
            cat = utils.get(guild.categories, name='Moderation')
            if cat is None:
                cat = await guild.create_category('Moderation')

            send_channel = utils.get(guild.text_channels, name='modlog')
            if send_channel is None:
                send_channel = await guild.create_text_channel('modlog', category=cat)
            # Creating Embed
            response = emb.gen_embed_orange("Edited Message Log",
                                            f"""Channel: {oc}
                                            Author: {author}
                                            Before: {oldContent}
                                            After: {newContent}
                                            Attachments: {attachment}""")

            await send_channel.send(embed=response)
        except Exception as e:
            print(e)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               On update query
    @commands.Cog.listener(name="on_member_update")
    async def on_member_update(self, before, after):
        # Validation
        if before.bot:
            return

        # Get variables
        member = before.name
        id = before.id
        oldNick = before.nick
        newNick = after.nick
        guild = before.guild

        if oldNick is None:
            oldNick = before.name
        if newNick is None:
            newNick = before.name

        if oldNick == newNick:
            return

        #  Logging to channel
        try:
            cat = utils.get(guild.categories, name='Moderation')
            if cat is None:
                cat = await guild.create_category('Moderation')

            send_channel = utils.get(guild.text_channels, name='modlog')
            if send_channel is None:
                send_channel = await guild.create_text_channel('modlog', category=cat)
            # Creating Embed
            response = emb.gen_embed_orange(member,
                                            f"""User Id: {id}
                                            Old Nickname: {oldNick}
                                            New Nickname: {newNick}""")
            response.set_thumbnail(url=before.avatar_url)
            await send_channel.send(embed=response)
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Logging(bot))
