# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys
import re
import traceback

# Third party imports
import discord # noqa
from discord import utils
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
        regex = "^[^\"\'\.\w]" # noqa
        if re.search(regex, message.content):
            return
        if message.author.bot:
            return
        if len(message.content) < 2:
            return

        # Getting Variables
        author = message.author
        oc = message.channel
        content = message.content
        guild = message.guild
        attachment = message.attachments
        if attachment != []:
            attachment = message.attachments[0].proxy_url
        else:
            attachment = None

        # Sending to log channel
        try:
            cat = utils.get(guild.categories, name='Moderation')
            if cat is None:
                cat = await guild.create_category('Moderation')

            send_channel = utils.get(guild.text_channels, name='modlog')
            if send_channel is None:
                send_channel = await guild.create_text_channel('modlog', category=cat)

            print(content)
            limit = 1024
            content = [content[i:i+limit] for i in range(0, len(content), limit)]
            print(content)

            # Creating Embed
            e = emb.gen_embed_orange("Deleted Message Log", "")
            if attachment:
                e.add_field(name='Attachments', value=attachment, inline=False)

            for chunk in content:
                print(chunk)
                e.add_field(name='Channel', value=oc, inline=True)
                e.add_field(name='Author', value=author, inline=True)
                e.add_field(name='Content', value=chunk, inline=False)

                await send_channel.send(embed=e)
                e.clear_fields()

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                               On edit query
    @commands.Cog.listener(name="on_message_edit")
    async def on_message_edit(self, before, after):

        # Validation
        if before.author.bot:
            return
        elif after.edited_at is not None:
            if (after.edited_at - before.created_at).total_seconds() < 60:
                return
        elif before.content == after.content:
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
        else:
            attachment = None

        # Logging to channel
        try:
            cat = utils.get(guild.categories, name='Moderation')
            if cat is None:
                cat = await guild.create_category('Moderation')

            send_channel = utils.get(guild.text_channels, name='modlog')
            if send_channel is None:
                send_channel = await guild.create_text_channel('modlog', category=cat)

            limit = 1024
            oldContent = [oldContent[i:i+limit] for i in range(0, len(oldContent), limit)]
            newContent = [newContent[i:i+limit] for i in range(0, len(newContent), limit)]

            # Creating Embed
            e = emb.gen_embed_orange("Edited Message Log", "")
            if attachment:
                e.add_field(name='Attachments', value=attachment, inline=False)

            for elem, chunk in enumerate(oldContent):
                e.add_field(name='Channel', value=oc, inline=True)
                e.add_field(name='Author', value=author, inline=True)
                e.add_field(name='Before', value=chunk, inline=False)
                e.add_field(name='After', value=newContent[elem], inline=False)

                await send_channel.send(embed=e)
                e.clear_fields()

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

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
            e = emb.gen_embed_orange(member, "")
            e.add_field(name='User ID', value=id, inline=True)
            e.add_field(name='Old Nickname', value=oldNick, inline=False)
            e.add_field(name='New Nickname', value=newNick, inline=False)
            e.set_thumbnail(url=before.avatar_url)

            await send_channel.send(embed=e)
        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())


def setup(bot):
    bot.add_cog(Logging(bot))
