#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import sys
import os

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
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @commands.command(name="kick", pass_context=True, help="Kicks a user from the server")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kicks a member from the server."""

        if reason is None:
            reason = f"Kicked by {ctx.author}\nID: {ctx.author.id}"

        e = emb.gen_embed_white(f'Kicked {member}', reason)
        e.set_thumbnail(url=member.avatar_url)

        try:
            await ctx.guild.kick(member, reason=reason)
            await ctx.message.delete()
            await ctx.send(embed=e)
        except Exception as e:
            print(e)
            embed = emb.gen_embed_orange('Error', e)
            await ctx.send(embed=embed)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @commands.command(name="ban", pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True, help="Bans the user from the server.")
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Bans a member from the server."""
        if reason is None:
            reason = f"Banned by {ctx.author}\nID: {ctx.author.id}"

        e = emb.gen_embed_white(f'Banned {member}', reason)

        try:
            await ctx.guild.ban(member, reason=reason)
            await ctx.message.delete()
            await ctx.send(embed=e)
        except Exception as e:
            print(e)
            embed = emb.gen_embed_orange('Error', e)
            await ctx.send(embed=embed)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @commands.command(name="unban", pass_context=True)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True, help="Unbans the user from the server")
    async def unban(self, ctx, member: discord.Member, *, reason=None):
        """Unbans a member from the server"""
        if reason is None:
            reason = f"Unbanned by {ctx.author}.\nID: {ctx.author.id}"

        e = emb.gen_embed_white(f'Unbanned {member}', reason)

        try:
            await ctx.guild.unban(member, reason=reason)
            await ctx.message.delete()
            await ctx.send(embed=e)
        except Exception as e:
            print(e)
            embed = emb.gen_embed_orange('Error', e)
            await ctx.send(embed=embed)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @commands.command(name="userinfo", pass_context=True)
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member):
        """Displays information about a user"""
        try:
            # Variables
            roles = [role.name.replace('@', '@\u200b') for role in getattr(member, 'roles', [])]
            shared = sum(g.get_member(member.id) is not None for g in self.bot.guilds)

            embed = discord.Embed()
            embed.set_author(name=member)
            embed.add_field(name='ID', value=member.id, inline=True)
            embed.add_field(name='Servers', value=shared, inline=True)
            embed.add_field(name='Joined', value=getattr(member, 'joined_at', None), inline=False)
            embed.add_field(name='Created', value=member.created_at, inline=False)

            voice = getattr(member, 'voice', None)
            if voice is not None:
                vc = voice.channel
                other_people = len(vc.members) - 1
                voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
                embed.add_field(name='Voice', value=voice, inline=False)

            if roles:
                embed.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else
                                f'{len(roles)} roles', inline=False)

            color = member.colour
            if color.value:
                embed.color = color
            else:
                embed.color = 0xf2f6f7

            if member.avatar:
                embed.set_thumbnail(url=member.avatar_url)

            if isinstance(member, discord.User):
                embed.set_footer(text='This member is not in this server.')

            await ctx.send(embed=embed)

        except Exception as e:
            print(e)
            await ctx.send(embed=emb.gen_embed_orange('Error', e))


def setup(bot):
    bot.add_cog(Admin(bot))
