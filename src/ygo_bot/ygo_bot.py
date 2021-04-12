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
    logger.info(ygos.all_records)

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
async def register(ctx):
    """Creates an entry for a new user."""
    username = str(ctx.author)
    try:
        ygos.create_new_player(username=username)
        await ctx.send(f"Successfully created user {username}")
    except Exception as e:
        await ctx.send(f"Error: {e}")




def start_bot():
    bot.run(TOKEN)
