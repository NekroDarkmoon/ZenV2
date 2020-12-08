#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import random
import sys
import os
import traceback

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
class Wildemount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Cog check
    async def cog_check(self, ctx):
        guilds = [719063399148814418, 739684323141353597]
        return True if ctx.guild.id in guilds else False

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Creating an lfg
    @commands.command(name="clfg", help="Create a post for a game.",
                      usage="d/p Description")
    async def clfg(self, ctx, post_type, *, msg):
        await ctx.message.delete()

        # validation
        if post_type.lower() == 'p':
            post_type = "Player"
        elif post_type.lower() == 'd':
            post_type = "DM"
        else:
            response = emb.gen_embed_yellow('Error', 'Usage: &clfg p/d Description')
            await ctx.send(embed=response)
            return

        if len(msg) < 5:
            response = emb.gen_embed_yellow('Error', 'Description must be longer than 5 words.')
            await ctx.send(embed=response)
            return

        # Getting variables
        author = ctx.author.name + '#' + ctx.author.discriminator
        post_id = random.randint(0, 10000000)
        server_id = ctx.guild.id

        # data_tuple = (server_id, post_id, author, post_type, msg)

        sql = """INSERT INTO quest(server_id, quest_id, author, quest_type, msg)
                 VALUES($1, $2, $3, $4, $5)"""

        try:
            await self.bot.pool.execute(sql, server_id, post_id, author, post_type, msg)
            response = emb.gen_embed_green(
                                        f'Looking for game - {post_id} ',
                                        f'Entry successfully created.\n\n**{author}**\n{msg}')
            await ctx.send(embed=response)
        except Exception as e:
            print("Failed to enter data", e)
            await ctx.send(embed=emb.gen_embed_orange("Error", "Internal Error Occured"))

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Looking up an lfg
    @commands.command(name="lfg", help="List all lfg quests", usage="d/p Description")
    async def lfg(self, ctx, quest_id=None):
        await ctx.message.delete()

        sql = """SELECT * FROM quest WHERE server_id=$1"""
        try:
            rows = await self.bot.pool.fetch(sql, ctx.guild.id)
        except Exception as e:
            print("Failed to read data from sqlite table", e)
            await ctx.send(embed=emb.gen_embed_orange("Error", "Internal Error Occured"))
            return

        # Validation
        if len(rows) == 0:
            response = emb.gen_embed_yellow("Looking for a Game", "No quests exist on this server")
            await ctx.send(embed=response)
            return

        if quest_id is not None:
            try:
                quest_id = int(quest_id)
            except ValueError:
                response = emb.gen_embed_yellow('LFG', 'Error. Please enter a number.')
                await ctx.send(embed=response)
                return

            sql = """SELECT * FROM quest WHERE server_id=$1 AND quest_id=$2"""

            try:
                record = await self.bot.pool.fetchrow(sql, ctx.guild.id, quest_id)
            except Exception as e:
                print("Failed to read data from Database", e)
                await ctx.send(embed=emb.gen_embed_orange("Error", "Internal Error Occured"))
                return
                print(record)
                if record is None:
                    response = emb.gen_embed_yellow('LFG', 'Error. No such quest exists.')
                    await ctx.send(embed=response)
                    return

            e = emb.gen_embed_green(f"Quest ID: {record[1]}", "")
            e.add_field(name="Quest Giver", value=f"{record[2]}", inline=True)
            e.add_field(name="Profession", value=f"{record[3]}", inline=True)
            e.add_field(name="Quest", value=f"{record[4]}", inline=False)
            e.add_field(name="Date posted", value=record[5], inline=False)
            await ctx.send(embed=e)
            return

        if len(rows) > 10:
            e = emb.gen_embed_green('Quests Available',
                                    "You can select view the following quests via `&lfg quest_id`")
            for record in rows:
                desc = record[4].replace("`", "").replace('\n', "")
                desc = f"{record[5]} - {desc[:40]}...\n"
                e.add_field(name=f'Quest #{record[1]} by a {record[3]}', value=desc, inline=False)

                if (len(e.fields)) > 20:
                    await ctx.send(embed=e)
                    e.clear_fields()

            await ctx.send(embed=e)

        else:
            for record in rows:
                e = emb.gen_embed_green(f"Quest ID: {record[1]}", "")
                e.add_field(name="Quest Giver", value=f"{record[2]}", inline=True)
                e.add_field(name="Profession", value=f"{record[3]}", inline=True)
                e.add_field(name="Quest", value=f"{record[4]}", inline=False)
                e.add_field(name="Date posted", value=record[5], inline=False)
                await ctx.send(embed=e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Deleting an lfg
    @commands.command(name="dlfg", help="Delete a posted quest", usage="QuestID")
    async def dlfg(self, ctx, quest_id=None):
        await ctx.message.delete()

        # Get vars
        author = ctx.author.name + '#' + ctx.author.discriminator

        # Validation
        if quest_id is None:
            response = emb.gen_embed_yellow('LFG', 'Please enter a QuestID')
            await ctx.send(embed=response)
            return

        try:
            quest_id = int(quest_id)
        except ValueError:
            await ctx.send(embed=emb.gen_embed_orange('LFG - Error',
                                                      'Error. Please enter a number.'))
            return

        sql = """SELECT * FROM quest WHERE server_id=$1 AND quest_id=$2"""
        try:
            record = await self.bot.pool.fetchrow(sql, ctx.guild.id, quest_id)
        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())
            await ctx.send(embed=emb.gen_embed_orange("Error", "Internal Error Occured"))
            return

        permissions = ctx.author.guild_permissions

        try:
            if (author != record[2]) and not permissions.administrator:
                await ctx.send(embed=emb.gen_embed_yellow("LFG - Error",
                                                          "You're not the author of the quest."))
                return
        except Exception:
            return

        sql = """DELETE FROM quest WHERE server_id=$1 AND quest_id=$2"""

        try:
            await self.bot.pool.execute(sql, ctx.guild.id, quest_id)
            desc = f"Deleted quest ID'ed {quest_id} by {author}"
            response = emb.gen_embed_green('Looking for game', desc)
            await ctx.send(embed=response)
        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())
            await ctx.send(embed=emb.gen_embed_orange("Error", "Internal Error Occured"))
            return

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                                   CPC
    @commands.command(name="playchn", help="List all lfg quests")
    async def playchn(self, ctx, *args):
        await ctx.message.delete()
        # Get vars
        server = ctx.guild
        author = ctx.author
        delete_query = False
        exit_query = False

        # Initial Validation
        if len(args) > 15:
            response = emb.gen_embed_yellow('Error', 'Max of 9 Players allowed.')
            await ctx.send(embed=response)
            return

        channel_name = f"{author.name}s game"
        channel_name = channel_name.lower().replace(' ', '-')
        cat_chns = getattr(server, 'categories', None)
        for chn in cat_chns:
            if chn.name == 'Play Channels':
                category = chn

        # Validation
        channels = getattr(server, 'channels', None)

        ids = []
        for arg in args:
            if len(args) == 1 and arg == '-d':
                delete_query = True
            elif len(args) != 1 and arg == '-d':
                await ctx.send(embed=emb.gen_embed_yellow('Error', 'Invalid Arguments'))
                return
            elif arg.startswith('<@!'):
                ids.append(arg.replace('<@!', '').replace('>', ''))

        # The weird delete query and validation query
        for channel in channels:
            if channel.name == channel_name:
                if delete_query:
                    try:
                        await channel.delete()
                        await ctx.send(embed=emb.gen_embed_green(author.name,
                                       f'{channel.name} Deleted'), delete_after=5)
                        exit_query = True
                    except Exception as e:
                        log.warning(e)
                        log.error(traceback.format_exc())
                else:
                    e = 'You already have an existing play channel. Unable to create more than one.'
                    e += '\nPinging a Crownsguard for help'
                    response = emb.gen_embed_yellow('Error', e)
                    try:
                        await ctx.send('<@!157433182331863040>', embed=response)
                        exit_query = True
                        break
                    except Exception as e:
                        log.warning(e)
                        log.error(traceback.format_exc())

        if exit_query or delete_query:
            return

        # Getting members
        users = []
        for id in ids:
            users.append(await self.bot.fetch_user(id))

        # Setting permissions
        overwrites = {
            server.default_role: discord.PermissionOverwrite(send_messages=False),
            author: discord.PermissionOverwrite(send_messages=True)
            }

        audio_overwrites = {
            server.default_role: discord.PermissionOverwrite(speak=True),
            author: discord.PermissionOverwrite(speak=False)
            }

        for user in users:
            overwrites.update({user: discord.PermissionOverwrite(send_messages=True)})
            audio_overwrites.update(
                {user: discord.PermissionOverwrite(speak=True)}
                )

        try:
            channel = await server.create_text_channel(channel_name, overwrites=overwrites,
                                                       category=category)
            await server.create_voice_channel(channel_name, category=category)
            response = emb.gen_embed_green('Game Channel', 'Created respective channels.')
            await ctx.send(channel.mention, embed=response)
        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                       Setting up channel restrictions
    @commands.Cog.listener()
    async def on_message(self, message):

        # Validate
        if message.author.bot:
            return

        try:
            roles = message.author.roles
        except Exception:
            print(f"User {message.author} has no roles.")
            return

        for role in roles:
            if role.name == 'Exceptions':
                return

        response = emb.gen_embed_orange("Error",
                                        "Please add relevant tags to your post.")

        if (message.channel.id == 719063951442313307) or (message.channel.id == 719070160014803045):
            content = message.content
            if "[" in content and "]" in content:
                pass
            else:
                await message.delete(delay=5)
                await self.bot.get_channel(message.channel.id).send(embed=response,
                                                                    delete_after=10)

        if (message.channel.id == 746124528312385576):
            content = message.content
            temp = "[entry]"
            if temp in content.lower():
                await message.add_reaction('\<:upvote:741279182109147286>') # noqa

                # Get vars
                author = message.author.name
                with open('event.txt', 'a') as fp:
                    msg = f"Author: {author}\n"
                    msg += f"Hook: \n {content} \n"
                    msg += "-------------------------------------------------------\n\n"
                    fp.write(msg)

            else:
                e = emb.gen_embed_red('Error',
                                      'Please mark your entry with [Entry]')
                await message.delete(delay=8)
                await self.bot.get_channel(message.channel.id).send(embed=e, delete_after=10)


def setup(bot):
    bot.add_cog(Wildemount(bot))
