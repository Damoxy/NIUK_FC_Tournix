import streamlit as st
import pandas as pd
from utils.config import get_app_title, get_season_urls
from utils.data_utils import load_fixtures_by_url, load_table_by_url
from utils.layout import set_page_config, inject_css, show_header
from utils.data_utils import get_h2h

set_page_config()
inject_css()

# Enhanced CSS for modern player profile page
st.markdown("""
    <style>
        /* Modern dark theme with better contrast */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
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
    stats = {
        'seasons': {},
        'career_totals': {"MP":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Points":0},
        'highest_win': {'score': '0-0', 'opponent': '', 'season': ''},
        'highest_defeat': {'score': '0-0', 'opponent': '', 'season': ''},
        'best_season': {'season': '', 'position': 999, 'points': 0, 'division': ''},
        'worst_season': {'season': '', 'position': 0, 'points': 0}
    }
    
    # Season-by-season stats
    for season, df in tables.items():
        if df.empty or "Twitter Handles" not in df.columns:
            continue
        
        df.columns = [str(c).strip() for c in df.columns]
        df["Twitter Handles"] = df["Twitter Handles"].astype(str).str.strip()
        row = df[df["Twitter Handles"] == player]
        
        if not row.empty:
            season_data = {}
            
            # Get basic stats
            for k in ["MP","W","D","L","Points"]:
                if k in row:
                    try: 
                        val = int(float(str(row[k].values[0]).replace(",","").strip()) or 0)
                        season_data[k] = val
                        stats['career_totals'][k] += val
                    except: 
                        season_data[k] = 0
            
            # Get goals
            if "GF" in row.columns and "GA" in row.columns:
                try:
                    gf = int(str(row["GF"].values[0]).replace(",","").strip())
                    ga = int(str(row["GA"].values[0]).replace(",","").strip())
                    season_data["GF"] = gf
                    season_data["GA"] = ga
                    stats['career_totals']["GF"] += gf
                    stats['career_totals']["GA"] += ga
                except: 
                    season_data["GF"] = 0
                    season_data["GA"] = 0
            elif "+ / -" in row.columns:
                try:
                    gf, ga = str(row["+ / -"].values[0]).strip().split("/")
                    gf, ga = int(gf.strip()), int(ga.strip())
                    season_data["GF"] = gf
                    season_data["GA"] = ga
                    stats['career_totals']["GF"] += gf
                    stats['career_totals']["GA"] += ga
                except: 
                    season_data["GF"] = 0
                    season_data["GA"] = 0
            
            season_data["GD"] = season_data["GF"] - season_data["GA"]
            
            # Get position
            if "Position" in row.columns:
                try:
                    position = int(str(row["Position"].values[0]).strip())
                    season_data["Position"] = position
                except:
                    season_data["Position"] = 999
            else:
                season_data["Position"] = 999
            
            stats['seasons'][season] = season_data
            
            # Check for best/worst season
            if season_data["Position"] < stats['best_season']['position']:
                stats['best_season'] = {
                    'season': season,
                    'position': season_data["Position"],
                    'points': season_data["Points"],
                    'division': get_player_division(player, df, season)
                }
            
            if season_data["Position"] > stats['worst_season']['position']:
                stats['worst_season'] = {
                    'season': season,
                    'position': season_data["Position"],
                    'points': season_data["Points"]
                }
    
    # Calculate career GD
    stats['career_totals']["GD"] = stats['career_totals']["GF"] - stats['career_totals']["GA"]
    
    # Find highest win/defeat from fixtures
    for fixture in fixtures:
        if fixture["home"] == player or fixture["away"] == player:
            for leg_home, leg_away in [(fixture["home_leg1"], fixture["away_leg1"]), 
                                     (fixture["home_leg2"], fixture["away_leg2"])]:
                if leg_home is not None and leg_away is not None:
                    if fixture["home"] == player:  # Player is home
                        goal_diff = leg_home - leg_away
                        opponent = fixture["away"]
                        score = f"{leg_home}-{leg_away}"
                    else:  # Player is away
                        goal_diff = leg_away - leg_home
                        opponent = fixture["home"]
                        score = f"{leg_away}-{leg_home}"
                    
                    # Check for highest win
                    if goal_diff > 0:
                        current_highest = stats['highest_win']['score']
                        if current_highest == '0-0':
                            current_diff = 0
                        else:
                            h, a = map(int, current_highest.split('-'))
                            current_diff = h - a
                        
                        if goal_diff > current_diff:
                            stats['highest_win'] = {
                                'score': score,
                                'opponent': opponent,
                                'season': fixture["season"]
                            }
                    
                    # Check for highest defeat
                    elif goal_diff < 0:
                        current_highest = stats['highest_defeat']['score']
                        if current_highest == '0-0':
                            current_diff = 0
                        else:
                            h, a = map(int, current_highest.split('-'))
                            current_diff = abs(h - a)
                        
                        if abs(goal_diff) > current_diff:
                            stats['highest_defeat'] = {
                                'score': score,
                                'opponent': opponent,
                                'season': fixture["season"]
                            }
    
    return stats

# --- UI ---
st.title("⚽ Player Profile")

# Player selection
selected_player = st.selectbox("Select a player to view their profile:", [""] + players)

if selected_player:
    player_stats = get_player_stats(selected_player, all_tables, all_fixtures)
    
    st.markdown(f"<h2 style='text-align:center; color:#ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>{selected_player.title()}</h2>", unsafe_allow_html=True)
    
    # Enhanced career statistics with modern design
    st.markdown("### 📈 Career Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    career = player_stats['career_totals']
    win_rate = round((career['W'] / career['MP']) * 100, 1) if career['MP'] > 0 else 0
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <div style="font-size: 2.5rem; font-weight: bold; color: #000000; margin-bottom: 0.5rem;">{}</div>
            <div style="font-size: 1.1rem; color: #000000; font-weight: 600;">Total Matches</div>
        </div>
        """.format(career['MP']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container">
            <div style="font-size: 2.5rem; font-weight: bold; color: #000000; margin-bottom: 0.5rem;">{}%</div>
            <div style="font-size: 1.1rem; color: #000000; font-weight: 600;">Win Percentage</div>
        </div>
        """.format(win_rate), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-container">
            <div style="font-size: 2.5rem; font-weight: bold; color: #000000; margin-bottom: 0.5rem;">{}</div>
            <div style="font-size: 1.1rem; color: #000000; font-weight: 600;">Total Points</div>
        </div>
        """.format(career['Points']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-container">
            <div style="font-size: 2.5rem; font-weight: bold; color: #000000; margin-bottom: 0.5rem;">{}</div>
            <div style="font-size: 1.1rem; color: #000000; font-weight: 600;">Goal Difference</div>
        </div>
        """.format(f"+{career['GD']}" if career['GD'] >= 0 else str(career['GD'])), unsafe_allow_html=True)
    
    # Enhanced Career Highlights with modern gradient cards
    st.markdown("### 🏆 Career Highlights")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card" style="background: linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%); border: 2px solid #28a745; box-shadow: 0 8px 32px rgba(40, 167, 69, 0.2);">
            <h4 style="color: #155724; margin-bottom: 1rem; font-size: 1.3rem;">🥇 Best Season</h4>
            <div style="font-size: 1.4rem; font-weight: bold; color: #155724; margin-bottom: 0.5rem;">{player_stats['best_season']['season']}</div>
            <div style="color: #155724; margin-bottom: 0.3rem; font-size: 1.1rem;">Division: {player_stats['best_season']['division']}</div>
            <div style="color: #155724; margin-bottom: 0.3rem; font-size: 1.1rem;">Position: {player_stats['best_season']['position']}</div>
            <div style="color: #155724; font-size: 1.1rem;">Points: {player_stats['best_season']['points']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if player_stats['highest_win']['score'] != '0-0':
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(145deg, #d1ecf1 0%, #bee5eb 100%); border: 2px solid #17a2b8; box-shadow: 0 8px 32px rgba(23, 162, 184, 0.2);">
                <h4 style="color: #0c5460; margin-bottom: 1rem; font-size: 1.3rem;">💪 Biggest Win</h4>
                <div style="font-size: 1.4rem; font-weight: bold; color: #0c5460; margin-bottom: 0.5rem;">{player_stats['highest_win']['score']}</div>
                <div style="color: #0c5460; margin-bottom: 0.3rem; font-size: 1.1rem;">vs {player_stats['highest_win']['opponent'].title()}</div>
                <div style="color: #0c5460; font-size: 1rem;">{player_stats['highest_win']['season']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="background: linear-gradient(145deg, #fff3cd 0%, #ffeaa7 100%); border: 2px solid #ffc107; box-shadow: 0 8px 32px rgba(255, 193, 7, 0.2);">
                <h4 style="color: #856404; margin-bottom: 1rem; font-size: 1.3rem;">💪 Biggest Win</h4>
                <div style="color: #856404; font-size: 1.1rem;">No wins recorded</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if player_stats['highest_defeat']['score'] != '0-0':
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(145deg, #f8d7da 0%, #f1b0b7 100%); border: 2px solid #dc3545; box-shadow: 0 8px 32px rgba(220, 53, 69, 0.2);">
                <h4 style="color: #721c24; margin-bottom: 1rem; font-size: 1.3rem;">😅 Heaviest Defeat</h4>
                <div style="font-size: 1.4rem; font-weight: bold; color: #721c24; margin-bottom: 0.5rem;">{player_stats['highest_defeat']['score']}</div>
                <div style="color: #721c24; margin-bottom: 0.3rem; font-size: 1.1rem;">vs {player_stats['highest_defeat']['opponent'].title()}</div>
                <div style="color: #721c24; font-size: 1rem;">{player_stats['highest_defeat']['season']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="background: linear-gradient(145deg, #d4edda 0%, #c3e6cb 100%); border: 2px solid #28a745; box-shadow: 0 8px 32px rgba(40, 167, 69, 0.2);">
                <h4 style="color: #155724; margin-bottom: 1rem; font-size: 1.3rem;">😅 Heaviest Defeat</h4>
                <div style="color: #155724; font-size: 1.1rem;">No defeats recorded</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Season-by-season breakdown
    if player_stats['seasons']:
        st.markdown("### 📊 Season-by-Season Performance")
        
        seasons_data = []
        for season, data in player_stats['seasons'].items():
            win_pct = round((data['W'] / data['MP']) * 100, 1) if data['MP'] > 0 else 0
            seasons_data.append({
                'Season': season,
                'Position': data['Position'] if data['Position'] != 999 else 'N/A',
                'MP': data['MP'],
                'W': data['W'],
                'D': data['D'],
                'L': data['L'],
                'Win %': f"{win_pct}%",
                'GF': data['GF'],
                'GA': data['GA'],
                'GD': f"+{data['GD']}" if data['GD'] >= 0 else str(data['GD']),
                'Points': data['Points']
            })
        
        import pandas as pd
        df_display = pd.DataFrame(seasons_data)
        st.dataframe(df_display, use_container_width=True)
    
    # H2H Comparison section
    st.markdown("### 🆚 Compare with Another Player")
    compare_player = st.selectbox("Select player to compare with:", [""] + [p for p in players if p != selected_player])
    
    if compare_player:
        compare_stats = get_player_stats(compare_player, all_tables, all_fixtures)
        
        st.markdown(f"<h4 style='text-align:center; color:#ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); font-size: 1.5rem; margin-bottom: 2rem;'>{selected_player.title()} vs {compare_player.title()}</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        # Enhanced Player 1 stats card
        with col1:
            career1 = player_stats['career_totals']
            win_rate1 = round((career1['W'] / career1['MP']) * 100, 1) if career1['MP'] > 0 else 0
            win_color1 = "#28a745" if win_rate1 >= 50 else "#ffc107" if win_rate1 >= 30 else "#dc3545"
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 1.5rem; font-size: 1.4rem;">{selected_player.title()}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div><strong style="color: #000000;">Matches:</strong> <span style="color: #000000;">{career1['MP']}</span></div>
                    <div><strong style="color: #000000;">Points:</strong> <span style="color: #000000;">{career1['Points']}</span></div>
                </div>
                <div style="background: {win_color1}; color: white; padding: 0.8rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.8rem; font-weight: bold;">{win_rate1}%</div>
                    <div style="font-size: 0.9rem;">Win Percentage</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1rem; text-align: center;">
                    <div><strong style="color: #28a745;">W:</strong> <span style="color: #000000;">{career1['W']}</span></div>
                    <div><strong style="color: #ffc107;">D:</strong> <span style="color: #000000;">{career1['D']}</span></div>
                    <div><strong style="color: #dc3545;">L:</strong> <span style="color: #000000;">{career1['L']}</span></div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1.5rem; text-align: center;">
                    <div><strong style="color: #000000;">GF:</strong> <span style="color: #000000;">{career1['GF']}</span></div>
                    <div><strong style="color: #000000;">GA:</strong> <span style="color: #000000;">{career1['GA']}</span></div>
                    <div><strong style="color: #000000;">GD:</strong> <span style="color: #000000;">{career1['GD']:+d}</span></div>
                </div>
                <div style="border-top: 2px solid #e9ecef; padding-top: 1rem;">
                    <div style="margin-bottom: 0.5rem;"><strong style="color: #667eea;">Best Season:</strong> <span style="color: #000000;">{player_stats['best_season']['season']} ({player_stats['best_season']['division']} - Pos: {player_stats['best_season']['position']})</span></div>
                    <div style="margin-bottom: 0.5rem;"><strong style="color: #667eea;">Biggest Win:</strong> <span style="color: #000000;">{player_stats['highest_win']['score'] if player_stats['highest_win']['score'] != '0-0' else 'None'}{f" vs {player_stats['highest_win']['opponent'].title()}" if player_stats['highest_win']['score'] != '0-0' and player_stats['highest_win']['opponent'] else ''}</span></div>
                    <div><strong style="color: #667eea;">Biggest Loss:</strong> <span style="color: #000000;">{player_stats['highest_defeat']['score'] if player_stats['highest_defeat']['score'] != '0-0' else 'None'}{f" vs {player_stats['highest_defeat']['opponent'].title()}" if player_stats['highest_defeat']['score'] != '0-0' and player_stats['highest_defeat']['opponent'] else ''}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Player 2 stats card
        with col2:
            career2 = compare_stats['career_totals']
            win_rate2 = round((career2['W'] / career2['MP']) * 100, 1) if career2['MP'] > 0 else 0
            win_color2 = "#28a745" if win_rate2 >= 50 else "#ffc107" if win_rate2 >= 30 else "#dc3545"
            st.markdown(f"""
            <div class="card" style="background: linear-gradient(145deg, #ffffff 0%, #f1f3f4 100%); border-left: 5px solid #764ba2;">
                <h3 style="color: #764ba2; margin-bottom: 1.5rem; font-size: 1.4rem;">{compare_player.title()}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div><strong style="color: #000000;">Matches:</strong> <span style="color: #000000;">{career2['MP']}</span></div>
                    <div><strong style="color: #000000;">Points:</strong> <span style="color: #000000;">{career2['Points']}</span></div>
                </div>
                <div style="background: {win_color2}; color: white; padding: 0.8rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;">
                    <div style="font-size: 1.8rem; font-weight: bold;">{win_rate2}%</div>
                    <div style="font-size: 0.9rem;">Win Percentage</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1rem; text-align: center;">
                    <div><strong style="color: #28a745;">W:</strong> <span style="color: #000000;">{career2['W']}</span></div>
                    <div><strong style="color: #ffc107;">D:</strong> <span style="color: #000000;">{career2['D']}</span></div>
                    <div><strong style="color: #dc3545;">L:</strong> <span style="color: #000000;">{career2['L']}</span></div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin-bottom: 1.5rem; text-align: center;">
                    <div><strong style="color: #000000;">GF:</strong> <span style="color: #000000;">{career2['GF']}</span></div>
                    <div><strong style="color: #000000;">GA:</strong> <span style="color: #000000;">{career2['GA']}</span></div>
                    <div><strong style="color: #000000;">GD:</strong> <span style="color: #000000;">{career2['GD']:+d}</span></div>
                </div>
                <div style="border-top: 2px solid #e9ecef; padding-top: 1rem;">
                    <div style="margin-bottom: 0.5rem;"><strong style="color: #764ba2;">Best Season:</strong> <span style="color: #000000;">{compare_stats['best_season']['season']} ({compare_stats['best_season']['division']} - Pos: {compare_stats['best_season']['position']})</span></div>
                    <div style="margin-bottom: 0.5rem;"><strong style="color: #764ba2;">Biggest Win:</strong> <span style="color: #000000;">{compare_stats['highest_win']['score'] if compare_stats['highest_win']['score'] != '0-0' else 'None'}{f" vs {compare_stats['highest_win']['opponent'].title()}" if compare_stats['highest_win']['score'] != '0-0' and compare_stats['highest_win']['opponent'] else ''}</span></div>
                    <div><strong style="color: #764ba2;">Biggest Loss:</strong> <span style="color: #000000;">{compare_stats['highest_defeat']['score'] if compare_stats['highest_defeat']['score'] != '0-0' else 'None'}{f" vs {compare_stats['highest_defeat']['opponent'].title()}" if compare_stats['highest_defeat']['score'] != '0-0' and compare_stats['highest_defeat']['opponent'] else ''}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced Direct Head-to-Head section
        st.markdown("#### 🔥 Direct Head-to-Head")
        matches, w1, d, l1 = get_h2h(all_fixtures, selected_player, compare_player)
        
        if matches:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-container" style="background: linear-gradient(145deg, #28a745 0%, #20c997 100%); color: white;">
                    <div style="font-size: 2rem; font-weight: bold; margin-bottom: 0.5rem;">{w1}</div>
                    <div style="font-size: 1rem; font-weight: 600;">{selected_player.title()} Wins</div>
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
                    <div style="font-size: 1rem; font-weight: 600;">{compare_player.title()} Wins</div>
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
