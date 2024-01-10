import datetime
import json
import discord
import sqlite3
import os
import yaml
from discord.ext import commands
from discord.ext.commands import Context
from db import on_start, on_start_guild_db, update_user_entry_db, delete_entry_db, add_user_db, leaderboard_db, \
    fetch_user_db, user_exist_in_db
from roulette import is_valid_bet, roulette, roulette_values
from model import RouletteUser

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), case_insensitive=True)

with open("config.yaml", 'r') as file:
    config = yaml.safe_load(file)

leaderboard_valid_categories = config["leaderboard"]["valid_categories"]
command_text = config["command_text"]


# Util
def create_embed(ctx: Context, title: str, description: str, fields: dict,
                 color: discord.Color = discord.Color.random(),
                 timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)) -> discord.Embed:
    non_currency_keys = ["Wins", "Losses"]
    embed = discord.Embed(title=title, description=description, color=color, timestamp=timestamp)
    for key, value in fields.items():
        if key in non_currency_keys:
            embed.add_field(name=key, value=value)
        else:
            embed.add_field(name=key, value=f"${value}")
    embed.set_thumbnail(url=ctx.author.avatar)
    return embed


def does_user_exist(ctx: Context):
    if not user_exist_in_db(conn, str(ctx.author.id), str(ctx.guild.id)):
        return "User does not exist yet. Please type !me to create a profile"


# bot events
@bot.event
async def on_ready():
    guild_list = on_start_guild_db(conn, bot.guilds)
    print(guild_list)
    print("Ready to Go")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command. Use !help for commands")


# @bot.command(description="Help Command")
# async def help(ctx: Context):
#     await ctx.send(command_text["help"])
#     return


@bot.command(help="View user statistics", description="View user statistics")
async def me(ctx: Context):
    if not user_exist_in_db(conn, str(ctx.author.id), str(ctx.guild.id)):
        print("not exist")
        try:
            r_user_obj = add_user_db(conn, ctx)
            embed_fields = {"Balance": r_user_obj.balance, "Wins": r_user_obj.wins, "Losses": r_user_obj.losses,
                            "Anita Max Wynn": r_user_obj.max_win}
            embed = create_embed(ctx, title=ctx.message.author.name, description='Roulette Stats',
                                 timestamp=datetime.datetime.now(datetime.UTC), fields=embed_fields)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error {e}")
    else:
        print("exist")
        try:
            r_user_obj = fetch_user_db(conn, str(ctx.author.id), str(ctx.guild.id))
            embed_fields = {"Balance": r_user_obj.balance, "Wins": r_user_obj.wins, "Losses": r_user_obj.losses,
                            "Anita Max Wynn": r_user_obj.max_win}
            embed = create_embed(ctx, title=ctx.message.author.name, description='Roulette Stats',
                                 timestamp=datetime.datetime.now(datetime.UTC), fields=embed_fields)

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")


@bot.command(help="View server statistics", description=f"{command_text["leaderboard_help"]}")
async def leaderboard(ctx: Context, arg: str = "balance"):
    valid_categories = leaderboard_valid_categories
    print(arg)
    if arg in valid_categories:
        user_list = leaderboard_db(conn, str(ctx.guild.id), arg)
        if user_list:
            embed = discord.Embed(title=f"{arg} leaderboard")
            count = 0
            for user in user_list:
                count += 1
                if arg == "balance" or arg == "max_win":
                    embed.add_field(name=f"{count}. {user[0]} -- ${user[1]}", value=f"", inline=True)
                else:
                    embed.add_field(name=f"{count}. {user[0]} -- {user[1]}", value=f"", inline=True)
            await ctx.send(embed=embed)
        return
    else:
        await ctx.send(f"Not a valid category. Please select on from the follow {leaderboard_valid_categories}")
        return


@bot.command(help="reload on funds when you lose all your money",
             description=f"reload on funds when you lose all your money")
async def beg(ctx: Context):
    if not user_exist_in_db(conn, str(ctx.author.id), str(ctx.guild.id)):
        await ctx.send("User does not exist yet. Please type !me to create a profile")
        return
    else:
        user_obj = fetch_user_db(conn, str(ctx.author.id), str(ctx.guild.id))
        print(f"fetched {user_obj}")
        fields_to_update = {"balance": user_obj.balance + 100}
        updated_user_obj = update_user_entry_db(conn=conn, user_id=user_obj.user_id,
                                                guild_id=user_obj.gid, **fields_to_update)
        embed_fields = {"Balance": updated_user_obj.balance, "Wins": updated_user_obj.wins,
                        "Losses": updated_user_obj.losses,
                        "Anita Max Wynn": updated_user_obj.max_win}
        embed = create_embed(ctx, title=ctx.message.author.name, description='Roulette Stats',
                             timestamp=datetime.datetime.now(datetime.UTC), fields=embed_fields)
        await ctx.send(embed=embed)


@bot.command(help="Create a bet", description=f"{command_text["bet_help"]}")
async def bet(ctx: Context, *args: str, ):
    if "help" in args:
        await ctx.send(command_text["bet_help"])
    if "clear" in args:
        user_obj = fetch_user_db(conn, str(ctx.author.id), str(ctx.guild.id))
        all_bet_choices = user_obj.curr_bet
        wagered = 0
        for wager in all_bet_choices.values():
            wagered += wager
        fields_to_update = {"curr_bet": json.dumps({}), "balance": user_obj.balance + wagered}
        user_obj = update_user_entry_db(conn=conn, user_id=user_obj.user_id, guild_id=user_obj.gid, **fields_to_update)
        print(user_obj)
        await ctx.send(f"Bets cleared. Balance is ${user_obj.balance}")
        return
    if not user_exist_in_db(conn, str(ctx.author.id), str(ctx.guild.id)):
        await ctx.send("User does not exist yet. Please type !me to create a profile")
        return
    else:
        print("else")
        user_obj = fetch_user_db(conn, str(ctx.author.id), str(ctx.guild.id))
        all_bet_choices = user_obj.curr_bet
        wager = 0
        print(args)
        for arg in args:
            bet_choice, value_str = arg.split(":")
            if not value_str.isnumeric():
                await ctx.send(f"{value_str} is not a valid number")
                return
            value = int(value_str)
            wager += int(value)
            if wager > user_obj.balance:
                await ctx.send(f"Combined wager of ${wager} is greater than your balance of ${user_obj.balance}")
                return
            if not is_valid_bet(bet_choice):
                await ctx.send(f"{bet_choice} is not a valid bet. Type !help bet for valid bets")
                return
            user_obj.curr_bet[bet_choice] = all_bet_choices.get(bet_choice, 0) + int(value)
        all_bet_choices_json = json.dumps(user_obj.curr_bet)
        print(all_bet_choices_json)
        fields_to_update = {"curr_bet": all_bet_choices_json, "balance": user_obj.balance - wager}
        user_obj = update_user_entry_db(conn=conn, user_id=user_obj.user_id, guild_id=user_obj.gid, **fields_to_update)
        print(user_obj)
        embed = create_embed(ctx, user_obj.display_name, f"Current Bets",
                             user_obj.curr_bet)
        await ctx.send(embed=embed)
        await ctx.send(f"Balance {user_obj.balance}")


def roulette_win(ctx: Context, roulette_user: RouletteUser, winning_amount: int):
    fields_to_update = {"wins": roulette_user.wins + 1, "balance": roulette_user.balance + winning_amount,
                        "curr_bet": json.dumps({})}
    try:
        user_obj = update_user_entry_db(conn=conn, user_id=roulette_user.user_id, guild_id=roulette_user.gid,
                                        **fields_to_update)
        return user_obj
    except Exception as e:
        return e


def roulette_loss(ctx: Context, roulette_user: RouletteUser):
    fields_to_update = {"losses": roulette_user.losses + 1, "curr_bet": json.dumps({})}
    try:
        user_obj = update_user_entry_db(conn=conn, user_id=roulette_user.user_id, guild_id=roulette_user.gid,
                                        **fields_to_update)
        return user_obj
    except Exception as e:
        return e


@bot.command(help="Spin the ball and watch your money multiply",
             description=f"Spin the ball and watch your money multiply")
async def roll(ctx: Context):
    if not user_exist_in_db(conn, str(ctx.author.id), str(ctx.guild.id)):
        await ctx.send("User does not exist yet. Please type !me to create a profile")
        return
    else:
        user_obj = fetch_user_db(conn, str(ctx.author.id), str(ctx.guild.id))
        if user_obj.curr_bet == {}:
            await ctx.send("You have not placed a bet. Use !bet to place a bet")
            return
        else:
            print(user_obj.curr_bet)
            winning_number, result_amount, wagered = roulette(user_obj.curr_bet)
            emoji = "\U0001F7E9"
            if winning_number in roulette_values["red_numbers"]:
                emoji = "\U0001F7E5"
            elif winning_number in roulette_values["black_numbers"]:
                emoji = "\U00002B1B"
            await ctx.send(f"Winning Number is {emoji} {winning_number} !")
            fields_to_update = {"curr_bet": json.dumps({})}
            if result_amount == 0:
                fields_to_update["balance"] = user_obj.balanc + wagered
                await ctx.send(f"Push.")
            if result_amount < 0:
                fields_to_update["losses"] = user_obj.losses + 1
                await ctx.send(f"You lose.")
            if result_amount > 0:
                fields_to_update["wins"] = user_obj.wins + 1
                fields_to_update["balance"] = user_obj.balance + result_amount + wagered
                if result_amount > user_obj.max_win:
                    fields_to_update["max_win"] = result_amount
                await ctx.send(f"Congratulations you won ${result_amount}!")
            user_obj = update_user_entry_db(conn=conn, user_id=user_obj.user_id, guild_id=user_obj.gid,
                                            **fields_to_update)
            await ctx.send(f"Your balance is ${user_obj.balance}.")
    return


if __name__ == "__main__":
    root = os.getcwd()
    data_file = os.path.join(root, 'data', 'data.db')
    conn = sqlite3.connect(data_file, detect_types=sqlite3.PARSE_DECLTYPES)
    on_start(conn)

    token = config["bot"]["token"]
    if token:
        bot.run(token)
    else:
        print("please add bot token into config.yaml")
