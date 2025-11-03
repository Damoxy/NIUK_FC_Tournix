import streamlit as st
from utils.config import get_app_title, get_season_urls
from utils.data_utils import load_fixtures_by_url, load_table_by_url
from utils.layout import set_page_config, inject_css, show_header, render_combined_league_record
from utils.h2h import render_h2h
# from fun_messages import get_random_loading_message

# --- CONFIG ---
set_page_config()
inject_css()

# Custom clickable navigation
st.sidebar.markdown("""
    <style>
        .nav-link {
            display: block;
            padding: 12px 16px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            text-decoration: none !important;
            color: #bdc3c7;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        .nav-link:hover {
            background: rgba(52, 152, 219, 0.2);
            color: #3498db;
            transform: translateX(5px);
            text-decoration: none !important;
        }
        .nav-link.active {
            background: rgba(52, 152, 219, 0.3);
            color: #3498db;
            border-left: 4px solid #3498db;
            text-decoration: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Current page indicator
st.sidebar.markdown('<a href="/" class="nav-link active">H2H</a>', unsafe_allow_html=True)
st.sidebar.markdown('<a href="/seed_reveal" class="nav-link">Seed Reveal</a>', unsafe_allow_html=True)

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
