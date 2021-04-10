# ygo_seasons_bot

## How to run the bot and have it persist
With ssh, if you simply run `python3 bot.py`, you will have to maintain that ssh session to have the bot persist.
This is counter-intuitive to having a headless RPi running the bot, since we want to be able to start it and be able to walk away.

1. Log into the bot through ssh (username: ygo_seasons).
2. `cd` to the location of `bot.py`
3. Do `screen python3 bot.py`. This will start the bot a separate window session.
4. Once the bot is logged in, do `ctrl+A`, then `ctrl+D`. This will detach your terminal from the bot's window.
5. You can now log out of ssh with `exit`, and the bot will persist.

## How to refresh the bot
Since the window running the bot is detached from your ssh connection, you will need to resume the session so the bot can be restarted.

1. Log into the bot through ssh (username: ygo_seasons).
2. Do `screen -r`. This will resume the window with the bot.
3. Do `ctrl+C` to close the bot process.
4. Refresh the code however you like, preferably using git.
    * Protip: Try not to develop ON the ssh connection, so we always know exactly what code is running on the RPi. It's running headless so having to attach a monitor, keyboard, and mouse to debug will be annoying.
5. Start from step 3 of [How to run the bot and have it persist](#how-to-run-the-bot-and-have-it-persist)
