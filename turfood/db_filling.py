import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

import db_utils

SQL_PATH = os.path.join(os.path.dirname(__file__), 'turfood.sqlite3')
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__),'credentials.json')
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID of a spreadsheet.
SPREADSHEET_ID = '1dE78op3XZrKkd9g8-6y0VpsdlEWxTHjdINN0g6UZEH8'

# Values for supportive map. They suggest how to copy items from google spreadsheet
UNIQUE = 0
ALL = 1
# Supportive map for migrate data from google spreadsheet to SQLite
# ["SQL table name", "google table list name" : {"SQL table field name" : google list column number, "...": 2}
TABLE_FILLING_RULES = {
    ("product_types", "products", UNIQUE): (
                                                ("name", 0),
                                           ),
    ("products", "products", ALL): (
                                                ("name", 1),
                                                ("product_type_id", (0, "product_types", "id")),
                                   ),
    ("recipes", "recipes_product_sets", UNIQUE): (
                                                ("name", 1),
                                                 ),
    ("recipes_product_sets", "recipes_product_sets", ALL): (
                                                ("recipe_id", (0, "recipe_type", "id")),
                                                ("product_type_id", (1, "product_types", "id")),
                                                ("product_id", (2, "products","id")),
                                                ("amount", 1),
                                                           ),
    ("recipe_types", "recipes_product_sets", UNIQUE): (
                                                ("name", 5),
                                                      ),
    ("store_products", "store_products", ALL): (
                                                ("name", 0),
                                                ("product_id", (1, "products", "id")),
                                                ("cost", 4),
                                                ("carbon", 3),
                                                ("fat", 2),
                                                ("protein", 1),
                                                 ),
}


def get_google_spreadsheet_api():
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
                CREDENTIALS_PATH , SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()


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
        sheet = get_google_spreadsheet_api()
        successfully_filled_tables = []
        empty_tables = []

        for rule in TABLE_FILLING_RULES:
            try:
                result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                            range=rule[1]).execute()
                print(result)
                successfully_filled_tables.append(rule[1])
            except HttpError:
                empty_tables.append(rule[1])
        print(empty_tables)
        print(successfully_filled_tables)
        self.values = result.get('values', [])
        print(type(self.values))
        if not self.values:
            print('No data found.')
