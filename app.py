import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re

# --- CONFIG ---
st.set_page_config(page_title="H2H Football Dashboard", layout="wide")

# --- GOOGLE SHEETS AUTH ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# --- SEASON URLS ---
season_urls = {
    "S3": "https://docs.google.com/spreadsheets/d/1UUaWuyXoAkji_72CEpylPSU39w3Fnwsw1uKYRe9sJcQ/edit?gid=956052616",
    "S4": "https://docs.google.com/spreadsheets/d/1-ulIZ5eNjaxR0-m69xLb8XRmHJu-L2bUB9bLUz9iOP8/edit?gid=956052616",
}


# --- HELPERS ---
def clean_round_name(text):
    if not text:
        return ""
    match = re.search(r"(ROUND\s*\d+)", text.upper())
    return match.group(1).title() if match else text


def load_fixtures(sheet, season):
    """Extract all fixtures from a season"""
    ws = sheet.worksheet("Fixtures")
    data = ws.get_all_values()
    fixtures = []
    current_round = None

    for row in data:
        if any("ROUND" in str(cell).upper() for cell in row if cell):
            current_round = clean_round_name(" ".join([c for c in row if c]).strip())
            continue
        if len(row) >= 9 and row[2] and row[3]:  # player columns
            home, away = row[2].strip(), row[3].strip()
            try:
                home_leg1, away_leg1 = int(row[4]), int(row[5])
            except:
                home_leg1, away_leg1 = None, None
            try:
                home_leg2, away_leg2 = int(row[7]), int(row[8])
            except:
                home_leg2, away_leg2 = None, None

            fixtures.append({
                "season": season,
                "round": current_round,
                "home": home,
                "away": away,
                "home_leg1": home_leg1,
                "away_leg1": away_leg1,
                "home_leg2": home_leg2,
                "away_leg2": away_leg2,
            })
    return fixtures


def load_table(sheet, season):
    """Load the league table for a season"""
    try:
        ws = sheet.worksheet(f"LEAGUE DASHBOARD-{season}")
    except:
        return pd.DataFrame()

    data = ws.get_all_values()
    df = pd.DataFrame(data)

    # Find header row dynamically
    header_row = None
    for i, row in df.iterrows():
        if "Twitter Handles" in row.values:
            header_row = i
            break
    if header_row is None:
        return pd.DataFrame()

    df.columns = df.iloc[header_row]
    df = df[header_row + 1:]
    df = df.loc[:, ~df.columns.duplicated()]  # remove duplicate cols
    return df.reset_index(drop=True)


def get_h2h(fixtures, p1, p2):
    """Extract head-to-head matches and calculate WDL"""
    matches, w, d, l = [], 0, 0, 0

    for f in fixtures:
        if {f["home"], f["away"]} == {p1, p2}:
            # 1st leg
            if f["home_leg1"] is not None and f["away_leg1"] is not None:
                h, a = f["home_leg1"], f["away_leg1"]
                matches.append((f["season"], f["round"], f["home"], f["away"], h, a))
                if h > a and f["home"] == p1: w += 1
                elif h < a and f["away"] == p1: w += 1
                elif h == a: d += 1
                else: l += 1

            # 2nd leg
            if f["home_leg2"] is not None and f["away_leg2"] is not None:
                h, a = f["home_leg2"], f["away_leg2"]
                matches.append((f["season"], f["round"], f["home"], f["away"], h, a))
                if h > a and f["home"] == p1: w += 1
                elif h < a and f["away"] == p1: w += 1
                elif h == a: d += 1
                else: l += 1

    return matches, w, d, l


# --- LOAD ALL DATA ---
all_fixtures, all_tables = [], {}
for season, url in season_urls.items():
    sheet = client.open_by_url(url)
    all_fixtures.extend(load_fixtures(sheet, season))
    all_tables[season] = load_table(sheet, season)

# Collect all unique players
players = sorted(set(f["home"] for f in all_fixtures) | set(f["away"] for f in all_fixtures))


# --- SIDEBAR ---
st.sidebar.title("⚙️ Settings")

# Season slider
max_seasons = len(season_urls)
season_limit = st.sidebar.slider("Include last N seasons", 1, max_seasons, max_seasons)

# Player selectors
player1 = st.sidebar.selectbox("Select Player 1", players, index=0)
player2 = st.sidebar.selectbox("Select Player 2", players, index=1)

# Limit data
selected_seasons = list(season_urls.keys())[-season_limit:]
fixtures_filtered = [f for f in all_fixtures if f["season"] in selected_seasons]
tables_filtered = {s: all_tables[s] for s in selected_seasons}


# --- MAIN CONTENT ---
st.title("⚽ Head-to-Head Football Dashboard")

# --- H2H ---
st.header("🤝 Head-to-Head Results")

matches, w, d, l = get_h2h(fixtures_filtered, player1, player2)

# Dashboard WDL
st.markdown(f"### Overall Record: {player1} vs {player2}")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div style="background:#28a745;padding:20px;border-radius:12px;text-align:center;color:white;font-size:22px;font-weight:bold;">{w}<br>Wins</div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div style="background:#ffc107;padding:20px;border-radius:12px;text-align:center;color:black;font-size:22px;font-weight:bold;">{d}<br>Draws</div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div style="background:#dc3545;padding:20px;border-radius:12px;text-align:center;color:white;font-size:22px;font-weight:bold;">{l}<br>Losses</div>""", unsafe_allow_html=True)

# --- H2H MATCHES COMBINED TILE (ALL IN ONE CARD) ---
if matches:
    match_lines = []
    for season, rnd, home, away, hs, as_ in matches:
        match_lines.append(f"{rnd} - {season}: {home} {hs}-{as_} {away}")
    match_text = "\n".join(match_lines)

    st.markdown(f"""
        <div style="background-color:#2f3b52;padding:20px;border-radius:12px;
        color:white;white-space:pre-line;box-shadow:0px 4px 6px rgba(0,0,0,0.2);">
        <b>Head-to-Head Matches</b>\n
        {match_text}
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("No head-to-head matches found between these players.")




# --- COMBINED LEAGUE RECORD ---
st.header("🏆 Combined League Record")
col1, col2 = st.columns(2)

for col, player in zip([col1, col2], [player1, player2]):
    totals = {"MP": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Points": 0}
    for season, df in tables_filtered.items():
        if df.empty or "Twitter Handles" not in df:
            continue
        df["Twitter Handles"] = df["Twitter Handles"].astype(str).str.strip()
        row = df[df["Twitter Handles"] == player]
        if not row.empty:
            for k in totals.keys():
                if k in row:
                    try:
                        totals[k] += int(row[k].values[0])
                    except:
                        pass
    with col:
        st.markdown(f"""
            <div style="background-color:#000000;padding:20px;border-radius:12px;
            text-align:center;font-size:18px;font-weight:bold;box-shadow:0px 4px 6px rgba(0,0,0,0.1);">
            <span style="font-size:20px;color:#007bff;">{player}</span><br><br>
            Matches: {totals['MP']}<br>
            Wins: {totals['W']} | Draws: {totals['D']} | Losses: {totals['L']}<br>
            GF: {totals['GF']} | GA: {totals['GA']} | GD: {totals['GD']}<br>
            Points: {totals['Points']}
            </div>
        """, unsafe_allow_html=True)
