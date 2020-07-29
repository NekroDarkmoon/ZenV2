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
    @commands.command(name="kick", pass_context=True)
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
    @commands.has_permissions(ban_members=True)
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
    @commands.has_permissions(ban_members=True)
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


def setup(bot):
    bot.add_cog(Admin(bot))
