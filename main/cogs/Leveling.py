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
# Level function -- So level up at 100, 250, 450...
def level_up(level):
    basexp = 400
    inc = 200
    return int(basexp*level + inc*level*(level-1)/2)


# Leveling function
async def leveling_up(channel, guild, conn, member, level, newexp):
    leveling = True
    level += 1
    string = ""

    try:
        while leveling:
            fetchrole = await conn.fetch("""SELECT * FROM roles WHERE
                                         level = $1 AND server_id = $2;""",
                                         level, guild.id)

            if (fetchrole != []):
                await member.add_roles(guild.get_role(fetchrole[0]["role_id"]))
                string += member.name+" reached level "+str(level)+" and is now a "
                string += fetchrole[0]["rolename"]+".\n"
            else:
                string = string + member.name+" reached level "+str(level)+".\n"

            nexp = level_up(level)
            if (newexp > nexp):
                level += 1
            else:
                leveling = False

        string += "Congratulations!"
        response = emb.gen_embed_cobalt("", string)
        await channel.send(embed=response, delete_after=10)
    except Exception as e:
        log.error(e)

    return int(level)


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

# Listener that checks every message and awards exp accordingly.
    @commands.Cog.listener()
    async def on_message(self, message):
        regex = "^[^\"\'\.\w]" # noqa

        if re.search(regex, message.content):
            return
        if message.author.bot:
            return

        conn = self.bot.pool

        guild = message.guild
        author = message.author
        time = message.created_at

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE server_id = $1 AND user_id = $2; """,
                                     guild.id, author.id)

        # case 1: this is the first message by this member; an entry is created in the database.
            if (fetch == []):
                newexp = random.randint(15, 25)
                await conn.execute("""INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )""",
                                   guild.id, author.id, time, 1, newexp, 1)

                string = "Welcome to this server, "+author.name+"!\n"+author.name+" is now level 1."
                response = emb.gen_embed_cobalt("A new adventure is starting.", string)
                await message.channel.send(embed=response)
                return

        # case 2: less than one minute has passed since this member's last message: no exp is awarded
            if((time - fetch[0]["last_exp"]).seconds < 60):
                await conn.execute("""UPDATE lb SET msg_amt = $1 WHERE server_id = $2 AND user_id = $3""",
                                   fetch[0]["msg_amt"]+1, guild.id, author.id)
                return

        # case 3: awarding new exp. Then,
            newexp = fetch[0]["total_exp"] + random.randint(15, 25)
            level = fetch[0]["level"]

        # if the awarded exp is enough to level up, call leveling_up
            if (newexp >= level_up(level)):
                newlevel = await leveling_up(message.channel, guild, conn, author, level, newexp)
                sql = """UPDATE lb SET msg_amt = $1,
                                       total_exp = $2,
                                       last_exp = $3,
                                       level = $4 WHERE server_id = $5 AND user_id = $6"""

                await conn.execute(sql, fetch[0]["msg_amt"]+1, newexp,
                                   time, newlevel, guild.id, author.id)

        # otherwise, silently add the awarded exp to the database.
            else:
                sql = """UPDATE lb SET msg_amt = $1,
                                       total_exp = $2,
                                       last_exp = $3 WHERE server_id = $4 AND user_id = $5"""
                await conn.execute(sql, fetch[0]["msg_amt"]+1, newexp, time, guild.id, author.id)

        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Give exp
    @commands.command(name="givexp")
    @commands.has_permissions(administrator=True)
    async def givexp(self, ctx, member: discord.Member, exp: int):
        """Gives another member xp"""
        # Validation
        if (exp < 0):
            response = emb.gen_embed_red("Warning!", "You can't give negative exp.")
            await ctx.send(embed=response)
            return

        if (exp == 0):
            response = emb.gen_embed_cobalt("", member.name +
                                            " was given 0 exp. Nothing to write home about...")
            await ctx.send(embed=response)
            return

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE server_id = $1 AND user_id = $2; """,
                                     ctx.guild.id, member.id)

            # Check if the member has an entry in the database; otherwise, a new entry is created.
            if (fetch == []):
                await conn.execute("""INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )""",
                                   ctx.guild.id, member.id, ctx.message.created_at, 1, 0, 0)

                string = "Welcome to this server, "+member.name+"!\n"+member.name+" is now level 1."

                response = emb.gen_embed_cobalt("A new adventure is starting.", string)
                await ctx.send(embed=response)

                newexp = exp
                level = 1

            else:
                # Send a message to verify that exp has been awarded.
                string = member.name+" was given "+str(exp)+" exp!"
                response = emb.gen_embed_cobalt("", string)
                await ctx.send(embed=response)

                newexp = fetch[0]["total_exp"] + exp
                level = fetch[0]["level"]

            # If the awarded exp is enough to level up, call leveling_up
            if (newexp >= level_up(level)):
                newlevel = await leveling_up(ctx.channel, ctx.guild, conn, member, level, newexp)
                sql = """UPDATE lb SET total_exp = $1,
                                       last_exp = $2,
                                       level = $3 WHERE server_id = $4 AND user_id = $5"""

                await conn.execute(sql, newexp, ctx.message.created_at, newlevel,
                                   ctx.guild.id, member.id)

        # otherwise, silently add the awarded exp to the database.
            else:
                sql = """UPDATE lb SET total_exp = $1,
                                       last_exp = $2 WHERE server_id = $3 AND user_id = $4"""
                await conn.execute(sql, newexp, ctx.message.created_at, ctx.guild.id, member.id)

        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Check exp
    @commands.command(name="rank")
    async def rank(self, ctx):
        """Gets your current status on the server"""
        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE user_id = $1; """, ctx.author.id)

            # Validation
            if (fetch == []):
                response = emb.gen_embed_green("", "Sorry, who?")
                await ctx.send(embed=response)
                return

            exp = 0
            texp = 0
            here = False

            for fetched in fetch:
                texp += fetched["total_exp"]
                if(fetched["server_id"] == ctx.guild.id):
                    here = True
                    here_fetch = fetched

            if here is True:
                exp = here_fetch["total_exp"]
                level = here_fetch["level"]
                nexp = level_up(level)
                missexp = nexp - exp

                string = f"""You have {texp} exp overall.

You are level {level} on this server, with {exp} exp.
You last gained exp {(ctx.message.created_at - here_fetch["last_exp"]).seconds} seconds ago.

Level {level+1} requires {nexp} exp: you need {missexp} more.\n\n"""

            else:
                string = f"Your adventure on this server hasn't started yet, but you have {texp} exp somewhere else.\n"

            # Validation
            if 'nexp' not in locals():
                response = emb.gen_embed_green("", "Sorry, who?")
                await ctx.send(embed=response)
                return

            e = emb.gen_embed_cobalt(f"{ctx.author}", string)
            e.set_thumbnail(url=ctx.author.avatar_url)
            e.add_field(name="XP", value=f"{exp}/{nexp}", inline=True)
            e.add_field(name="Level", value=level, inline=True)
            e.add_field(name="Messages", value=here_fetch["msg_amt"], inline=True)
            await ctx.send(embed=e)

        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Check exp
    @commands.command(name="theirxp")
    @commands.has_permissions(manage_guild=True)
    async def theirxp(self, ctx, member: discord.Member):
        """Gets the exp for another member on the server"""
        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE user_id = $1; """, member.id)

            if (fetch == []):
                response = emb.gen_embed_red("Warning!",
                                             "This adventurer doesn't have any exp anywhere.")
                await ctx.send(embed=response)
                return

            exp = 0
            texp = 0
            here = False

            for fetched in fetch:
                texp += fetched["total_exp"]
                if(fetched["server_id"] == ctx.guild.id):
                    here = True
                    here_fetch = fetched

            if here is True:
                exp = here_fetch["total_exp"]
                level = here_fetch["level"]
                nexp = level_up(level)
                missexp = nexp - exp

                string = f"""You have {texp} exp overall.

You are level {level} on this server, with {exp} exp. You last gained exp
{(ctx.message.created_at - here_fetch["last_exp"] ).seconds} seconds ago.

Level {level+1} requires {nexp} exp: you need {missexp} more."""

            else:
                string = f"{member.name}'s adventure on this server hasn't started yet, but they have {texp} exp somewhere else.\n"

            e = emb.gen_embed_cobalt(f"{member}", string)
            e.set_thumbnail(url=member.avatar_url)
            e.add_field(name="XP", value=f"{exp}/{nexp}", inline=True)
            e.add_field(name="Level", value=level, inline=True)
            e.add_field(name="Messages", value=here_fetch["msg_amt"], inline=True)
            await ctx.send(embed=e)

        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Levels
    @commands.command(name="levels")
    async def levels(self, ctx, max: int = 10):
        """Lists the exp required for levels"""
        string = ""

        if max < 3:
            min = max
        else:
            min = max - 3
        max = max + 3

        for i in range(min, max):
            string += f"To level {i+1}: {level_up(i)} exp\n"

        response = emb.gen_embed_cobalt("Exp requirements by level", string)
        await ctx.send(embed=response)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Ranking
    @commands.command(name="ranking")
    async def ranking(self, ctx, max: int = 10):
        """Lists top 15 ranking on the server"""
        conn = self.bot.pool

        try:
            sql = """SELECT * FROM lb WHERE server_id = $1 ORDER BY total_exp DESC;"""
            fetch = await conn.fetch(sql, ctx.guild.id)

            if (fetch == []):
                response = emb.gen_embed_red("Warning!", "There are no adventurers in this server.")
                await ctx.send(embed=response)
                return

            rank = 0

            table = []

            for fetched in fetch:
                rank = rank + 1
                line = [rank, ctx.guild.get_member(fetched["user_id"]).name, fetched["level"]]
                table.append(line)
                if rank > 15:
                    break

            headers = ["Rank", "Name", "Level"]
            content = tabulate.tabulate(table, headers, tablefmt="simple", stralign="left",
                                        numalign="center")
            response = emb.gen_embed_cobalt("Ranking", "```"+content+"```")
            await ctx.send(embed=response)

        except Exception as e:
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Role rewards
    @commands.command(name="rewards")
    async def rewards(self, ctx, *args):
        """Fetches all the possible rewards for levels"""
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
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Create Role rewards
    @commands.command(name="createrr")
    @commands.has_permissions(manage_guild=True)
    async def createrr(self, ctx, rolename: str, level: int,
                       colour: discord.Colour = discord.Colour.default()):
        """Creates a reward role"""
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
            log.error(e)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                             Delete Role rewards
    @commands.command(name="deleterr")
    @commands.has_permissions(manage_guild=True)
    async def deleterr(self, ctx, rolename: str):
        """Deletes a reward role"""
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
            log.error(e)


def setup(bot):
    bot.add_cog(Leveling(bot))


# SQL queries

# SELECT * FROM lb
# SELECT total_exp, level FROM lb (returns all records, showing the requested entries)
# SELECT * FROM lb WHERE total_exp > 100 AND level < 2;
# INSERT INTO lb VALUES (server_id, user_id, msg_amt, total_exp, level)
#
