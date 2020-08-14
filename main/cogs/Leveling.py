#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import sys
import os
import asyncpg

# Third party imports
import discord # noqa
from discord.ext import commands
import re
import random
import tabulate

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)
from settings import embeds as emb # noqa


# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------

# this tells the total exp needed to get to the next level.
# each level takes 50 more exp than the previous one. So level up at 100, 250, 450...
def level_up(level):

    basexp = 400
    inc = 50

    return int(basexp*level + inc*level*(level-1)/2)


# we use a while cycle to check the possibility of multiple level-ups at a single time.
# this function returns the new level as an integer, and sends an embed to the channel for each new level and role.
async def leveling_up(channel, guild, conn, member, level, newexp):

    leveling = True
    level += 1
    string = ""

    try:
        while leveling:

            fetchrole = await conn.fetch("""SELECT * FROM roles WHERE level = $1 AND server_id = $2;""", level, guild.id)

            if (fetchrole != []):
                await member.add_roles(guild.get_role(fetchrole[0]["role_id"]))
                string = string + member.name+" reached level "+str(level)+" and is now a "+fetchrole[0]["rolename"]+".\n"
            else:
                string = string + member.name+" reached level "+str(level)+".\n"
            
            nexp = level_up(level)
            if (newexp > nexp):
                level += 1
            else:
                leveling = False

        string = string + "Congratulations!"
        response = emb.gen_embed_cobalt("", string)
        await channel.send(embed=response)
    except Exception as e:
        print(e)  
    
    return int(level)
    




# postgre is smart and takes in the datetime.datetime object directly

# --------------------------------------------------------------------------
#                                 Main
# --------------------------------------------------------------------------
class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


# Listener that checks every message and awards exp accordingly.
    @commands.Cog.listener()
    async def on_message(self, message):
        
        regex = "^[^\"\'\.\w]"

        if re.search(regex, message.content):          
            return
        if message.author.bot:
            return 

        conn = self.bot.pool

        guild = message.guild
        author = message.author
        time = message.created_at

        try:

            fetch = await conn.fetch("""SELECT * FROM lb WHERE server_id = $1 AND user_id = $2; """, guild.id, author.id )

        # case 1: this is the first message by this member; an entry is created in the database.
            if ( fetch == [] ):

                newexp = random.randint(15,30)
                await conn.execute("""INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )""", guild.id, author.id, time, 1, newexp, 1)

                string = "Welcome to this server, "+author.name+"!\n"+author.name+" is now level 1."
                response = emb.gen_embed_cobalt("A new adventure is starting.", string)
                await message.channel.send(embed=response)
                return

        # case 2: less than one minute has passed since this member's last message: no exp is awarded
            if( ( time - fetch[0]["last_exp"] ).seconds < 60 ):

                await conn.execute("""UPDATE lb SET msg_amt = $1 WHERE server_id = $2 AND user_id = $3""", fetch[0]["msg_amt"]+1, guild.id, author.id)
                return
        
        # case 3: awarding new exp. Then,    
            newexp = fetch[0]["total_exp"] + random.randint(15,30)
            level = fetch[0]["level"]

        # if the awarded exp is enough to level up, call leveling_up
            if ( newexp >= level_up(level)):

                newlevel = await leveling_up(message.channel, guild, conn, author, level, newexp)

                await conn.execute("""UPDATE lb SET msg_amt = $1, total_exp = $2, last_exp = $3, level = $4 WHERE server_id = $5 AND user_id = $6""", fetch[0]["msg_amt"]+1, newexp, time, newlevel, guild.id, author.id)

        # otherwise, silently add the awarded exp to the database.
            else:
                await conn.execute("""UPDATE lb SET msg_amt = $1, total_exp = $2, last_exp = $3 WHERE server_id = $4 AND user_id = $5""", fetch[0]["msg_amt"]+1, newexp, time, guild.id, author.id)
                        
        except Exception as e:
            print(e)


# 
    @commands.command(name="givexp")
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, member:discord.Member, exp:int):

    # checking that the given exp is a positive number
        if (exp < 0):
            response = emb.gen_embed_red("Warning!", "You can't give negative exp.")
            await ctx.send(embed=response)
            return
        if (exp == 0):
            response = emb.gen_embed_cobalt("", member.name + " was given 0 exp. Nothing to write home about...")
            await ctx.send(embed=response)
            return

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE server_id = $1 AND user_id = $2; """, ctx.guild.id, member.id )

        # check if the member has an entry in the database; otherwise, a new entry is created.
            if ( fetch == [] ):
                await conn.execute("""INSERT INTO lb VALUES ( $1, $2, $3, $4, $5, $6 )""", ctx.guild.id, member.id, ctx.message.created_at, 1, 0, 0)
                string = "Welcome to this server, "+member.name+"!\n"+member.name+" is now level 1."
                response = emb.gen_embed_cobalt("A new adventure is starting.", string)
                await ctx.send(embed=response)

                newexp = exp
                level = 1
               
            else:
        # send a message to verify that exp has been awarded.
                string = member.name+" was given "+str(exp)+" exp!"
                response = emb.gen_embed_cobalt("", string)
                await ctx.send(embed=response)

                newexp = fetch[0]["total_exp"] + exp
                level = fetch[0]["level"]

        # if the awarded exp is enough to level up, call leveling_up 
            if ( newexp >= level_up(level)):
                newlevel = await leveling_up(ctx.channel, ctx.guild, conn, member, level, newexp)
                await conn.execute("""UPDATE lb SET total_exp = $1, last_exp = $2, level = $3 WHERE server_id = $4 AND user_id = $5""", 
                                 newexp, ctx.message.created_at, newlevel, ctx.guild.id, member.id)
        # otherwise, silently add the awarded exp to the database.
            else:
                await conn.execute("""UPDATE lb SET total_exp = $1, last_exp = $2 WHERE server_id = $3 AND user_id = $4""", newexp, ctx.message.created_at, ctx.guild.id, member.id)

        except Exception as e:
            print(e)






    @commands.command(name="myexp")
    async def myexp(self, ctx):

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE user_id = $1; """, ctx.author.id )

            if ( fetch == [] ):
                await ctx.send("Sorry, who?")
                return

            exp = 0
            texp = 0
            here = False

            for fetched in fetch:
                texp += fetched["total_exp"]           
                if( fetched["server_id"] == ctx.guild.id):
                    here = True
                    here_fetch = fetched

            if here==True:
                exp = here_fetch["total_exp"]
                level = here_fetch["level"]
                nexp = level_up(level)
                missexp = nexp - exp

                string = "You have "+str(texp)+" exp overall.\n\n"
                string = string + "You are level "+str(level)+" on this server, with "+str(exp)+" exp. You last gained exp "+str(( ctx.message.created_at - here_fetch["last_exp"] ).seconds)+" seconds ago.\n"
                string = string + "Level "+str(level+1)+" requires "+str(nexp)+" exp: you need "+str(missexp)+ " more."
                if( missexp < 50 ): string = string + " You are so close!"

            else:
                string = "Your adventure on this server hasn't started yet, but you have "+str(texp)+" exp somewhere else.\n"

            response = emb.gen_embed_cobalt("Your exp", string)
            await ctx.send(embed=response)
           
        except Exception as e:
            print(e)


    @commands.command(name="theirexp")
    @commands.has_permissions(administrator=True)
    async def theirexp(self, ctx, member:discord.Member):

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE user_id = $1; """, member.id )

            if ( fetch == [] ):
                response = emb.gen_embed_red("Warning!", "This adventurer doesn't have any exp anywhere.")
                await ctx.send(embed=response)
                return

            exp = 0
            texp = 0
            here = False

            for fetched in fetch:
                texp += fetched["total_exp"]           
                if( fetched["server_id"] == ctx.guild.id):
                    here = True
                    here_fetch = fetched

            if here==True:
                exp = here_fetch["total_exp"]
                level = here_fetch["level"]
                nexp = level_up(level)
                missexp = nexp - exp

                string = "They have "+str(texp)+" exp overall.\n\n"
                string = string + "They are level "+str(level)+" on this server, with "+str(exp)+" exp. They last gained exp "+str(( ctx.message.created_at - here_fetch["last_exp"] ).seconds)+" seconds ago.\n"
                string = string + "Level "+str(level+1)+" requires "+str(nexp)+" exp: they need "+str(missexp)+ " more."
                if( missexp < 50 ): string = string + " They are so close..."

            else:
                string = member.name+"'s adventure on this server hasn't started yet, but they have "+str(texp)+" exp somewhere else.\n"

            response = emb.gen_embed_cobalt(member.name+"'s exp", string)
            await ctx.send(embed=response)
           
        except Exception as e:
            print(e)





    @commands.command(name="levels")
    async def levels(self, ctx, max:int=10):

        string = "To level 1: 0 exp\n"

        for i in range(1, max):

            string = string+"To level "+str(i+1)+": "+str(level_up(i))+" exp\n"

        response = emb.gen_embed_cobalt("Exp requirements by level", string)
        await ctx.send(embed=response)




    @commands.command(name="ranking")
    async def ranking(self, ctx, max:int=10):

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM lb WHERE server_id = $1 ORDER BY total_exp DESC;""", ctx.guild.id)

            if ( fetch == [] ):
                response = emb.gen_embed_red("Warning!", "There are no adventurers in this server.")
                await ctx.send(embed=response)
                return
            
            rank = 0
            
            table = []

            for fetched in fetch:
                rank = rank+1
                line = [ rank, ctx.guild.get_member(fetched["user_id"]).name, fetched["level"] ]
                table.append(line)

            headers=["Rank", "Name", "Level"]
            content = tabulate.tabulate(table, headers, tablefmt="simple", stralign="left", numalign="center")
            response = emb.gen_embed_cobalt("Ranking", "```"+content+"```")
            await ctx.send(embed=response)

        except Exception as e:
            print(e)


##############################################################################################################à
# Database stuff


# command to drop tables - useful in testing phase when you need to reset it all
    @commands.command(name="drop")
    @commands.has_permissions(administrator=True)
    async def drop(self, ctx, db:str):

        conn = self.bot.pool

        try:
            if ( db == "lb"):
                await conn.execute("""DROP TABLE lb;""")
                response = emb.gen_embed_red("Warning!", "Table lb deleted.")
                await ctx.send(embed=response)

            elif ( db == "roles"):
    
                fetchrole = await conn.fetch("""SELECT * FROM roles""")

                print(fetchrole)
                for fetched in fetchrole:
                    await self.bot.get_guild(fetched["server_id"]).get_role(fetched["role_id"]).delete()

                await conn.execute("""DROP TABLE roles;""")
                response = emb.gen_embed_red("Warning!", "Table roles deleted.")
                await ctx.send(embed=response)

            else:
                response = emb.gen_embed_red("Warning!", "That's not a table.")
                await ctx.send(embed=response)
      
        
        except Exception as e:
            print(e)



# command that makes a list of the roles available in the server
    @commands.command(name="roles")
    async def roles(self, ctx, *args):

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM roles WHERE server_id = $1 ORDER BY level ASC;""", ctx.guild.id)

            if ( fetch == [] ):
                response = emb.gen_embed_red("Warning!", "There are no roles yet.\nYou can add roles using 'createrole Name Level (Colour)'.")
                await ctx.send(embed=response)
                return
            
            table = []
            for fetched in fetch:
                line = [fetched["rolename"], fetched["level"]]
                table.append(line)
            headers=["Role", "Level"]
            content = tabulate.tabulate(table, headers, tablefmt="simple", stralign="left", numalign="right")

            response = emb.gen_embed_cobalt("Roles on this server:", "```"+content+"```")
            await ctx.send(embed=response)

        except Exception as e:
            print(e)


# creating a enw role
# Note: missing a check on current players to assign the new role to those who deserve it
    @commands.command(name="createrole")
    @commands.has_permissions(administrator=True)
    async def createrole(self, ctx, rolename:str, level:int, colour:discord.Colour=discord.Colour.default()):

        conn = self.bot.pool

        try:
        # checking if the role already exists, or if there is another role at that level
            fetch = await conn.fetch("""SELECT * FROM roles WHERE rolename = $1 AND server_id = $2""", rolename, ctx.guild.id)
            if ( fetch != [] ):
                response = emb.gen_embed_red("Warning!", "This rolename already exists.")
                await ctx.send(embed=response)
                return

            fetch = await conn.fetch("""SELECT * FROM roles WHERE level = $1 AND server_id = $2;""", level, ctx.guild.id)
            if ( fetch != [] ):
                response = emb.gen_embed_red("Warning!", "There already is a role at this level.")
                await ctx.send(embed=response)
                return

        # creating a new role in the server (note: this doesn't check if another role with the same name already exists).
            role = await ctx.guild.create_role(name=rolename, colour=colour)

        # creating a new role in the database and linking to the server role by id
            await conn.execute("""INSERT INTO roles VALUES ( $1, $2, $3, $4 )""", rolename, ctx.guild.id, role.id, level)
  
            response = emb.gen_embed_cobalt("Well done!", "New role created!")
            await ctx.send(embed=response)    
            
        except Exception as e:
            print(e)


# this function deletes both the discord server role and the database role.
    @commands.command(name="deleterole")
    @commands.has_permissions(administrator=True)
    async def deleterole(self, ctx, rolename:str):

        conn = self.bot.pool

        try:
            fetch = await conn.fetch("""SELECT * FROM roles WHERE rolename = $1 AND server_id = $2;""", rolename, ctx.guild.id)
            if ( fetch == [] ):
                response = emb.gen_embed_red("Warning!", "This is not a leveling role.")
                await ctx.send(embed=response)
                return

            print(fetch)

            await ctx.guild.get_role(fetch[0]["role_id"]).delete()

            await conn.execute("""DELETE FROM roles WHERE rolename = $1;""", rolename)

            response = emb.gen_embed_cobalt("Well done!", "The role has been deleted.")
            await ctx.send(embed=response) 
            
        except Exception as e:
            print(e)







def setup(bot):
    bot.add_cog(Leveling(bot))


# SQL queries

# SELECT * FROM lb
# SELECT total_exp, level FROM lb (returns all records, showing the requested entries)
# SELECT * FROM lb WHERE total_exp > 100 AND level < 2;
# INSERT INTO lb VALUES (server_id, user_id, msg_amt, total_exp, level)
#
#
#
#

# execute does a straight SQL query but can't return anything. Or can it? Also, it can take arguments from the function.
#
#
#
#
#
#
