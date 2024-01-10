import discord.message

from model import RouletteUser, RouletteGuild, RouletteBet
from discord.ext.commands.context import Context

import sqlite3
import json


# sqlite3.register_adapter(dict, lambda d: json.dumps(d).encode('utf8'))
# sqlite3.register_converter("dictionary", lambda d: json.loads(d.decode('utf8')))


def create_roulette_user(ctx: Context):
    user_ctx = ctx.message.author
    guild_ctx = ctx.message.guild
    user_obj = RouletteUser(user_id=user_ctx.id, display_name=user_ctx.name, gid=guild_ctx.id)
    return user_obj


def create_roulette_guild(ctx: Context):
    guild_ctx = ctx.message.guild
    guild_obj = RouletteGuild(guild_name=guild_ctx.name, guild_id=guild_ctx.id)
    return guild_obj


def convert_user_db_to_roulette_user(db_tuple: tuple) -> RouletteUser:
    print(db_tuple)
    r_user = RouletteUser(user_id=db_tuple[0], display_name=db_tuple[1], gid=db_tuple[2], balance=db_tuple[3],
                          wins=db_tuple[4], losses=db_tuple[5], max_win=db_tuple[6], last_beg=db_tuple[7],
                          curr_bet=json.loads(db_tuple[8]))

    return r_user


def on_start(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS guild (
            guild_id text PRIMARY KEY,
            guild_name text
    )""")

    cursor.execute(""" CREATE TABLE IF NOT EXISTS user (
            user_id text ,
            display_name text,
            guild_id text,
            balance integer DEFAULT 0,
            wins integer DEFAULT 0,
            losses integer DEFAULT 0,
            max_win integer DEFAULT 0,
            last_beg integer,
            curr_bet text,
            PRIMARY KEY(user_id,guild_id))
    """)
    #
    # cursor.execute(""" CREATE TABLE IF NOT EXISTS user (
    #         user_id text PRIMARY KEY,
    #         display_name text,
    #         guild_id text,
    #         balance integer DEFAULT 0,
    #         wins integer DEFAULT 0,
    #         losses integer DEFAULT 0,
    #         max_win integer DEFAULT 0,
    #         last_beg integer
    # )""")

    cursor.execute(""" CREATE TABLE IF NOT EXISTS guild_user (
            guild_id integer,
            user_id integer,
            PRIMARY KEY (guild_id, user_id)
            FOREIGN KEY(user_id) REFERENCES user(user_id),
            FOREIGN KEY(guild_id) REFERENCES guild(guild_id)
    )""")

    conn.commit()


# util
def user_exist_in_db(conn: sqlite3.Connection, user_id: str, guild_id: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM user WHERE user_id = ? AND guild_id = ?", (user_id, guild_id,))
    result = cursor.fetchone()[0]
    return result == 1


def guild_exist_in_db(conn: sqlite3.Connection, guild_id: str) -> bool:
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM guild WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()[0]
    return result == 1


# def update_entry_db(conn: sqlite3.Connection, table: str, column_to_update: str, new_column_value: str | int | dict,
#                     condition_column: str, condition: str, ctx: Context):
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             f"UPDATE {table} SET {column_to_update} = ? WHERE {condition_column} = {condition}", (new_column_value,))
#         conn.commit()
#         r_user = fetch_user_db(conn, "user", condition_column, condition)
#         return r_user
#     except Exception as e:
#         return e


def update_user_entry_db(conn: sqlite3.Connection, user_id: str, guild_id: str, **kwargs):
    cursor = conn.cursor()
    print(kwargs)
    for key, val in kwargs.items():
        try:
            cursor.execute(
                f"UPDATE user SET {key} = ? WHERE user_id = ? and guild_id = ?", (val, user_id, guild_id)
            )
            conn.commit()
        except Exception as e:
            return e
    r_user = fetch_user_db(conn, user_id, guild_id)
    return r_user


def delete_entry_db(conn: sqlite3.Connection, table: str, condition_column: str, condition: str):
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table} WHERE {condition_column} = ?", (condition,))
        conn.commit()
        return True
    except Exception as e:
        return e


def fetch_user_db(conn: sqlite3.Connection, user_id: str, guild_id: str):
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM user WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        result = cursor.fetchone()
        print(f"results- {result}")
        r_user = convert_user_db_to_roulette_user(result)
        return r_user
    except Exception as e:
        return e


# User
def add_user_db(conn: sqlite3.Connection, ctx: Context):
    r_user = create_roulette_user(ctx)
    print(r_user)
    cursor = conn.cursor()
    result = user_exist_in_db(conn, r_user.user_id, r_user.gid)
    if result == 0:
        try:
            cursor.execute(
                f"INSERT INTO user VALUES(?,?,?,0,0,0,0,0,?)",
                (r_user.user_id, r_user.display_name, r_user.gid, json.dumps({})))
            cursor.execute(f"INSERT INTO guild_user VALUES(?,?)", (r_user.gid, r_user.user_id))
            conn.commit()
        except Exception as e:
            return e
    return r_user


# guilds
def on_start_guild_db(conn: sqlite3.Connection, guilds):
    cursor = conn.cursor()
    for guild in guilds:
        result = guild_exist_in_db(conn, guild.id)
        print(result)
        if result == 0:
            cursor.execute(f"INSERT INTO guild VALUES (?,?)", (guild.id, guild.name))
            conn.commit()
    cursor.execute("SELECT * FROM guild")
    return cursor.fetchall()


def leaderboard_db(conn: sqlite3.Connection, guild_id: str, sort_category: str):
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
        SELECT display_name, {sort_category}
        FROM guild
        JOIN guild_user ON guild.guild_id = guild_user.guild_id
        JOIN user ON guild_user.user_id = user.user_id
        WHERE guild.guild_id = {guild_id}
        ORDER BY {sort_category} DESC
        LIMIT 10""")
        user_list = cursor.fetchall()
        return user_list
    except Exception as e:
        return e
