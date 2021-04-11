from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
AFKOIN_SHEET_ID = '19lTpDVxdIcQqZ8CSXa2I3y_ENE_A5znImgvdR3-6A9Q'
SAMPLE_RANGE_NAME = 'coin_tracker!A1:E'

client_json = 'client.json'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                # 'credentials.json', SCOPES)
                'client.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=AFKOIN_SHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    # print(values)
    # return
    if not values:
        print('No data found.')
    else:
        print('Username: Total AFKOins')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[1]))

    result = sheet.values().get(spreadsheetId=AFKOIN_SHEET_ID,
                                range='coin_tracker!A1:A1').execute()
    values = result.get('values', [])
    print(values)


    range_name = 'coin_tracker!A5:E'
    values = [
        [
            "Daria", 40, 4
        ],
        # Additional rows ...
    ]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=AFKOIN_SHEET_ID, range=range_name,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

if __name__ == '__main__':
    main()
