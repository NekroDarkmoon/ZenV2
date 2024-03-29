#!/usr/bin/env python3

# --------------------------------------------------------------------------
#                                 Imports
# --------------------------------------------------------------------------
# Standard library imports
import asyncpg
import logging
import sys
import os
import traceback

# Third party imports
# import discord # noqa
# from discord.ext import commands

# Local application imports
# Enabling local imports
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)


log = logging.getLogger(__name__)


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

    # Table for Reputation system
    sql = """CREATE TABLE IF NOT EXISTS 
             rep(server_id BIGINT NOT NULL,
                 user_id BIGINT NOT NULL,
                 rep BIGINT NOT NULL DEFAULT 0,
                 CONSTRAINT server_user UNIQUE (server_id, user_id));"""
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
                                              posted_date DATE NOT NULL DEFAULT CURRENT_DATE,
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
    conn = await asyncpg.create_pool(database='Zen', user='Zen', password=configs['db_password'])
    try:
        await create_schemas(conn)
        log.info("Database connection established.")
    except Exception as e:
        log.warning(e)
        log.error(traceback.format_exc())

    return conn
