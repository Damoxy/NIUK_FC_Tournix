import streamlit as st
from utils.config import get_app_title, get_season_urls
from utils.data_utils import load_fixtures_by_url, load_table_by_url, get_h2h
from utils.layout import set_page_config, inject_css, show_header, render_combined_league_record
from utils.h2h import render_h2h
import pandas as pd
import altair as alt

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
    player1 = st.selectbox("Player 1", players, index=0, key="player1_select")
    player2 = st.selectbox("Player 2", players, index=1, key="player2_select")
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
        color: #000000 !important;
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
    # Prepare data for enhanced player profile UI
    submit_fixtures = [f for f in all_fixtures if f["season"] in selected_seasons]
    submit_tables = {s: all_tables[s] for s in selected_seasons}
    
    # Show enhanced player comparison instead of old H2H
    st.markdown("""
    <style>
        /* Modern dark theme with better contrast */
        .stApp {
            background: #ffffff !important;
            min-height: 100vh;
        }
        
        /* Enhanced card styling with modern look */
        .card {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%) !important;
            border: none !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
            padding: 1.5rem !important;
            margin-bottom: 1rem !important;
            color: #2c3e50 !important;
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        }
        
        .card:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 48px rgba(0,0,0,0.15) !important;
        }
        
        .card h3, .card h4 {
            color: #000000 !important;
            font-weight: 700 !important;
            margin-bottom: 1rem !important;
        }
        
        /* Enhanced metric containers */
        .metric-container {
            background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
            padding: 1.5rem;
            border-radius: 16px;
            border: none;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .metric-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(0,0,0,0.15);
        }
        
        .metric-container div {
            color: #2c3e50 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    #st.markdown(f"<h4 style='text-align:center; color:#ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); font-size: 1.5rem; margin-bottom: 2rem;'>{player1.title()} vs {player2.title()}</h4>", unsafe_allow_html=True)
    
    # Get player stats
    from utils.h2h import get_player_stats
    player1_stats = get_player_stats(player1, submit_tables, submit_fixtures)
    player2_stats = get_player_stats(player2, submit_tables, submit_fixtures)
    
    col1, col2 = st.columns(2)
    
    # Player 1 stats card
    with col1:
        career1 = player1_stats['career_totals']
        win_rate1 = round((career1['W'] / career1['MP']) * 100, 1) if career1['MP'] > 0 else 0
        win_color1 = "#28a745" if win_rate1 >= 50 else "#ffc107" if win_rate1 >= 30 else "#dc3545"
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #667eea;">
            <h3 style="color: #667eea; margin-bottom: 1.5rem; font-size: 1.4rem;">{player1.title()}</h3>
            <div style="background: {win_color1}; color: white; padding: 0.8rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 1.8rem; font-weight: bold;">{win_rate1}%</div>
                <div style="font-size: 0.9rem;">Win Percentage</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1rem; text-align: center;">
                <div><strong style="color: #28a745; font-size: 1.1rem;">W:</strong> <span style="color: #000000; font-size: 1.3rem;">{career1['W']}</span></div>
                <div><strong style="color: #ffc107; font-size: 1.1rem;">D:</strong> <span style="color: #000000; font-size: 1.3rem;">{career1['D']}</span></div>
                <div><strong style="color: #dc3545; font-size: 1.1rem;">L:</strong> <span style="color: #000000; font-size: 1.3rem;">{career1['L']}</span></div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1.5rem; text-align: center;">
                <div><strong style="color: #000000; font-size: 1.1rem;">GF:</strong> <span style="color: #000000; font-size: 1.3rem;">{career1['GF']}</span></div>
                <div><strong style="color: #000000; font-size: 1.1rem;">GA:</strong> <span style="color: #000000; font-size: 1.3rem;">{career1['GA']}</span></div>
                <div><strong style="color: #000000; font-size: 1.1rem;">GD:</strong> <span style="color: #000000; font-size: 1.3rem;">{int(career1['GD']):+d}</span></div>
            </div>
            <div style="text-align: center; margin-bottom: 1rem;"><strong style="color: #667eea; font-size: 0.9rem;">Seasons Played:</strong> <span style="color: #000000; font-size: 1rem;">{len(player1_stats['seasons'])}</span></div>
            <div style="border-top: 2px solid #e9ecef; padding-top: 1rem;">
                <div style="margin-bottom: 0.5rem;"><strong style="color: #667eea;">Best Season:</strong> <span style="color: #000000;">{player1_stats['best_season']['season']} ({player1_stats['best_season']['division']} - Pos: {player1_stats['best_season']['position']})</span></div>
                <div style="margin-bottom: 0.5rem;"><strong style="color: #667eea;">Biggest Win:</strong> <span style="color: #000000;">{player1_stats['highest_win']['score'] if player1_stats['highest_win']['score'] != '0-0' else 'None'}{f" vs {player1_stats['highest_win']['opponent'].title()}" if player1_stats['highest_win']['score'] != '0-0' and player1_stats['highest_win']['opponent'] else ''}</span></div>
                <div><strong style="color: #667eea;">Biggest Loss:</strong> <span style="color: #000000;">{player1_stats['highest_defeat']['score'] if player1_stats['highest_defeat']['score'] != '0-0' else 'None'}{f" vs {player1_stats['highest_defeat']['opponent'].title()}" if player1_stats['highest_defeat']['score'] != '0-0' and player1_stats['highest_defeat']['opponent'] else ''}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Player 2 stats card
    with col2:
        career2 = player2_stats['career_totals']
        win_rate2 = round((career2['W'] / career2['MP']) * 100, 1) if career2['MP'] > 0 else 0
        win_color2 = "#28a745" if win_rate2 >= 50 else "#ffc107" if win_rate2 >= 30 else "#dc3545"
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #764ba2;">
            <h3 style="color: #764ba2; margin-bottom: 1.5rem; font-size: 1.4rem;">{player2.title()}</h3>
            <div style="background: {win_color2}; color: white; padding: 0.8rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 1.8rem; font-weight: bold;">{win_rate2}%</div>
                <div style="font-size: 0.9rem;">Win Percentage</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1rem; text-align: center;">
                <div><strong style="color: #28a745; font-size: 1.1rem;">W:</strong> <span style="color: #000000; font-size: 1.3rem;">{career2['W']}</span></div>
                <div><strong style="color: #ffc107; font-size: 1.1rem;">D:</strong> <span style="color: #000000; font-size: 1.3rem;">{career2['D']}</span></div>
                <div><strong style="color: #dc3545; font-size: 1.1rem;">L:</strong> <span style="color: #000000; font-size: 1.3rem;">{career2['L']}</span></div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1.5rem; text-align: center;">
                <div><strong style="color: #000000; font-size: 1.1rem;">GF:</strong> <span style="color: #000000; font-size: 1.3rem;">{career2['GF']}</span></div>
                <div><strong style="color: #000000; font-size: 1.1rem;">GA:</strong> <span style="color: #000000; font-size: 1.3rem;">{career2['GA']}</span></div>
                <div><strong style="color: #000000; font-size: 1.1rem;">GD:</strong> <span style="color: #000000; font-size: 1.3rem;">{int(career2['GD']):+d}</span></div>
            </div>
            <div style="text-align: center; margin-bottom: 1rem;"><strong style="color: #764ba2; font-size: 0.9rem;">Seasons Played:</strong> <span style="color: #000000; font-size: 1rem;">{len(player2_stats['seasons'])}</span></div>
            <div style="border-top: 2px solid #e9ecef; padding-top: 1rem;">
                <div style="margin-bottom: 0.5rem;"><strong style="color: #764ba2;">Best Season:</strong> <span style="color: #000000;">{player2_stats['best_season']['season']} ({player2_stats['best_season']['division']} - Pos: {player2_stats['best_season']['position']})</span></div>
                <div style="margin-bottom: 0.5rem;"><strong style="color: #764ba2;">Biggest Win:</strong> <span style="color: #000000;">{player2_stats['highest_win']['score'] if player2_stats['highest_win']['score'] != '0-0' else 'None'}{f" vs {player2_stats['highest_win']['opponent'].title()}" if player2_stats['highest_win']['score'] != '0-0' and player2_stats['highest_win']['opponent'] else ''}</span></div>
                <div><strong style="color: #764ba2;">Biggest Loss:</strong> <span style="color: #000000;">{player2_stats['highest_defeat']['score'] if player2_stats['highest_defeat']['score'] != '0-0' else 'None'}{f" vs {player2_stats['highest_defeat']['opponent'].title()}" if player2_stats['highest_defeat']['score'] != '0-0' and player2_stats['highest_defeat']['opponent'] else ''}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Create a DataFrame for the line chart
    all_seasons = sorted(list(SEASON_URLS.keys()))
    chart_data = []

    for season in all_seasons:
        # Player 1
        p1_perf = player1_stats['seasonal_performance'].get(season)
        if p1_perf:
            pos = p1_perf['position']
            # Division 1: Invert position (1→45, 5→41, 45→1) so UP = better
            # Division 2: Keep position as negative so UP from N/A is also better (-1, -5, -30)
            if p1_perf['division'] == 'Division 1':
                pos = 46 - pos  # Invert: position 1 becomes 45, position 45 becomes 1
            else:  # Division 2
                pos = -pos  # Make negative
            chart_data.append({
                'Season': season, 
                'Player': player1.title(), 
                'Position': pos, 
                'Division': p1_perf['division'],
                'DisplayLabel': f"DIV 1: {p1_perf['position']}" if p1_perf['division'] == 'Division 1' else f"DIV 2: {p1_perf['position']}"
            })
        else:
            chart_data.append({
                'Season': season, 
                'Player': player1.title(), 
                'Position': 0, 
                'Division': 'DP',
                'DisplayLabel': 'DP (Didn\'t Participate)'
            })

        # Player 2
        p2_perf = player2_stats['seasonal_performance'].get(season)
        if p2_perf:
            pos = p2_perf['position']
            # Division 1: Invert position so UP = better
            # Division 2: Keep position as negative
            if p2_perf['division'] == 'Division 1':
                pos = 46 - pos  # Invert: position 1 becomes 45, position 45 becomes 1
            else:  # Division 2
                pos = -pos  # Make negative
            chart_data.append({
                'Season': season, 
                'Player': player2.title(), 
                'Position': pos, 
                'Division': p2_perf['division'],
                'DisplayLabel': f"DIV 1: {p2_perf['position']}" if p2_perf['division'] == 'Division 1' else f"DIV 2: {p2_perf['position']}"
            })
        else:
            chart_data.append({
                'Season': season, 
                'Player': player2.title(), 
                'Position': 0, 
                'Division': 'DP',
                'DisplayLabel': 'DP (Didn\'t Participate)'
            })

    df_chart = pd.DataFrame(chart_data)

    # Calculate dynamic scale based on actual data range
    if not df_chart.empty:
        # Get the max absolute value from the data (excluding N/A which is 0)
        # This includes both inverted Div 1 positions (1-30) and negative Div 2 positions (-1 to -30)
        positions = df_chart[df_chart['Position'] != 0]['Position'].values
        if len(positions) > 0:
            max_pos = max(abs(positions))
            # Round up to nearest multiple of 5 for cleaner scale
            scale_range = max(int((max_pos * 1.1 + 4) / 5) * 5, 10)
        else:
            scale_range = 30
    else:
        scale_range = 30

    # Create the Altair chart with dual-scale visualization
    # INVERTED LOGIC (so UP always = better performance):
    # Division 1: Position 1 (best) → 45 (chart height), drops show decline
    # Division 2: Position 1 (best) → -1 (chart), drops show decline  
    # DP: 0 in the middle (shown in red/orange with thicker line)
    
    # Main line chart for non-DP data
    non_dp_data = df_chart[df_chart['Position'] != 0]
    
    # Regular lines for Division 1 and 2
    main_chart = alt.Chart(non_dp_data).mark_line(point=True, size=2, opacity=0.8).encode(
        x=alt.X('Season:N', sort=all_seasons, title='Season', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Position:Q',
                scale=alt.Scale(domain=[-scale_range, scale_range], zero=True),
                axis=alt.Axis(
                    labelExpr="datum.value == 0 ? 'DP' : datum.value > 0 ? 'DIV 1: ' + (46 - datum.value) : 'DIV 2: ' + (-datum.value)",
                    labelAngle=0
                ), 
                title=None),
        color=alt.Color('Player:N', scale=alt.Scale(scheme='category10')),
        tooltip=['Player:N', 'Season:N', 'DisplayLabel:N', 'Division:N']
    )
    
    # Add white dotted reference line at y=0 (DP line) that spans entire chart
    dp_reference = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        strokeDash=[3, 3],
        size=5,
        opacity=0.8,
        color='#FFFFFF'
    ).encode(y='y:Q')
    
    # Combine all charts
    chart = (main_chart + dp_reference).properties(
        title=alt.TitleParams(text='Seasonal Performance Comparison', anchor='middle', align='center'),
        height=500,
        width='container'
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # Head-to-Head section
    st.markdown("#### Head-to-Head")
    matches, w1, d, l1 = get_h2h(submit_fixtures, player1, player2)
    
    if matches:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container" style="background: linear-gradient(145deg, #28a745 0%, #20c997 100%); color: white;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{w1}</div>
                <div style="font-size: 1rem; font-weight: 600;">{player1.title()} Wins</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-container" style="background: linear-gradient(145deg, #ffc107 0%, #ffdd57 100%); color: white;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{d}</div>
                <div style="font-size: 1rem; font-weight: 600;">Draws</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-container" style="background: linear-gradient(145deg, #dc3545 0%, #e74c3c 100%); color: white;">
                <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{l1}</div>
                <div style="font-size: 1rem; font-weight: 600;">{player2.title()} Wins</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Display match history
        match_lines = []
        for season, rnd, home, away, hs, as_ in matches:
            hs_text = str(hs) if hs is not None else "-"
            as_text = str(as_) if as_ is not None else "-"

            score_style = "color:#424242;"  
            home_name, away_name = home.title(), away.title()

            if hs is not None and as_ is not None:
                if hs > as_:
                    score_style = "color:#1b5e20;"
                    home_name = f"<b>{home.title()}</b>"
                elif hs < as_:
                    score_style = "color:#1b5e20;"
                    away_name = f"<b>{away.title()}</b>"
                else:
                    score_style = "color:#424242;"

            division_label = ""
            for f in submit_fixtures:
                if (f['season'] == season and f['home'] == home and f['away'] == away and 
                    (f['home_leg1'] == hs or f['home_leg2'] == hs)):
                    if f['division'] == 'Div1_Fixtures':
                        division_label = "Division 1"
                    elif f['division'] == 'Div2_Fixtures':
                        division_label = "Division 2"
                    elif f['division'] == 'Cup':
                        division_label = "Cup"
                    break

            if rnd:
                match_label = f"{season} {division_label} {rnd} :"
            else:
                match_label = f"{season} {division_label} :"
            match_label = match_label.replace('  ', ' ').strip()

            match_lines.append(
                f"{match_label} {home_name} "
                f"<span style='{score_style}'>{hs_text}-{as_text}</span> {away_name}"
            )

        match_text = "<br>".join(match_lines)

        st.markdown(f"""
        <div class="card" style="background:#f1f5f9; text-align:center; margin-top: 1rem;">
            <b style="font-size:24px; color:#000000;">Head-to-Head Matches</b><br><br>
            <span style="font-size:18px; color:#000000;">{match_text}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 16px; border: 2px solid rgba(255,255,255,0.2); text-align: center;">
            <div style="font-size: 1.2rem; color: #ffffff; font-weight: 500;">
                🤝 These players have never faced each other directly.
            </div>
        </div>
        """, unsafe_allow_html=True)
