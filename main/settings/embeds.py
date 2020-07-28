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


# --------------------------------------------------------------------------
#                                   Main
# --------------------------------------------------------------------------
# Use when custom colors are required
def gen_embed_custom(head, response, color):
    embed = discord.Embed(
        title=head,
        description=response,
        color=color
    )
    return embed


# Used for a failure due to permissions or not allowed queries
def gen_embed_red(head, response):
    embed = discord.Embed(
        title=head,
        description=response,
        color=0xff3e30
    )

    return embed


# Used for a generic response
def gen_embed_green(head, response):
    embed = discord.Embed(
        title=head,
        description=response,
        # color=0x6cd164
        color=0x8dff63
    )

    return embed


# Used for missing arguments and other such failures
def gen_embed_yellow(head, response):
    embed = discord.Embed(
        title=head,
        description=response,
        color=0xffcf30
    )

    return embed


# Used when something fails internally due to code
def gen_embed_orange(head, response):
    embed = discord.Embed(
        title=head,
        description=response,
        color=0xffa230
    )

    return embed


def gen_embed_cobalt(head, response):
    embed = discord.Embed(
        title=head,
        description=response,
        color=0x63ddff
    )

    return embed


def gen_embed_white(head, response):
    embed = discord.Embed(
        title=head,
        description=response,
        color=0xf2f6f7
    )

    return embed
