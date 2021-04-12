import logging
import coloredlogs
import sys
import os
from src.ygo_sheet_grabber.spreadsheet import YGOSpreadsheet

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Set up logger
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s', '%Y-%m-%d %H:%M:%S')
    coloredlogs.install(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)

    ygos = YGOSpreadsheet(json_directory=os.path.join('src', 'ygo_sheet_grabber'))
    logger.info(ygos.usernames)
    logger.info(ygos.all_records)
