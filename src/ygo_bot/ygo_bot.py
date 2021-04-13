import discord
from discord.ext import commands
import logging
import os
from src.ygo_sheet_grabber.spreadsheet import YGOSpreadsheet

logger = logging.getLogger(__name__)

TOKEN = 'ODMwMzE2ODIxODY5MzYzMjEy.YHE6zA.ynGT4tmXWWnjfxyPaJvx4DHCmsw'

description = '''Bot for AFKyle's YuGiOh Seasons'''
bot = commands.Bot(command_prefix='?', description=description)
ygos = YGOSpreadsheet(json_directory=os.path.join('src', 'ygo_sheet_grabber'))

@bot.event
async def on_ready():
    logger.info(f"Logged in username: {bot.user.name}, id: {bot.user.id}.")
    logger.info(ygos.usernames)
    logger.info(ygos.get_all_player_info())
    logger.info(ygos.get_player_info(username="klarq#4529"))

@bot.command()
async def hello(ctx):
    """Says world"""
    logger.info(dir(ctx))
    logger.info(f"{ctx.author}: {ctx.command}")
    await ctx.send("world")

@bot.command()
async def add(ctx, left : int, right : int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def register(ctx, alias=None):
    """Creates an entry for a new user, with option for an alias."""
    username = str(ctx.author)
    if alias is None:
        alias = username
    try:
        ygos.create_new_player(username=username)
        ygos.set_player_value(username=username, key="Alias", value=alias)
        await ctx.send(f"Successfully created player {username} with alias {alias}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def players(ctx):
    """Shows a list of registered players and their information"""
    player_info = ygos.get_all_player_info()
    player_strings = []
    for player in player_info.values():
        key_val_strings = []
        for key, val in player.items():
            if key in ['Username', 'Alias']: # Can add more header names here later.
                key_val_strings.append(f"{key}: {val}")
        player_strings.append("\t".join(key_val_strings))
    output_string = "\n".join(player_strings)
    await ctx.send("```"+output_string+"```")

@bot.command()
async def duelist(ctx):
    """Shows the info of the user sending the command."""
    username = str(ctx.author)
    player_info = ygos.get_player_info(username)
    key_val_strings = []
    for key, val in player_info.items():
        key_val_strings.append(f"{key}: {val}")
    output_string = "\t".join(key_val_strings)
    await ctx.send("```"+output_string+"```")

@bot.command()
async def award(ctx, username, increment):
    """Awards coins to the username. Negative numbers allowed"""
    try:
        player_info = ygos.get_player_info(username)
        coin_header_string = 'Current AFKoins'
        current_coins = int(player_info[coin_header_string])
        new_coins = int(increment) + current_coins
        ygos.set_player_value(username=username, key=coin_header_string, value=new_coins)
        await ctx.send(f"Added {increment} AFKoins to {username}'s stash. New balance: {new_coins}")
    except Error as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def setcoins(ctx, username, value):
    """Sets the user's coin stash to the given value."""
    try:
        player_info = ygos.get_player_info(username)
        coin_header_string = 'Current AFKoins'
        current_coins = int(player_info[coin_header_string])
        ygos.set_player_value(username=username, key=coin_header_string, value=int(value))
        await ctx.send(f"Changing {username}'s AFKoin stash from {current_coins} to {value}")
    except Error as e:
        await ctx.send(f"Error: {e}")





def start_bot():
    bot.run(TOKEN)
