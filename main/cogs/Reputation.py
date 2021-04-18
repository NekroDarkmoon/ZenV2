#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import logging
import os
import sys
import re
import sys
import traceback
import time

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
#                                 Main
# --------------------------------------------------------------------------
class Reputation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = list()

    #  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Give rep
    @commands.command(name="giverep")
    async def giverep(self, ctx, member: discord.Member, rep: int = 1):
        """ Gives another member rep. (Max of 1)
        
        Usage: `giverep "username"/@mention/id rep`
        """

        # Set Varaibles
        author = ctx.author
        conn = self.bot.pool
        roles = ctx.author.roles
        is_admin = False

        await ctx.message.delete()

        for role in roles:
            if role.name == "Admin":
                is_admin = True

        # Validation
        if rep == 0:
            e = emb.gen_embed_cobalt("Eh?",
                                     f"{member.name} was given 0 rep??")
            await ctx.send(embed=e, delete_after=5)
            return
        
        if member.bot:
            await ctx.send("`Can't give rep to a bot.`")
            return
        
        if not is_admin and (ctx.author.id == member.id):
            e = emb.gen_embed_red("Hunh",
                                  "Sneakily trying to give yourself xp eh.")
            await ctx.send(embed=e, delete_after=5)
            return
        
        for elem, user in enumerate(self.cooldown):
            curr_time = time.time()
            if user[0] == author.id and (curr_time - user[1]) < 120:
                e = emb.gen_embed_red("Cooldown",
                                       f"Currently in cooldown.")
                await ctx.send(embed=e, delete_after=5)
                return
            elif user[0] == author.id and (curr_time - user[1] > 120):
                print("Removing from cooldown")
                self.cooldown.pop(elem)
            else:
                pass

        if not is_admin and (rep > 1 or rep < 0):
            e = emb.gen_embed_red("Eh??", f"Unable to give more than 1 rep.")
            await ctx.send(embed=e, delete_after=5)
            return 
        
        try:
            sql = """INSERT INTO rep (server_id, user_id, rep)
                    VALUES ($1, $2, $3)
                    ON CONFLICT ON CONSTRAINT server_user 
                    DO UPDATE SET rep = rep.rep + $3;"""
            
            await conn.execute(sql, ctx.guild.id, member.id, rep)
            e = emb.gen_embed_green("Rep",
                                    f"Gave {member.name} {rep} rep.")
            
            await ctx.send(embed=e, delete_after=5)
            
            if not is_admin:
                curr_time = time.time()
                self.cooldown.append((author.id, curr_time))

        except Exception as e:
            log.error(traceback.format_exc())

    #  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Get Rep
    @commands.command(name="rep")
    async def rep(self, ctx, member: discord.Member = None):
        """Displays the Reputation of a user.
        
        Usage: `giverep "username"/@mention/id`
        Note: Leave arguments empty to display your own rep.
        """
    
        # Validation
        if member == None:
            member = ctx.author
        
        # Variables
        conn = self.bot.pool
        
        try:
            sql = """ SELECT * FROM rep WHERE server_id=$1 AND user_id=$2;"""
            fetch = await conn.fetchrow(sql, ctx.guild.id, member.id)
        except Exception as e:
            log.error(traceback.format_exc())

        if fetch is None:
            rep = 0
        else:
            rep = fetch[2]

        message = f"Member {member.name} has `{rep}` rep."
        await ctx.send(message)


    #  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Set Rep
    @commands.command(name="setrep")
    @commands.has_permissions(administrator=True)
    async def setrep(self, ctx, member: discord.Member, rep: int):
        """ Set rep for a particular member
        
        Usage: `setrep "username/@mention/id rep"`
        """

        # Variables
        conn = self.bot.pool

        try:
            sql = """INSERT INTO rep (server_id, user_id, rep)
                    VALUES ($1, $2, $3)
                    ON CONFLICT ON CONSTRAINT server_user 
                    DO UPDATE SET rep = $3;"""
            
            await conn.execute(sql, ctx.guild.id, member.id, rep)
            e = emb.gen_embed_green("Rep",
                                    f"Set {member.name}'s rep to {rep}.")
            
            await ctx.send(embed=e, delete_after=5)
        except Exception as e:
            log.error(traceback.format_exc())



    #  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #                          Rank rep
    @commands.command(name="toprep")
    async def toprep(self, ctx, page: int = 1):
        """ Displays the ranking by reputation.
        
        Usage: `toprep (page_num)` 
        """        
        
        # Validation
        if page < 1:
            return

        # Variables
        conn = self.bot.pool

        try:
            sql = """SELECT * FROM rep WHERE server_id=$1 ORDER BY rep.rep DESC;"""
            fetch = await conn.fetch(sql, ctx.guild.id)
        except Exception as e:
            log.error(traceback.format_exc())
        
        if fetch is []:
            message = "No one in this server has reputation points."
            await ctx.send(message)
            return
        
        table = list()

        if len(fetch) < (15*(page-1)):
            message = f"Not enough users with rep to display page {page}"
            await ctx.send(message)
            return
    
        fetch = fetch[15*(page-1):]

        for elem, fetched in enumerate(fetch):
            
            elem = elem + 15*(page-1) + 1

            try:
                line = [elem, ctx.guild.get_member(fetched["user_id"]).name, fetched["rep"]]
            except Exception:
                sql = """DELETE FROM rep WHERE server_id=$1 and user_id=$2;"""
                await conn.execute(sql, ctx.guild.id, fetched["user_id"])
                log.warning(f"Deleted {fetched['user_id']} from db")
                continue

            table.append(line)
            if elem > 14:
                break
        
        headers = ["Rank", "Name", "Rep"]
        content = tabulate.tabulate(table, headers, tablefmt="simple", stralign="left",
                                    numalign="center")
        
        if len(content) > 2000:
            await ctx.send("Too many entries. Fix coming soon-ish ")
        
        else:
            e = emb.gen_embed_cobalt("Ranking", f"```{content}```")
            await ctx.send(embed=e)

            
def setup(bot):
    bot.add_cog(Reputation(bot))
