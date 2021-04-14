import discord
from discord.ext import commands
import logging
import os
import requests
import urllib.parse
import json
from src.ygo_sheet_grabber.spreadsheet import YGOSpreadsheet
from src.ydk_converter.ydkconverter import convert_ydk


logger = logging.getLogger(__name__)

TOKEN = 'ODMwMzE2ODIxODY5MzYzMjEy.YHE6zA.ynGT4tmXWWnjfxyPaJvx4DHCmsw'

description = '''Bot for AFKyle's YuGiOh Seasons\nUpload your .ydk file in a PM to me to convert to a .lflist.conf file.'''
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
    except Exception as e:
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
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def games(ctx, username, increment):
    """Increments/decrements the games of the player."""
    try:
        player_info = ygos.get_player_info(username)
        increment = int(increment)
        games_header_string = "Games Played"
        current_games = int(player_info[games_header_string])
        new_games = increment + current_games
        ygos.set_player_value(username=username, key=games_header_string, value=new_games)
        await ctx.send(f"Changing {username}'s games from {current_games} to {new_games}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def alias(ctx, _alias):
    """Sets your alias!"""
    try:
        username = str(ctx.author)
        ygos.check_player_registered(username)
        ygos.set_player_value(username=username, key="Alias", value=_alias)
        await ctx.send(f"Alias for {username} successfully changed to {_alias}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def setsignaturecard(ctx, *args):
    """Set your signature card!"""
    try:
        username = str(ctx.author)
        sig_card_name = " ".join(args[:])
        ygos.check_player_registered(username)
        sig_card_name_encoded = urllib.parse.quote_plus(sig_card_name)
        requested_card = requests.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={sig_card_name_encoded}")
        if requested_card.status_code != 200:
            await ctx.send(f"Could not find your card on YGOPro. Please make sure your card is spelt correctly.")
        else:
            ygos.set_player_value(username=username, key="Signature Card", value=sig_card_name)
            await ctx.send(f"Signature card successfully set to {sig_card_name}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def showsignaturecard(ctx):
    """Show off your signature card!"""
    try:
        username = str(ctx.author)
        ygos.check_player_registered(username)
        player_info = ygos.get_player_info(username)
        sig_card_name = player_info["Signature Card"]
        sig_card_name_encoded = urllib.parse.quote_plus(sig_card_name)
        requested_card = requests.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={sig_card_name_encoded}")
        if requested_card.status_code != 200:
            await ctx.send(f"Could not find your card on YGOPro. Please make sure your signature card is set.")
        else:
            # Get the image_url
            card_info = json.loads(requested_card.text)
            image_url = card_info["data"][0]["card_images"][-1]["image_url"]
            await ctx.send(f"{image_url}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.event
async def on_message(message):
    if (len(message.attachments) == 1):
        if (message.attachments[0].url.endswith('.ydk')): #detect ydk file
            if (message.author.bot): #prevents bot self loop if it happens
                return
            else:
                channel=message.channel
                #await channel.send("your file is txt")
                await message.attachments[0].save(fp="afkseasons.ydk")
                #await channel.send("Received")
                convert_ydk("afkseasons")
                # f = open("this.txt", "a")
                # f.write("Now the file has more content!")
                # f.close()
                await channel.send(file=discord.File("afkseasons.lflist.conf"))
                os.remove("afkseasons.lflist.conf")


    await bot.process_commands(message) #allows over commands to be processed while bot listens


def start_bot():
    bot.run(TOKEN)
