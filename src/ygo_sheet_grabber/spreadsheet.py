# from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging
import coloredlogs
import sys
import os

logger = logging.getLogger(__name__)
# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
AFKOIN_SHEET_ID = '19lTpDVxdIcQqZ8CSXa2I3y_ENE_A5znImgvdR3-6A9Q'
SAMPLE_RANGE_NAME = 'coin_tracker!A1:E'

def excel_column_name(n):
    """Number to Excel-style column name, e.g., 1 = A, 26 = Z, 27 = AA, 703 = AAA."""
    name = ''
    while n > 0:
        n, r = divmod (n - 1, 26)
        name = chr(r + ord('A')) + name
    return name

def excel_column_number(name):
    """Excel-style column name to number, e.g., A = 1, Z = 26, AA = 27, AAA = 703."""
    n = 0
    for c in name:
        n = n * 26 + 1 + ord(c) - ord('A')
    return n

def flatten_list(_list):
    """
    Convenience function to flatten a list, mainly because record from
    google sheets come in nested lists.
    """
    return [item for sublist in _list for item in sublist]

class YGOSpreadsheet:
    def __init__(self, json_directory=''):
        """
        Need to create the service and expose the sheet to usage.
        """
        self.json_directory = json_directory
        self.client_json_path = os.path.join(json_directory, 'clientjson')
        self.token_json_path = os.path.join(json_directory, 'token.json')
        self.prepare_credentials()
        service = build('sheets', 'v4', credentials=self.creds)
        self.sheet = service.spreadsheets()
        logger.info("YGOSpreadsheet initiated.")
        logger.info(f"Current records: {self.get_all_records()}")

    def get_all_records(self):
        """
        Get a list with all the records.
        This also serves to update the self.max_row and self.max_column attributes.
        """
        # Read some large number of records, to make sure we capture all the data.
        values =  self.read_values(read_range=["A", "Z"])
        return values

    def get_all_player_info(self):
        all_records = self.get_all_records()
        all_records.pop(0)
        headers = self.headers
        player_info_dicts = {}
        for record in all_records:
            name = record[0]
            player_info_dicts[name] = dict(zip(headers, record))
        return player_info_dicts

    def get_usernames(self):
        """
        Returns a list of registered usernames.
        """
        usernames = self.read_values(read_range=["A", "A"])
        # Only show through all
        return flatten_list(usernames)[1:]

    def get_headers(self):
        headers = self.read_values(read_range=["1", "1"])
        return flatten_list(headers)

    def get_player_info(self, username=None):
        """
        Reads the info of a player given a usename.
        params:
            username : string of the username to fetch the information of.
        returns:
            a dictionary of player information, keyed by the sheet headers.
            e.g. {'Username': 'Alice', 'Total accumulated AFKoins': '10', 'AFKoins spent': '1'}
        """
        headers = self.headers
        # Get the list of usernames
        usernames = self.usernames
        logger.info(username)
        if username in usernames:
            row_num = usernames.index(username) + 2
        player_info = self.read_values(read_range=[f"{row_num}", f"{row_num}"])
        player_info_dict = dict(zip(headers, flatten_list(player_info)))
        logger.info(player_info_dict)
        return player_info_dict

    def create_new_player(self, username=None):
        """
        Creates a new player. Will first check if the username has already been used.
        params:
            username : string of the username to create a new entry for.
        """
        # Make sure that the player usename is unique.
        if username in self.usernames:
            raise ValueError(f"Username '{username}' already exists.")
        else:
            # Create a new entry at the bottom of the list.
            # if N users exist, new entry should go in row N+2.
            values_to_write = [username]
            for i in range(len(self.headers)-1):
                values_to_write.append("0")
            #logger.info(f"{values_to_write}")
            logger.info("Updating coin_tracker")
            new_row_num = len(self.usernames)+2
            self.write_values(write_range=[f"{new_row_num}", f"{new_row_num}"], values=[values_to_write])
            
            #Match History Sheet - Stephen
            values_to_write = [username]
            for i in range(len(self.usernames)-1):
                values_to_write.append("0")
            values_to_write.append("NA")
            logger.info("Updating match_history")
            self.write_values(sheet_name='match_history',write_range=["B1", f"{len(self.usernames)}"], values=[self.usernames])
            self.write_values(sheet_name='match_history',write_range=[f"{new_row_num}", f"{len(self.usernames)+1}"], values=[values_to_write])

    def set_player_value(self, username=None, key=None, value=None):
        """
        Sets an attribute for a player to a certain value.
        params:
            username : string of the player name to alter the record of.
            key : The header entry of the attribute to change.
        """
        if username in self.usernames:
            if key is None or value is None:
                raise ValueError(f"Need a key value pair, got key: {key}, value: {value}.")
            elif key in self.headers:
                row_num = self.usernames.index(username) + 2
                col_num = self.headers.index(key) + 1
                col_char = excel_column_name(col_num)
                cell_name = f"{col_char}{row_num}"
                self.write_values(write_range=[f"{cell_name}", f"{cell_name}"], values=[[value]])
        else:
            raise ValueError(f"Username '{username}' does not exist.")

    def read_values(self, sheet_name='coin_tracker', read_range=['A1', 'A1']):
        """
        Reads values from a sheet, using a specified range.
        params:
            sheet_name : a string denoting the sheet to read from.
            read_range : two strings, denoting the range to read from
                         e.g. from A1 - B2 will read 4 cells.

        returns:
            The read data, formatted in rows.
            e.g. if read range is A1 - C3, will return:
            [[A1, A2, A3], [B1, B2, B3], [C1, C2, C3]]
        """
        range_string = f"{sheet_name}!{read_range[0]}:{read_range[1]}"
        result = self.sheet.values().get(spreadsheetId=AFKOIN_SHEET_ID,
                                    range=range_string).execute()
        values = result.get('values', [])
        return values

    def write_values(self, sheet_name='coin_tracker', write_range=[None, None], values=[None]):
        """
        Writes values to a sheet, using a specified range.
        params:
            sheet_name : a string denoting the sheet to write to.
            write_range : two strings, denoting the range to write to
                         e.g. from A1 - B2 will write to 4 cells.
            values : the values to write into the sheet.
                     Please format this as follows:
                     If wanting to write from A1 ~ C3, values should be of the form:
                     [[A1, A2, A3], [B1, B2, B3], [C1, C2, C3]].
                     Empty cells should be populated with an empty string.
        """
        if None in write_range:
            raise ValueError(f"write_range should not have None, got {write_range}.")
        body = {
            'values': values
        }
        range_string = f"{sheet_name}!{write_range[0]}:{write_range[1]}"
        result = self.sheet.values().update(
            spreadsheetId=AFKOIN_SHEET_ID, range=range_string,
            valueInputOption='USER_ENTERED', body=body).execute()
        logger.info(f"{result.get('updatedCells')} cells updated.")
        self.get_all_records()

    def prepare_credentials(self):
        """
        Checks for a token to access the google sheet, and failing that creates one.
        """
        self.creds = None
        # Use an existing token if it exists.
        if os.path.exists(self.token_json_path):
            self.creds = Credentials.from_authorized_user_file(self.token_json_path, SCOPES)
        # No existing token, need to log in using the OAuth consent screen.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_json_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Create a token so we don't need to manually log in next time.
            with open(self.token_json_path, 'w') as token:
                token.write(self.creds.to_json())

    @property
    def usernames(self):
        return self.get_usernames()

    @property
    def headers(self):
        return self.get_headers()

    @property
    def all_records(self):
        return self.get_all_records()


if __name__ == '__main__':
    # Set up logger
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s::%(levelname)s::%(message)s', '%Y-%m-%d %H:%M:%S')
    coloredlogs.install(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)

    ygos = YGOSpreadsheet()
    logger.info(ygos.usernames)
    # logger.info(ygos.read_values(read_range=["A", "A"]))
    # ygos.read_values(read_range=["A1", "E5"])
    # values = [["Evan", 50, 5]]
    # ygos.write_values(write_range=["A6", "E"], values=values)
    # ygos.get_player_info("Alice")
    # ygos.create_new_player("Fred")
    ygos.set_player_value(username="Fred", key="Current AFKoins", value="5")
    # print(ygos.sheet.get_all_records())
