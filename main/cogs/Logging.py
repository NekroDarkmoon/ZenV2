# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys
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

            # Creating Embed
            e = emb.gen_embed_orange("Deleted Message Log", "")
            e.add_field(name='Channel', value=oc, inline=True)
            e.add_field(name='Author', value=author, inline=True)
            e.add_field(name='Content', value=content, inline=False)

            if attachment:
                e.add_field(name='Attachments', value=attachment, inline=False)

            await send_channel.send(embed=e)

        except Exception as e:
            log.error(e)

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

            # Creating Embed
            e = emb.gen_embed_orange("Edited Message Log", "")
            e.add_field(name='Channel', value=oc, inline=True)
            e.add_field(name='Author', value=author, inline=True)
            e.add_field(name='Before', value=oldContent, inline=False)
            e.add_field(name='After', value=newContent, inline=False)

            if attachment:
                e.add_field(name='Attachments', value=attachment, inline=False)

            await send_channel.send(embed=e)
        except Exception as e:
            log.error(e)

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
            log.error(e)


def setup(bot):
    bot.add_cog(Logging(bot))
