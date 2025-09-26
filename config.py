import streamlit as st

def get_app_title():
    return st.secrets["players"]["APP_TITLE"]

def get_season_urls():
    urls = dict(st.secrets["players"])
    urls.pop("APP_TITLE", None)
    return urls
