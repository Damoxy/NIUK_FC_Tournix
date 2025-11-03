import streamlit as st
from utils.config import get_app_title, get_season_urls
from utils.data_utils import load_fixtures_by_url, load_table_by_url
from utils.layout import set_page_config, inject_css, show_header, render_combined_league_record
from utils.h2h import render_h2h
# from fun_messages import get_random_loading_message

# --- CONFIG ---
set_page_config()
inject_css()

APP_TITLE = get_app_title()
SEASON_URLS = get_season_urls()

# --- DATA ---
all_fixtures, all_tables = [], {}
with st.spinner("Loading data..."):
    for season, url in SEASON_URLS.items():
        all_fixtures.extend(load_fixtures_by_url(url, season))
        all_tables[season] = load_table_by_url(url, season)

players = sorted(set(f["home"] for f in all_fixtures) | set(f["away"] for f in all_fixtures))

# --- SIDEBAR ---
st.sidebar.title("⚙️")
max_seasons = len(SEASON_URLS)
season_limit = st.sidebar.slider("Include last N seasons", 1, max_seasons, max_seasons)

with st.sidebar.form("player_form"):
    player1 = st.selectbox("Select Player 1", players, index=0, key="player1_select")
    player2 = st.selectbox("Select Player 2", players, index=1, key="player2_select")
    submit = st.form_submit_button("Submit")

selected_seasons = sorted(list(SEASON_URLS.keys()))[-season_limit:]
fixtures_filtered = [f for f in all_fixtures if f["season"] in selected_seasons]
tables_filtered = {s: all_tables[s] for s in selected_seasons}

# --- MAIN CONTENT ---
show_header(APP_TITLE)
if submit:
    render_h2h(fixtures_filtered, player1, player2)
    render_combined_league_record(tables_filtered, [player1, player2])
