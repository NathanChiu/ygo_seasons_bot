import logging
import coloredlogs
import sys
import os
from src.ygo_bot.ygo_bot import start_bot

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Set up logger
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s', '%Y-%m-%d %H:%M:%S')
    coloredlogs.install(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)

    start_bot()
