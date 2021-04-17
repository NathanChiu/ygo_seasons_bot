import discord
from discord.ext import commands
import logging
import os
import requests
import urllib.parse
import json
from src.ygo_sheet_grabber.spreadsheet import YGOSpreadsheet
from src.ydk_converter.ydkconverter import convert_ydk
from src.ygo_bot.bot_params import Rewards

logger = logging.getLogger(__name__)

TOKEN = 'ODMwMzE2ODIxODY5MzYzMjEy.YHE6zA.ynGT4tmXWWnjfxyPaJvx4DHCmsw'

description = '''Bot for AFKyle's YuGiOh Seasons\n
                 Features: \n
                 \tFile conversion:
                 \t\tUpload your .ydk file in a PM to me to convert to a .lflist.conf file.\n
                 \tCommands:
                 \t\tType ?[command] to issue a command. Try the 'help' command to get a list of available commands.
                 \t\tCommand arguments are presented in their help strings. Arguments should be space separated. (*) denotes optional arguments.
              '''
bot = commands.Bot(command_prefix='?', description=description)
ygos = YGOSpreadsheet(json_directory=os.path.join('src', 'ygo_sheet_grabber'))

@bot.event
async def on_ready():
    logger.info(f"Logged in username: {bot.user.name}, id: {bot.user.id}.")
    logger.info(ygos.usernames)
    logger.info("Ready to go!")
    # logger.info(ygos.get_all_player_info())
    # logger.info(ygos.get_player_info(username="klarq#4529"))
    # logger.info(ygos.get_player_info(username="klarq#4529", sheet_name="match_history"))

class Profile(commands.Cog):
    def __init__(self, b):
        self.bot = b

    @commands.command()
    async def register(self, ctx, alias=None):
        """(*alias) Creates an entry for a new user, with option for an alias."""
        username = str(ctx.author)
        if alias is None:
            alias = username
        try:
            ygos.create_new_player(username=username)
            ygos.set_record_value(id=username, key="Alias", value=alias)
            await ctx.send(f"Successfully created player {username} with alias {alias}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def setalias(self, ctx, _alias):
        """(alias) Sets your alias!"""
        try:
            username = str(ctx.author)
            ygos.check_player_registered(username)
            ygos.set_record_value(id=username, key="Alias", value=_alias)
            await ctx.send(f"Alias for {username} successfully changed to {_alias}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def setcard(self, ctx, *args):
        """(exactcardspelling)Set your signature card!"""
        try:
            username = str(ctx.author)
            sig_card_name = " ".join(args[:])
            ygos.check_player_registered(username)
            sig_card_name_encoded = urllib.parse.quote_plus(sig_card_name)
            requested_card = requests.get(f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={sig_card_name_encoded}")
            if requested_card.status_code != 200:
                await ctx.send(f"Could not find your card on YGOPro. Please make sure your card is spelt correctly.")
            else:
                ygos.set_record_value(record=username, key="Signature Card", value=sig_card_name)
                await ctx.send(f"Signature card successfully set to {sig_card_name}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def showcard(self, ctx):
        """Show off your signature card!"""
        try:
            username = str(ctx.author)
            ygos.check_player_registered(username)
            player_info = ygos.get_player_info(username=username)
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

bot.add_cog(Profile(bot))

class Admin(commands.Cog):
    def __init__(self, b):
        self.bot = b

    @commands.command()
    async def setgames(self, ctx, value=None, username=None):
        """(value, *username) Sets the games of the player."""
        try:
            if username is None:
                _username = str(ctx.author)
            ygos.set_record_value(sheet_name="coin_tracker",
                                id=_username,
                                key="Games Played",
                                value=value)
            await ctx.send(f"Changing {_username}'s games to {value}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def setcoins(self, ctx, value=None, username=None):
        """(value, *username) Sets the user's coin stash to the given value."""
        try:
            if username is None:
                _username = str(ctx.author)
            ygos.set_record_value(sheet_name="coin_tracker",
                                id=username,
                                key="Current AFKoins",
                                value=new_val)
            await ctx.send(f"Changing {username}'s AFKoin stash from {current_coins} to {value}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def settournamentwinner(self, ctx, id, winner):
        """(id, winner) Sets the winner of a tournament."""
        try:
            tournaments = ygos.get_all_record_dict(sheet_name="tournaments")
            if ygos.check_player_registered(winner) and str(id) in tournaments:
                ygos.set_record_value(sheet_name="tournaments", \
                                      id=str(id), \
                                      key="Champion", \
                                      value=winner)
            await ctx.send(f"{winner} has been crowned the winner of tournament #{id}!")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def settournamentname(self, ctx, id, name):
        """(id, name) Sets the name of a tournament."""
        try:
            tournaments = ygos.get_all_record_dict(sheet_name="tournaments")
            if str(id) in tournaments:
                ygos.set_record_value(sheet_name="tournaments", \
                                      id=str(id), \
                                      key="Tournament", \
                                      value=name)
            await ctx.send(f"{winner} has been crowned the winner of tournament #{id}!")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def tournament(self, ctx, tname=None):
        """(*tournamentname) Creates a new tournament. Tournament name optional."""
        try:
            ygos.create_tournament(tname)
            if tname is None:
                await ctx.send(f"New Unnamed Tournament Created.")
            else:
                await ctx.send(f"New Tournament created: {tname}.")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def addcoins(self, ctx, increment, username=None):
        """(increment, *username) Awards coins to the username. Negative numbers allowed"""
        if username is None:
            username = str(ctx.author)
        try:
            new_coins = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Current AFKoins",
                                                  value=increment)
            await ctx.send(f"Added {increment} AFKoins to {username}'s stash. New balance: {new_coins}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def win(self, ctx, num=1, username=None):
        """(increment, *username) Increments the games and coins of the player from a win."""
        try:
            if username is None:
                username = str(ctx.author)
            new_games = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Games Played",
                                                  value=num)
            new_coins = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Current AFKoins",
                                                  value=Rewards.Win*num)
            await ctx.send(f"Win recorded for {username}. Total games: {new_games}, total coins: {new_coins}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def lose(self, ctx, num=1, username=None):
        """Increments the games and coins of the player from a loss."""
        try:
            if username is None:
                username = str(ctx.author)
            new_games = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Games Played",
                                                  value=num)
            new_coins = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Current AFKoins",
                                                  value=Rewards.Lose*num)
            await ctx.send(f"Loss recorded for {username}. Total games: {new_games}, total coins: {new_coins}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def addgames(self, ctx, increment, username):
        """(increment, *username) Adds games to the username. Negative numbers allowed"""
        if username is None:
            username = str(ctx.author)
        try:
            new_games = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Games Played",
                                                  value=increment)
            await ctx.send(f"Added {increment} AFKoins to {username}'s games. New games balance: {new_games}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

bot.add_cog(Admin(bot))

class Concierge(commands.Cog):
    def __init__(self, b):
        self.bot = b
    @commands.command()
    async def duelists(self, ctx):
        """Shows a list of registered players and their information"""
        player_info = ygos.get_all_record_dict()
        player_strings = []
        for player in player_info.values():
            key_val_strings = []
            for key, val in player.items():
                if key in ['Username', 'Alias']: # Can add more header names here later.
                    key_val_strings.append(f"{key}: {val}")
            player_strings.append("\t".join(key_val_strings))
        output_string = "\n".join(player_strings)
        await ctx.send("```"+output_string+"```")

    @commands.command()
    async def duelist(self, ctx, username=None):
        """(*username) Shows the info of a given user, including stats!."""
        if username is None:
            username = str(ctx.author)
        key_val_strings = []
        player_info = ygos.get_player_info(username=username)
        key_val_strings.append(f"'Username': {player_info['Username']}")
        key_val_strings.append(f"'Alias': {player_info['Alias']}")
        key_val_strings.append(f"'Signature Card': {player_info['Signature Card']}")
        num_games = int(player_info["Games Played"])
        player_info = ygos.get_player_info(sheet_name="match_history", username=username)
        num_wins = 0
        for wins in player_info.values():
            if wins.isdigit():
                num_wins += int(wins)
        key_val_strings.append(f"'Win rate (total games)': {num_wins/num_games:.2f}({num_games})")
        tourns = ygos.tournaments_won(username)
        key_val_strings.append(f"'Tournaments won': {len(tourns)}")
        output_string = "\n".join(key_val_strings)
        await ctx.send("```"+output_string+"```")

    @commands.command()
    async def archenemies(self, ctx):
        """Shows your archenemies (most wins and most losses)"""
        try:
            username = str(ctx.author)
            players_info = ygos.get_all_record_dict(sheet_name="match_history")
            min_name = ""
            min_wins = 0
            for name, info in players_info.items():
                logger.info(info)
                if name == username:
                    player_info = {k:int(v) for k,v in info.items() if v.isdigit()}
                    max_key = max(player_info, key=lambda k: player_info[k])
                    max_wins = player_info[max_key]
                else:
                    if int(info[username]) > min_wins:
                        min_name = name
                        min_wins = int(info[username])
            await ctx.send(f"Most wins against {max_key} ({max_wins}), most losses against {min_name} ({min_wins}).")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def recordvs(self, ctx, opponent):
        """(opponent) Shows your record against an opponent."""
        try:
            username = str(ctx.author)
            player_info = ygos.get_player_info(sheet_name="match_history", username=username)
            opponent_info = ygos.get_player_info(sheet_name="match_history", username=opponent)
            await ctx.send(f"Record vs {opponent}: {player_info[opponent]} wins, {opponent_info[username]} losses.")
        except Exception as e:
            await ctx.send(f"Error: {e}")

bot.add_cog(Concierge(bot))

class UpdatingRecords(commands.Cog):
    def __init__(self, b):
        self.bot = b
    @commands.command()
    async def winvs(self, ctx, loser=None, num_wins=1):
        """(opponent, *numwins) Record a win against a player. Can specify number of wins after the opponent's name."""
        try:
            winner = str(ctx.author)
            if not ygos.check_player_registered(loser) or \
                        not ygos.check_player_registered(winner):
                raise ValueError(f"Either {winner} or {loser} is not a registered player.")
            # Winner
            ygos.increment_user_value(sheet_name="coin_tracker",
                                      username=winner,
                                      key=["Games Played", "Current AFKoins"],
                                      value=[num_wins, Rewards.Win*num_wins])
            # Loser
            ygos.increment_user_value(sheet_name="coin_tracker",
                                      username=loser,
                                      key=["Games Played", "Current AFKoins"],
                                      value=[num_wins, Rewards.Lose*num_wins])
            ygos.increment_user_value(sheet_name="match_history",
                                      username=winner,
                                      key=loser,
                                      value=num_wins)
            await ctx.send(f"Hark! {winner} has achieved {num_wins} win(s) against {loser}!")
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command()
    async def spendcoins(self, ctx, increment, username=None):
        """(amount, *username) Awards coins to the username. Negative numbers allowed"""
        if username is None:
            username = str(ctx.author)
        try:
            new_coins = ygos.increment_user_value(sheet_name="coin_tracker",
                                                  username=username,
                                                  key="Current AFKoins",
                                                  value=-int(increment))
            await ctx.send(f"{username} spent {increment} coin(s)! New balance: {new_coins}")
        except Exception as e:
            await ctx.send(f"Error: {e}")

bot.add_cog(UpdatingRecords(bot))





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
                os.remove("afkseasons.ydk")
                os.remove("afkseasons.lflist.conf")
    await bot.process_commands(message) #allows over commands to be processed while bot listens
# bot.add_

def start_bot():
    bot.run(TOKEN)
