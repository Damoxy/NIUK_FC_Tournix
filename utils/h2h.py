import streamlit as st
import pandas as pd
from utils.data_utils import get_h2h, display_division_name


def get_player_division(player, df, season):
    """Determine which division a player is in based on table structure"""
    if df.empty or "Twitter Handles" not in df.columns:
        return "Unknown"
    
    # Extract season number for comparison (e.g., "S5", "S6", "S7")
    season_num = season.replace('S', '')
    
    # Divisions only started from Season 5 onwards
    if int(season_num) < 5:
        return "Division 1"  # Pre-division era, consider all as single division
    
    # Convert to list to iterate through rows more easily
    df_rows = df.to_dict('records')
    div2_section_started = False
    
    for i, row in enumerate(df_rows):
        # Check if we've hit the DIV 2 section by looking across all columns for the marker
        row_text = ' '.join([str(val) for val in row.values() if pd.notna(val) and val != ''])
        
        # Look for Division 2 markers - make it more flexible for different seasons
        div2_markers = [
            'DIV 2', '(DIV 2)', 'DIVISION 2',
            f'SEASON {season_num} (DIV 2)',  # Season-specific marker
            f'S{season_num} (DIV 2)',       # Alternative format
            'FC26 SEASON',                   # Part of the header structure
        ]
        
        # Check if this row contains any DIV 2 marker
        if any(marker in row_text.upper() for marker in [m.upper() for m in div2_markers]):
            # Additional check: make sure it's actually a division header, not just a player name
            if 'SEASON' in row_text.upper() and 'DIV 2' in row_text.upper():
                div2_section_started = True
                continue
        
        # Check if this row contains our player
        twitter_handle = row.get('Twitter Handles', '')
        if pd.notna(twitter_handle) and str(twitter_handle).lower().strip() == player.lower().strip():
            if div2_section_started:
                return "Division 2"
            else:
                return "Division 1"
    
    # Fallback: if we can't find division markers, use position-based logic
    # This is for seasons where the division structure might be different
    df_clean = df.dropna(subset=['Twitter Handles'])
    df_clean = df_clean[df_clean['Twitter Handles'].str.contains('@', na=False)]
    
    player_row = df_clean[df_clean['Twitter Handles'].str.lower().str.strip() == player.lower().strip()]
    if not player_row.empty and 'Position' in player_row.columns:
        try:
            position = int(player_row['Position'].iloc[0])
            # For seasons 5+ with divisions, use position-based fallback
            # Typically positions 1-16 are Div 1, 17+ are Div 2
            # But this can vary by season, so this is just a fallback
            if position <= 16:
                return "Division 1"
            else:
                return "Division 2"
        except:
            pass
    
    return "Unknown"


def get_player_stats(player, tables, fixtures):
    """Get comprehensive player statistics across all seasons"""
    player_stats = {
        'seasons': [],
        'career_totals': {
            'MP': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Points': 0
        },
        'best_season': {'season': 'N/A', 'division': 'N/A', 'position': float('inf')},
        'highest_win': {'score': '0-0', 'opponent': None},
        'highest_defeat': {'score': '0-0', 'opponent': None},
        'seasonal_performance': {}
    }

    all_seasons = sorted(tables.keys())

    for season in all_seasons:
        table = tables.get(season)
        if table is not None and not table.empty and "Twitter Handles" in table.columns:
            player_row = table[table["Twitter Handles"].str.lower().str.strip() == player.lower().strip()]
            if not player_row.empty:
                player_stats['seasons'].append(season)
                
                # Update career totals
                for col in ['MP', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Points']:
                    if col in player_row:
                        value = player_row[col].values[0]
                        # Ensure value is numeric, defaulting to 0 if not
                        numeric_value = pd.to_numeric(value, errors='coerce')
                        if pd.notna(numeric_value):
                            player_stats['career_totals'][col] += numeric_value

                # Update best season
                division = get_player_division(player, table, season)
                
                # Correctly calculate position within the division
                if 'Position' in player_row.columns:
                    try:
                        position = int(player_row['Position'].iloc[0])
                    except (ValueError, TypeError):
                        position = player_row.index[0] + 1 # Fallback to index
                else:
                    position = player_row.index[0] + 1 # Fallback to index

                if division == 'Division 1' and position < player_stats['best_season']['position']:
                    player_stats['best_season'] = {
                        'season': season,
                        'division': division,
                        'position': position
                    }
                elif division == 'Division 2':
                    # For division 2, a lower position number is better.
                    # We need to handle the logic for what a "best season" in Div 2 means.
                    # Assuming for now any Div 1 season is better than any Div 2.
                    # If no best season is set, or the current best is also Div 2 and worse position.
                    if player_stats['best_season']['division'] != 'Division 1':
                         if position < player_stats['best_season']['position']:
                            player_stats['best_season'] = {
                                'season': season,
                                'division': division,
                                'position': position
                            }

                # Store seasonal performance for the chart
                player_stats['seasonal_performance'][season] = {
                    'position': position,
                    'division': division
                }

    # Find highest win and defeat from fixtures
    player_fixtures = [f for f in fixtures if player.lower() in (f['home'].lower(), f['away'].lower())]
    for fixture in player_fixtures:
        for leg_home, leg_away in [(fixture["home_leg1"], fixture["away_leg1"]), 
                                   (fixture["home_leg2"], fixture["away_leg2"])]:
            if leg_home is not None and leg_away is not None:
                if fixture["home"].lower() == player.lower():  # Player is home
                    goal_diff = leg_home - leg_away
                    opponent = fixture["away"]
                    score = f"{leg_home}-{leg_away}"
                else:  # Player is away
                    goal_diff = leg_away - leg_home
                    opponent = fixture["home"]
                    score = f"{leg_away}-{leg_home}"
                
                # Check for highest win
                if goal_diff > 0:
                    current_highest = player_stats['highest_win']['score']
                    if current_highest == '0-0':
                        current_diff = 0
                    else:
                        h, a = map(int, current_highest.split('-'))
                        current_diff = h - a
                    
                    if goal_diff > current_diff:
                        player_stats['highest_win'] = {
                            'score': score,
                            'opponent': opponent,
                            'season': fixture["season"]
                        }
                
                # Check for highest defeat
                elif goal_diff < 0:
                    current_highest = player_stats['highest_defeat']['score']
                    if current_highest == '0-0':
                        current_diff = 0
                    else:
                        h, a = map(int, current_highest.split('-'))
                        current_diff = abs(h - a)
                    
                    if abs(goal_diff) > current_diff:
                        player_stats['highest_defeat'] = {
                            'score': score,
                            'opponent': opponent,
                            'season': fixture["season"]
                        }
    
    return player_stats


def render_h2h(fixtures_filtered, player1, player2):
    # --- H2H Header ---
    st.markdown(
        "<h2 style='text-align:center; font-size:36px; color:#000000;'>Head-to-Head Results</h2>",
        unsafe_allow_html=True
    )

    # Get stats from perspective of player1
    matches, w1, d, l1 = get_h2h(fixtures_filtered, player1, player2)

    # Swap if player2 has more wins than player1
    if w1 < l1:
        matches, w1, d, l1 = get_h2h(fixtures_filtered, player2, player1)
        player1, player2 = player2, player1

    # --- Player names left & right ---
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; width: 100%; font-size: 28px; font-weight: bold;">
        <div style="flex:1; text-align:left; color:#000000;">{player1}</div>
        <div style="flex:1; text-align:right; color:#000000;">{player2}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- W/D/L cards (always from left player's perspective) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="card" style="background:#e8f5e9;color:#1b5e20;text-align:center;padding:10px;border-radius:10px;">
                <h1 style="font-size:48px;margin:0;">{w1}</h1>
                <p style="font-size:22px;margin:0;">Wins</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card" style="background:#eeeeee;color:#424242;text-align:center;padding:10px;border-radius:10px;">
                <h1 style="font-size:48px;margin:0;">{d}</h1>
                <p style="font-size:22px;margin:0;">Draws</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="card" style="background:#ffebee;color:#b71c1c;text-align:center;padding:10px;border-radius:10px;">
                <h1 style="font-size:48px;margin:0;">{l1}</h1>
                <p style="font-size:22px;margin:0;">Losses</p>
            </div>
        """, unsafe_allow_html=True)


    # --- Match history ---
    if matches:
        match_lines = []
        for season, rnd, home, away, hs, as_ in matches:
            hs_text = str(hs) if hs is not None else "-"
            as_text = str(as_) if as_ is not None else "-"

            # Default draw style
            score_style = "color:#424242;"  
            home_name, away_name = home, away

            if hs is not None and as_ is not None:
                if hs > as_:
                    score_style = "color:#1b5e20;"  # green
                    home_name = f"<b>{home}</b>"
                elif hs < as_:
                    score_style = "color:#1b5e20;"  # green
                    away_name = f"<b>{away}</b>"
                else:
                    score_style = "color:#424242;"  # gray

            # Compose match label
            division_label = display_division_name('Cup') if (rnd and 'Cup' in str(rnd)) or (home and away and home != away and home in ['Cup', 'CUP']) else None
            # Use division from fixtures if available
            division_label = None
            if hasattr(fixtures_filtered[0], 'division') or (isinstance(fixtures_filtered[0], dict) and 'division' in fixtures_filtered[0]):
                for f in fixtures_filtered:
                    if f['season'] == season and f['home'] == home and f['away'] == away and (f['home_leg1'] == hs or f['home_leg2'] == hs):
                        division_label = display_division_name(f['division'])
                        break
            if not division_label:
                division_label = ''
            # Compose round/label
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
        <div class="card" style="background:#f1f5f9; text-align:center;">
            <b style="font-size:24px; color:#00000;">Head-to-Head Matches</b><br><br>
            <span style="font-size:18px; color:#00000;">{match_text}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background-color:#f0f0f0; padding:15px; border-radius:10px; 
                color:#000000; text-align:center; font-size:16px; font-weight:bold;">
            No head-to-head matches found between these players.
            </div>""", unsafe_allow_html=True)


def render_player_profile(all_fixtures, all_tables, players):
    """Render the player profile page with sidebar player selection and comparison"""
    
    # Enhanced CSS for modern player profile page
    st.markdown("""
        <style>
            /* Modern dark theme with better contrast */
            .stApp {
                background: #3a3a3a !important;
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
                color: #2c3e50 !important;
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
            
            /* Override white text for metric containers - force inline colors to show */
            .metric-container div[style*="color"] {
                color: inherit !important;
            }
            
            /* Ensure metric container text is never white */
            .metric-container div {
                color: #2c3e50 !important;
            }
            
            .metric-container div[style*="color: #667eea"] {
                color: #667eea !important;
            }
            
            .metric-container div[style*="color: #28a745"] {
                color: #28a745 !important;
            }
            
            .metric-container div[style*="color: #ffc107"] {
                color: #ffc107 !important;
            }
            
            .metric-container div[style*="color: #dc3545"] {
                color: #dc3545 !important;
            }
            
            .metric-container div[style*="color: #764ba2"] {
                color: #764ba2 !important;
            }
            
            .metric-container div[style*="color: #6c757d"] {
                color: #6c757d !important;
            }
            
            /* Better text contrast and typography */
            .stMarkdown, .stMarkdown p, .stMarkdown div {
                color: #ffffff !important;
                font-weight: 500 !important;
            }
            
            /* Section headers with better styling */
            h1, h2, h3, h4 {
                color: #ffffff !important;
                font-weight: 700 !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
                margin-bottom: 1rem !important;
            }
            
            h3 {
                font-size: 1.8rem !important;
                margin-top: 2rem !important;
            }
            
            /* Selectbox and input styling */
            .stSelectbox label {
                color: #ffffff !important;
                font-weight: 600 !important;
                font-size: 1.1rem !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
            }
            
            .stSelectbox > div > div {
                background-color: rgba(255,255,255,0.9) !important;
                border-radius: 12px !important;
                border: 2px solid rgba(255,255,255,0.2) !important;
            }
            
            /* Dataframe styling */
            .stDataFrame {
                background: rgba(255,255,255,0.95) !important;
                border-radius: 16px !important;
                box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
                overflow: hidden !important;
            }
            
            /* Metrics styling */
            .metric-label {
                color: #ffffff !important;
                font-weight: 600 !important;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
            }
            
            /* Info box styling */
            .stAlert {
                background: rgba(255,255,255,0.1) !important;
                border: 2px solid rgba(255,255,255,0.2) !important;
                border-radius: 12px !important;
                backdrop-filter: blur(10px) !important;
            }
            
            .stAlert > div {
                color: #ffffff !important;
                font-weight: 500 !important;
            }
            
            /* Button styling */
            .stButton > button {
                background: linear-gradient(145deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                font-weight: 600 !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
                transition: all 0.3s ease !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Create sidebar for player selection
    with st.sidebar:
        st.markdown("### Select Players")
        
        # Add black background styling to sidebar for better visibility
        st.markdown("""
        <style>
            /* Sidebar background styling */
            [data-testid="stSidebar"] {
                background: #000000 !important;
            }
            
            /* Make selectbox text more visible on sidebar */
            [data-testid="stSidebar"] .stSelectbox label {
                color: #ffffff !important;
                font-weight: 600 !important;
            }
            
            /* Style selectbox options - black text on white background */
            [data-testid="stSidebar"] .stSelectbox > div > div {
                background-color: rgba(255,255,255,0.95) !important;
            }
            
            /* Make all text in selectbox black */
            [data-testid="stSidebar"] .stSelectbox div {
                color: #000000 !important;
            }
            
            /* Style selected value text */
            [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span {
                color: #000000 !important;
            }
            
            /* Style dropdown options */
            [data-testid="stSidebar"] [role="option"] {
                color: #000000 !important;
                background-color: rgba(255,255,255,0.95) !important;
            }
            
            /* Ensure input text is black */
            [data-testid="stSidebar"] input {
                color: #000000 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Player selection
        selected_player = st.selectbox("Player 1:", [""] + players, key="player1_select")
        
        # Comparison player selection
        compare_player = st.selectbox(
            "Player 2 (Compare):", 
            [""] + [p for p in players if p != selected_player] if selected_player else [""],
            key="player2_select"
        )
    
    if selected_player:
        player_stats = get_player_stats(selected_player, all_tables, all_fixtures)
        
        # H2H Comparison section
        if compare_player:
            compare_stats = get_player_stats(compare_player, all_tables, all_fixtures)
            
            st.markdown(f"<h4 style='text-align:center; color:#050505; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); font-size: 1.5rem; margin-bottom: 2rem;'>{selected_player.title()} vs {compare_player.title()}</h4>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            # Enhanced Player 1 stats card
            with col1:
                career1 = player_stats['career_totals']
                win_rate1 = round((career1['W'] / career1['MP']) * 100, 1) if career1['MP'] > 0 else 0
                win_color1 = "#28a745" if win_rate1 >= 50 else "#ffc107" if win_rate1 >= 30 else "#dc3545"
                st.markdown(f"""
                <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #667eea;">
                    <h3 style="color: #667eea; margin-bottom: 1.5rem; font-size: 1.4rem;">{selected_player.title()}</h3>
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
                        <div><strong style="color: #000000; font-size: 1.1rem;">GD:</strong> <span style="color: #000000; font-size: 1.3rem;">{career1['GD']:+d}</span></div>
                    </div>
                    <div style="text-align: center; margin-bottom: 1rem;"><strong style="color: #667eea; font-size: 0.9rem;">Seasons Played:</strong> <span style="color: #000000; font-size: 1rem;">{len(player_stats['seasons'])}</span></div>
                    <div style="border-top: 2px solid #e9ecef; padding-top: 1rem;">
                        <div style="margin-bottom: 0.5rem;"><strong style="color: #667eea;">Best Season:</strong> <span style="color: #000000;">{player_stats['best_season']['season']} ({player_stats['best_season']['division']} - Pos: {player_stats['best_season']['position']})</span></div>
                        <div style="margin-bottom: 0.5rem;"><strong style="color: #667eea;">Biggest Win:</strong> <span style="color: #000000;">{player_stats['highest_win']['score'] if player_stats['highest_win']['score'] != '0-0' else 'None'}{f" vs {player_stats['highest_win']['opponent'].title()}" if player_stats['highest_win']['score'] != '0-0' and player_stats['highest_win']['opponent'] else ''}</span></div>
                        <div><strong style="color: #667eea;">Biggest Loss:</strong> <span style="color: #000000;">{player_stats['highest_defeat']['score'] if player_stats['highest_defeat']['score'] != '0-0' else 'None'}{f" vs {player_stats['highest_defeat']['opponent'].title()}" if player_stats['highest_defeat']['score'] != '0-0' and player_stats['highest_defeat']['opponent'] else ''}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced Head-to-Head section in the middle
            with col2:
                compare_stats = get_player_stats(compare_player, all_tables, all_fixtures)
                matches, w1, d, l1 = get_h2h(all_fixtures, selected_player, compare_player)
                
                if matches:
                    st.markdown(f"""
                    <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #6c757d; height: 100%;">
                        <h3 style="color: #6c757d; margin-bottom: 1.5rem; font-size: 1.4rem;">Head-to-Head</h3>
                        <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 1.5rem; text-align: center;">
                            <div style="background: linear-gradient(145deg, #28a745 0%, #20c997 100%); color: white; padding: 0.8rem; border-radius: 8px;">
                                <div style="font-size: 1.8rem; font-weight: bold;">{w1}</div>
                                <div style="font-size: 0.9rem;">{selected_player.title()} Wins</div>
                            </div>
                            <div style="background: linear-gradient(145deg, #ffc107 0%, #ffdd57 100%); color: white; padding: 0.8rem; border-radius: 8px;">
                                <div style="font-size: 1.8rem; font-weight: bold;">{d}</div>
                                <div style="font-size: 0.9rem;">Draws</div>
                            </div>
                            <div style="background: linear-gradient(145deg, #dc3545 0%, #e74c3c 100%); color: white; padding: 0.8rem; border-radius: 8px;">
                                <div style="font-size: 1.8rem; font-weight: bold;">{l1}</div>
                                <div style="font-size: 0.9rem;">{compare_player.title()} Wins</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #6c757d; height: 100%;">
                        <h3 style="color: #6c757d; margin-bottom: 1.5rem; font-size: 1.4rem;">Head-to-Head</h3>
                        <div style="text-align: center; color: #000000; font-weight: 500; padding: 2rem 1rem;">
                            🤝 These players have never faced each other directly.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Enhanced Player 2 stats card
            with col3:
                career2 = compare_stats['career_totals']
                win_rate2 = round((career2['W'] / career2['MP']) * 100, 1) if career2['MP'] > 0 else 0
                win_color2 = "#28a745" if win_rate2 >= 50 else "#ffc107" if win_rate2 >= 30 else "#dc3545"
                st.markdown(f"""
                <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #764ba2;">
                    <h3 style="color: #764ba2; margin-bottom: 1.5rem; font-size: 1.4rem;">{compare_player.title()}</h3>
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
                        <div><strong style="color: #000000; font-size: 1.1rem;">GD:</strong> <span style="color: #000000; font-size: 1.3rem;">{career2['GD']:+d}</span></div>
                    </div>
                    <div style="text-align: center; margin-bottom: 1rem;"><strong style="color: #764ba2; font-size: 0.9rem;">Seasons Played:</strong> <span style="color: #000000; font-size: 1rem;">{len(compare_stats['seasons'])}</span></div>
                    <div style="border-top: 2px solid #e9ecef; padding-top: 1rem;">
                        <div style="margin-bottom: 0.5rem;"><strong style="color: #764ba2;">Best Season:</strong> <span style="color: #000000;">{compare_stats['best_season']['season']} ({compare_stats['best_season']['division']} - Pos: {compare_stats['best_season']['position']})</span></div>
                        <div style="margin-bottom: 0.5rem;"><strong style="color: #764ba2;">Biggest Win:</strong> <span style="color: #000000;">{compare_stats['highest_win']['score'] if compare_stats['highest_win']['score'] != '0-0' else 'None'}{f" vs {compare_stats['highest_win']['opponent'].title()}" if compare_stats['highest_win']['score'] != '0-0' and compare_stats['highest_win']['opponent'] else ''}</span></div>
                        <div><strong style="color: #764ba2;">Biggest Loss:</strong> <span style="color: #000000;">{compare_stats['highest_defeat']['score'] if compare_stats['highest_defeat']['score'] != '0-0' else 'None'}{f" vs {compare_stats['highest_defeat']['opponent'].title()}" if compare_stats['highest_defeat']['score'] != '0-0' and compare_stats['highest_defeat']['opponent'] else ''}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display full match history below
            if matches:
                st.markdown("#### Recent Matches")
                match_lines = []
                for season, rnd, home, away, hs, as_ in matches:
                    hs_text = str(hs) if hs is not None else "-"
                    as_text = str(as_) if as_ is not None else "-"

                    # Default draw style
                    score_style = "color:#424242;"  
                    home_name, away_name = home.title(), away.title()

                    if hs is not None and as_ is not None:
                        if hs > as_:
                            score_style = "color:#1b5e20;"  # green
                            home_name = f"<b>{home.title()}</b>"
                        elif hs < as_:
                            score_style = "color:#1b5e20;"  # green
                            away_name = f"<b>{away.title()}</b>"
                        else:
                            score_style = "color:#424242;"  # gray

                    # Get division info
                    division_label = ""
                    for f in all_fixtures:
                        if (f['season'] == season and f['home'] == home and f['away'] == away and 
                            (f['home_leg1'] == hs or f['home_leg2'] == hs)):
                            if f['division'] == 'Div1_Fixtures':
                                division_label = "Division 1"
                            elif f['division'] == 'Div2_Fixtures':
                                division_label = "Division 2"
                            elif f['division'] == 'Cup':
                                division_label = "Cup"
                            break

                    # Compose match label
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
                <div class="card" style="background:#f1f5f9; text-align:center;">
                    <span style="font-size:18px; color:#000000;">{match_text}</span>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 3rem; border-radius: 16px; border: 2px solid rgba(255,255,255,0.2); text-align: center; margin-top: 2rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⚽</div>
            <div style="font-size: 1.5rem; color: #ffffff; font-weight: 600; margin-bottom: 1rem;">
                Welcome to Player Profiles
            </div>
            <div style="font-size: 1.1rem; color: #ffffff; font-weight: 400; opacity: 0.8;">
                👆 Select a player from the dropdown above to view their detailed statistics, career highlights, and compare with other players.
            </div>
        </div>
        """, unsafe_allow_html=True)
