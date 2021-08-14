import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

import db_utils

SQL_PATH = os.path.join(os.path.dirname(__file__), 'turfood.sqlite3')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1dE78op3XZrKkd9g8-6y0VpsdlEWxTHjdINN0g6UZEH8'
SAMPLE_RANGE_NAME = 'recipes_product_sets(new)!A2:F'

class TurFoodDB(object):
    """
    Create database tables from DEFAULT_SQL_PATH and fill it with actual data
    """
    def __init__(self):
        self.conn = db_utils.create_connection(SQL_PATH)
        self.table_names = self.get_sql_table_names()
        self.values = None

    def get_sql_table_names(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [item for sublist in cur.fetchall() for item in sublist if (item != 'sqlite_sequence') ]

    def get_google_spreadsheet_data(self):
        successfully_filled_tables = []
        empty_tables = []
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
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        for table_name in self.table_names:
            try:
                result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                            range=table_name).execute()
                print(result)
                successfully_filled_tables.append(table_name)
            except HttpError:
                empty_tables.append(table_name)
        print(empty_tables)
        print(successfully_filled_tables)
        self.values = result.get('values', [])
        print(type(self.values))
        if not self.values:
            print('No data found.')
