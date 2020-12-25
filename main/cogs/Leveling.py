#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import random
import re
import sys
import traceback

# Third party imports
import discord # noqa
from discord.ext import commands
import tabulate

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from settings import embeds as emb # noqa


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------
#                           Level Up Functions
# --------------------------------------------------------------------------
# Claculate level
def level_up(level):
    basexp = 400
    inc = 200
    return int(basexp*level + inc*level*(level-1)/2)


# Leveling Function
async def leveling_up(channel, guild, conn, member, level, newxp):
    leveling = True
    level += 1
    string = ""

    try:
        while leveling:
            sql = """SELECT * FROM roles WHERE level=$1 AND server_id=$2;"""
            fetchrole = await conn.fetchrow(sql, level, guild.id)

            if fetchrole is not None:
                await member.add_roles(guild.get_role(fetchrole[2]))
                string += f"{member.name} reached level {level} and is now a {fetchrole[0]}\n"
            else:
                string += f"{member.name} reached level {level}. \n"

            nxp = level_up(level)
            if newxp > nxp:
                level += 1
            else:
                leveling = False

        string += "Congratulations!"
        e = emb.gen_embed_green("", string)
        await channel.send(embed=e, delete_after=10)

    except Exception as e:
        log.warning(e)
        log.error(traceback.format_exc())

    return int(level)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                            XP Giver
    @commands.Cog.listener()
    async def on_message(self, message):
        regex = "^[^\"\'\.\w]" # noqa

        if re.search(regex, message.content) or message.author.bot:
            return

        conn = self.bot.pool

        guild = message.guild
        author = message.author
        time = message.created_at

        # Try block
        try:
            sql = """SELECT * FROM lb WHERE server_id = $1 AND user_id = $2; """
            fetch = await conn.fetchrow(sql, guild.id, author.id)

            # Case 1: First message by user
            if fetch is None:
                newxp = random.randint(15, 25)
                sql = """INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )"""
                await conn.execute(sql, guild.id, author.id, time, 1, newxp, 1)

                string = f"Welcome to the server, {author.name}! \n{author.name} is now level 1."
                e = emb.gen_embed_cobalt("A new adventure is starting.", string)
                await message.channel.send(embed=e)
                return

            # Case 2: Less than 1 min has elasped since last message.
            if (time - fetch["last_exp"]).seconds < 60:
                sql = """UPDATE lb SET msg_amt = $1 WHERE server_id = $2 AND user_id = $3"""
                await conn.execute(sql, fetch[3]+1, guild.id, author.id)
                return

            # Case 3: Awarding new xp. Then,
            newxp = fetch[4] + random.randint(15, 25)
            level = fetch[5]

            # If leveled up call leveling Function
            if newxp >= level_up(level):
                newlevel = await leveling_up(message.channel, guild, conn, author, level, newxp)
                sql = """UPDATE lb SET msg_amt = $1,
                                       total_exp = $2,
                                       last_exp = $3,
                                       level = $4 WHERE server_id = $5 AND user_id = $6"""

                await conn.execute(sql, fetch[3] + 1, newxp, time, newlevel, guild.id, author.id)

            # Otherwise, silently add the awarded xp to the database
            else:
                sql = """UPDATE lb SET msg_amt = $1,
                                       total_exp = $2,
                                       last_exp = $3 WHERE server_id = $4 AND user_id = $5"""

                await conn.execute(sql, fetch[3] + 1, newxp, time, guild.id, author.id)

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Give xp
    @commands.command(name="givexp")
    @commands.has_permissions(administrator=True)
    async def givexp(self, ctx, member: discord.Member, exp: int):
        """Gives another member xp

        Usage: `givexp "username"/@mention/id xp_amt`"""

        # Validation
        if exp < 0:
            e = emb.gen_embed_red("Warning!", "You can't give negative xp.")
            await ctx.send(embed=e)
            return

        if exp == 0:
            e = emb.gen_embed_cobalt("Eh?",
                                     f"{member.name} was given 0 xp. Nothing to write home about...")
            await ctx.send(embed=e)
            return

        # Set connection
        conn = self.bot.pool

        try:
            sql = """SELECT * FROM lb WHERE server_id=$1 AND user_id=$2;"""
            fetch = await conn.fetchrow(sql, ctx.guild.id, member.id)

            #  If no previous entry
            if fetch is None:
                sql = """INSERT INTO lb VALUES ($1, $2, $3, $4, $5, $6)"""
                await conn.execute(sql, ctx.guild.id, member.id, ctx.message.created_at, 1, 0, 0)
                string = f"Welcome to this server, {member.name}!\n{member.name} is now level 1."

                e = emb.gen_embed_green("A new adventure is starting", string)
                await ctx.send(embed=e)

                newxp = exp
                level = 1

            else:
                string = f"{member.name} was given {exp} exp!"
                e = emb.gen_embed_green("", string)
                await ctx.send(embed=e)

                newxp = fetch[4] + exp
                level = fetch[5]

            # If threshold reached next level
            if newxp >= level_up(level):
                newlevel = await leveling_up(ctx.channel, ctx.guild, conn, member, level, newxp)
                sql = """UPDATE lb SET total_exp = $1,
                                       last_exp = $2,
                                       level = $3 WHERE server_id = $4 AND user_id = $5"""

                await conn.execute(sql, newxp, ctx.message.created_at, newlevel, ctx.guild.id, member.id)

            else:
                sql = """UPDATE lb SET total_exp = $1,
                                       last_exp = $2 WHERE server_id = $3 AND user_id = $4"""

                await conn.execute(sql, newxp, ctx.message.created_at, ctx.guild.id, member.id)

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Check xp
    @commands.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Gets rank on the server

        Usage: `rank id[Optional]`"""

        conn = self.bot.pool

        # Verification
        if member is None:
            member = ctx.author

        try:
            sql = """SELECT * FROM lb WHERE server_id=$1 AND user_id=$2"""
            fetch = await conn.fetchrow(sql, ctx.guild.id, member.id)

            if fetch is None:
                e = emb.gen_embed_red("", "This adventurer doesn't have any xp on this server.")
                await ctx.send(embed=e)
                return

            xp = fetch[4]
            level = fetch[5]
            nxp = level_up(level)
            missxp = nxp - xp

            string = f"You are level {level} on this server, with {xp} xp.\n"
            string += f"You last gained xp {(ctx.message.created_at - fetch[2]).seconds} seconds ago."
            string += f"\n\n Level {level+1} requires {nxp} xp: You need {missxp} more."

            e = emb.gen_embed_cobalt(f"{member}", string)
            e.set_thumbnail(url=member.avatar_url)
            e.add_field(name="XP", value=f"{xp}/{nxp}", inline=True)
            e.add_field(name="Level", value=level, inline=True)
            e.add_field(name="Messages", value=fetch[3], inline=True)
            await ctx.send(embed=e)

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Levels
    @commands.command(name="levels")
    async def levels(self, ctx, max: int = 10):
        """Lists the xp required for levels

        Usage: `levels level`"""
        string = ""

        if max < 3:
            min = max
        else:
            min = max - 3
        max = max + 3

        for i in range(min, max):
            string += f"To level {i+1}: {level_up(i)} xp\n"

        e = emb.gen_embed_cobalt("XP requirements by level", string)
        await ctx.send(embed=e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Ranking
    @commands.command(name="ranking")
    async def ranking(self, ctx, max: int = 15):
        """Lists top 15 ranked adventurers on the server

        Usage: `rank`"""

        conn = self.bot.pool

        try:
            sql = """SELECT * FROM lb WHERE server_id=$1 ORDER BY total_exp DESC;"""
            fetch = await conn.fetch(sql, ctx.guild.id)
        except Exception as e:
            print(e)

        if fetch == []:
            e = emb.gen_embed_red("Warning!", "There are no adventurers in this guild.")
            await ctx.send(embed=e)
            return

        rank = 1
        table = []

        for fetched in fetch:
            try:
                line = [rank, ctx.guild.get_member(fetched["user_id"]).name, fetched["level"]]
            except Exception:
                sql = """DELETE FROM lb WHERE server_id=$1 and user_id=$2;"""
                await conn.execute(sql, ctx.guild.id, fetched["user_id"])
                log.warning(f"Deleted {fetched['user_id']} from db")
                continue

            table.append(line)
            if rank > max:
                break
            else:
                rank += 1

        headers = ["Rank", "Name", "Level"]
        content = tabulate.tabulate(table, headers, tablefmt="simple", stralign="left",
                                    numalign="center")

        if len(content) > 2000:
            await ctx.send("Too many entries. Fix coming soon-ish.")

        else:
            e = emb.gen_embed_cobalt("Ranking", f"```{content}```")
            await ctx.send(embed=e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Role rewards
    @commands.command(name="rewards")
    async def rewards(self, ctx, *args):
        """Fetches all the possible rewards for levels

        Usage: `rewards`"""

        conn = self.bot.pool

        try:
            sql = """SELECT * FROM roles WHERE server_id = $1 ORDER BY level ASC;"""
            fetch = await conn.fetch(sql, ctx.guild.id)

            if (fetch == []):
                response = emb.gen_embed_red("Warning!", """There are no roles yet.
You can add roles using 'createrole Name Level (Colour)'.""")
                await ctx.send(embed=response)
                return

            table = []
            for fetched in fetch:
                line = [fetched["rolename"], fetched["level"]]
                table.append(line)

            headers = ["Role", "Level"]
            content = tabulate.tabulate(table, headers, tablefmt="simple", stralign="left",
                                        numalign="right")

            response = emb.gen_embed_cobalt("Roles on this server:", f"```{content}```")
            await ctx.send(embed=response)

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Create Role rewards
    @commands.command(name="createrr")
    @commands.has_permissions(manage_guild=True)
    async def createrr(self, ctx, rolename: str, level: int,
                       colour: discord.Colour = discord.Colour.default()):
        """Creates a reward role

        Usage: `createrr rolename level colour`"""

        conn = self.bot.pool
        try:
            # checking if the role already exists, or if there is another role at that level
            sql = """SELECT * FROM roles WHERE rolename = $1 AND server_id = $2"""
            fetch = await conn.fetch(sql, rolename, ctx.guild.id)

            if (fetch != []):
                response = emb.gen_embed_red("Warning!", "This rolename already exists.")
                await ctx.send(embed=response)
                return

            fetch = await conn.fetch("""SELECT * FROM roles WHERE level = $1 AND server_id = $2;""",
                                     level, ctx.guild.id)

            if (fetch != []):
                response = emb.gen_embed_red("Warning!", "There already is a role at this level.")
                await ctx.send(embed=response)
                return

            # Creating a new role in the server
            # (note: this doesn't check if another role with the same name already exists).
            role = await ctx.guild.create_role(name=rolename, colour=colour)

            # creating a new role in the database and linking to the server role by id
            await conn.execute("""INSERT INTO roles VALUES ( $1, $2, $3, $4 )""", rolename,
                               ctx.guild.id, role.id, level)

            response = emb.gen_embed_cobalt("Well done!", "New role created!")
            await ctx.send(embed=response)

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Delete Role rewards
    @commands.command(name="deleterr")
    @commands.has_permissions(manage_guild=True)
    async def deleterr(self, ctx, rolename: str):
        """Deletes a reward role

        Usage: deleterr rolename"""

        conn = self.bot.pool

        try:
            sql = """SELECT * FROM roles WHERE rolename = $1 AND server_id = $2;"""
            fetch = await conn.fetch(sql, rolename, ctx.guild.id)

            if (fetch == []):
                response = emb.gen_embed_red("Warning!", "This is not a leveling role.")
                await ctx.send(embed=response)
                return

            await ctx.guild.get_role(fetch[0]["role_id"]).delete()

            await conn.execute("""DELETE FROM roles WHERE rolename = $1;""", rolename)

            response = emb.gen_embed_cobalt("Well done!", "The role has been deleted.")
            await ctx.send(embed=response)

        except Exception as e:
            log.warning(e)
            log.error(traceback.format_exc())


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Leveling(bot))
