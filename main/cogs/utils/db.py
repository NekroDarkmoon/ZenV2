#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import asyncpg
import sys
import os

# Third party imports
# import discord # noqa
# from discord.ext import commands

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


# --------------------------------------------------------------------------
#                              Create Schemas
# --------------------------------------------------------------------------
async def create_schemas(conn):
    # Add tables here
    # Table for server settings

    sql = """CREATE TABLE IF NOT EXISTS settings(server_id BIGINT NOT NULL,
                                                 prefix TEXT,
                                                 log_channel BIGINT,
                                                 welcome_channel BIGINT,
                                                 dnd_cog BOOLEAN NOT NULL DEFAULT FALSE,
                                                 leveling_cog BOOLEAN NOT NULL DEFAULT FALSE,
                                                 tag_cog BOOLEAN NOT NULL DEFAULT FALSE,
                                                 save_cog BOOLEAN NOT NULL DEFAULT FALSE,
                                                 voice_cog BOOLEAN NOT NULL DEFAULT FALSE);"""

    await conn.execute(sql)

    # Table for leveling system
    sql = """CREATE TABLE IF NOT EXISTS lb(server_id BIGINT NOT NULL,
                                           user_id BIGINT NOT NULL,
                                           last_exp TIMESTAMP NOT NULL,
                                           msg_amt INTEGER NOT NULL,
                                           total_exp INTEGER not NULL,
                                           level INTEGER NOT NULL);"""

    await conn.execute(sql)

    # Table for roles (for the leveling system)
    sql = """CREATE TABLE IF NOT EXISTS roles(rolename TEXT NOT NULL,
                                              server_id BIGINT NOT NULL,
                                              role_id BIGINT NOT NULL,
                                              level INTEGER NOT NULL,
                                              description TEXT);"""

    await conn.execute(sql)

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Custom tables for certain servers
    sql = '''CREATE TABLE IF NOT EXISTS quest(server_id BIGINT NOT NULL,
                                              quest_id BIGINT UNIQUE,
                                              author TEXT NOT NULL,
                                              quest_type text NOT NULL,
                                              msg TEXT);'''

    await conn.execute(sql)
    return


# --------------------------------------------------------------------------
#                                   Main
# --------------------------------------------------------------------------
async def create_db(configs):
    conn = await asyncpg.create_pool(database='zen', user='zen', password=configs['db_password'])
    try:
        await create_schemas(conn)
    except Exception as e:
        print(e)

    return conn
