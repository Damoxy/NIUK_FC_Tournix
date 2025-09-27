import toml
import gspread
from google.oauth2.service_account import Credentials

def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(CONFIG["gcp_service_account"], scopes=scopes)
    return gspread.authorize(creds)

def get_worksheet(sheet_name="FIXTURES", tab_name="seed"):
    client = get_gspread_client()
    sheet = client.open(sheet_name)
    return sheet.worksheet(tab_name)
