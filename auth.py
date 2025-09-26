import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def init_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict,
        ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)
