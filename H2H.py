import streamlit as st
from utils.config import get_app_title, get_season_urls
from utils.data_utils import load_fixtures_by_url, load_table_by_url
from utils.layout import set_page_config, inject_css, show_header, render_combined_league_record
from utils.h2h import render_h2h

set_page_config()
inject_css()

APP_TITLE = get_app_title()
SEASON_URLS = get_season_urls()

# --- DATA ---
all_fixtures, all_tables = [], {}
with st.spinner("Loading data..."):
    for season, url in SEASON_URLS.items():
        season_fixtures = load_fixtures_by_url(url, season)
        # Normalize player names in fixtures to lowercase
        for f in season_fixtures:
            f["home"] = f["home"].lower().strip()
            f["away"] = f["away"].lower().strip()
        all_fixtures.extend(season_fixtures)
        # Normalize player names in tables to lowercase
        table = load_table_by_url(url, season)
        if not table.empty and "Twitter Handles" in table.columns:
            table["Twitter Handles"] = table["Twitter Handles"].astype(str).str.lower().str.strip()
        all_tables[season] = table

# Normalize player names to lowercase to avoid duplicates
players_raw = set(f["home"] for f in all_fixtures) | set(f["away"] for f in all_fixtures)
players = sorted({p for p in players_raw if p})

max_seasons = len(SEASON_URLS)
season_limit = st.sidebar.slider("Include last N seasons", 1, max_seasons, max_seasons)

with st.sidebar.form("player_form"):
    player1 = st.selectbox("Select Player 1", players, index=0, key="player1_select")
    player2 = st.selectbox("Select Player 2", players, index=1, key="player2_select")
    submit = st.form_submit_button("Submit")

selected_seasons = sorted(list(SEASON_URLS.keys()))[-season_limit:]
fixtures_filtered = [f for f in all_fixtures if f["season"] in selected_seasons]
tables_filtered = {s: all_tables[s] for s in selected_seasons}

show_header(APP_TITLE)

if not submit:
    st.markdown("""
    <style>
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #222831 !important;
    }
    .stMarkdown p, .stMarkdown li {
        color: #222831 !important;
        font-size: 1.18em !important;
    }
    .stMarkdown a {
        color: #007bff !important;
        text-decoration: underline;
        font-size: 1.18em !important;
    }
    .custom-roast-box {
        background: #f5f5f5;
        color: #222831;
        border-radius: 10px;
        padding: 1.2em 1em;
        margin-top: 1em;
        font-size: 1.1em;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        position: relative;
    }
    .custom-roast-copy-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        padding: 4px 8px;
        font-size: 0.9em;
        border-radius: 5px;
        border: none;
        background: #e0e0e0;
        color: #222831;
        cursor: pointer;
        transition: background 0.2s;
    }
    .custom-roast-copy-btn:hover {
        background: #bdbdbd;
        color: #222831;
    }
    .stButton>button {
        color: #fff;
        background: #007bff;
        border: none;
        border-radius: 6px;
        padding: 0.5em 1.2em;
        font-weight: 600;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background: #0056b3;
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    # Welcome to NIUK FC League
    
    <span style='font-size:1.18em;'>Use the sidebar to select players and compare head-to-head stats, or visit the <a href='./seed_reveal' target='_self'>Seed Reveal</a> page to participate in the Cup seeding.</span>
    
    <span style='font-size:1.18em;'>If you want to roast a player, just select a player in the drop down!</span>
    """, unsafe_allow_html=True)
    from utils.openrouter_utils import roast_player_with_openrouter
    # For anonymous roast: do not send player name to OpenRouter, use a placeholder
    anon_placeholder = "this player"
    player = st.selectbox(
        "Select a player to roast",
        players,
        key="roast_player_select"
    )
    st.markdown("""
    <div style='font-size:0.98em; color:#888; margin-bottom:0.5em;'>
        <b>N.B.:</b> Player names are <u>never</u> sent to any AI model, only stats are used. Roasts are generated purely for fun!
    </div>
    """, unsafe_allow_html=True)
    if st.button("Roast!"):
        # Show loading placeholder immediately
        loading_placeholder = st.empty()
        loading_placeholder.markdown("""
            <div style='text-align: center; padding: 20px; color: #666;'>
                <div style='display: inline-block; width: 30px; height: 30px; border: 3px solid #f3f3f3; border-top: 3px solid #007bff; border-radius: 50%; animation: spin 1s linear infinite;'></div>
                <p style='margin-top: 10px; font-style: italic;'>Generating roast... please wait!</p>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Gather stats for the selected player
        player_stats = []
        for season, df in all_tables.items():
            if not df.empty and "Twitter Handles" in df.columns:
                row = df[df["Twitter Handles"].astype(str).str.strip() == player]
                if not row.empty:
                    stats = []
                    for col in ["MP", "W", "D", "L", "GF", "GA", "GD", "Points"]:
                        if col in row:
                            val = row[col].values[0]
                            stats.append(f"{col}: {val}")
                    player_stats.append(f"{season}: {', '.join(stats)}")
        # Format stats for prompt: more natural, no 'Stats:' prefix, no pipes, no quotes
        stats_summary = '\n'.join(player_stats) if player_stats else "No stats found."
        
        # Generate roast
        roast = roast_player_with_openrouter(anon_placeholder, stats_summary)
        
        # Clear loading indicator
        loading_placeholder.empty()
        
        # Replace placeholder with actual player name in the response
        roast = roast.replace(anon_placeholder, player)
        # Show roast in a styled <div> that auto-expands to fit all content (no textarea, no copy button)
        st.markdown(f'''
            <div class="custom-roast-box" style="white-space:pre-wrap;word-break:break-word;">
                {roast}
            </div>
        ''', unsafe_allow_html=True)

if submit:
    render_h2h(fixtures_filtered, player1, player2)
    render_combined_league_record(tables_filtered, [player1, player2])
