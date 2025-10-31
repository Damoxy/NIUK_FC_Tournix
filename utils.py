import re
import pandas as pd
import streamlit as st
import os
import pickle
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Example usage in your app:
# from fun_messages import get_random_loading_message
# with st.spinner(get_random_loading_message()):
#     data = load_fixtures_by_url(...)

def clean_round_name(text):
    if not text:
        return ""
    match = re.search(r"(ROUND\s*\d+)", text.upper())
    return match.group(1).title() if match else text

def display_division_name(division):
    mapping = {
        "Div1_Fixtures": "Division 1",
        "Div2_Fixtures": "Division 2",
        "Cup": "CUP"
    }
    return mapping.get(division, division)

def load_fixtures(sheet, season, divisions=["Div1_Fixtures", "Div2_Fixtures"], cup_sheet="Cup_Fixtures"):
    import time
    all_fixtures = []

    # Helper to safely get worksheet with delay
    def safe_get_worksheet(name):
        try:
            ws = sheet.worksheet(name)
            time.sleep(1)  
            return ws
        except Exception as e:
            print(f"Could not load worksheet '{name}': {e}")
            return None

    # Division Fixtures
    for division in divisions:
        ws = safe_get_worksheet(division)
        if not ws:
            continue
        data = ws.get_all_values()
        current_round = None
        for row in data:
            # Detect round row
            if any("ROUND" in str(cell).upper() for cell in row if cell):
                current_round = clean_round_name(" ".join([c for c in row if c]).strip())
                continue
            # Parse fixture row
            if len(row) >= 9 and row[2] and row[3]:
                home, away = row[2].strip(), row[3].strip()
                try:
                    home_leg1, away_leg1 = int(row[4]), int(row[5])
                except:
                    home_leg1, away_leg1 = None, None
                try:
                    home_leg2, away_leg2 = int(row[7]), int(row[8])
                except:
                    home_leg2, away_leg2 = None, None
                all_fixtures.append({
                    "season": season,
                    "division": division,
                    "round": current_round,
                    "home": home,
                    "away": away,
                    "home_leg1": home_leg1,
                    "away_leg1": away_leg1,
                    "home_leg2": home_leg2,
                    "away_leg2": away_leg2,
                })

    # Cup Fixtures
    ws = safe_get_worksheet(cup_sheet)
    if ws:
        data = ws.get_all_values()
        current_round = None
        for row in data:
            # Detect Cup round header (e.g., "Playoffs", "R of 32", etc.)
            if len([c for c in row if c]) == 1 and not row[2:4]:
                current_round = " ".join([c for c in row if c]).strip()
                continue
            if len(row) >= 9 and row[2] and row[3]:
                home, away = row[2].strip(), row[3].strip()
                try:
                    home_leg1, away_leg1 = int(row[4]), int(row[5])
                except:
                    home_leg1, away_leg1 = None, None
                try:
                    home_leg2, away_leg2 = int(row[7]), int(row[8])
                except:
                    home_leg2, away_leg2 = None, None
                all_fixtures.append({
                    "season": season,
                    "division": "Cup",
                    "round": current_round,
                    "home": home,
                    "away": away,
                    "home_leg1": home_leg1,
                    "away_leg1": away_leg1,
                    "home_leg2": home_leg2,
                    "away_leg2": away_leg2,
                })

    return all_fixtures

def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict,
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

@st.cache_data(show_spinner=False)
def load_fixtures_by_url(sheet_url, season, divisions=["Div1_Fixtures", "Div2_Fixtures"], cup_sheet="Cup_Fixtures"):
    cache_file = os.path.join(CACHE_DIR, f"fixtures_cache_{season}.pkl")
    cache_age = 24 * 3600  # 1 day
    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < cache_age:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
    gc = get_gspread_client()
    sheet = gc.open_by_url(sheet_url)
    all_fixtures = []
    def safe_get_worksheet(name):
        try:
            ws = sheet.worksheet(name)
            time.sleep(5)
            return ws
        except Exception as e:
            print(f"Could not load worksheet '{name}': {e}")
            return None
    for division in divisions:
        ws = safe_get_worksheet(division)
        if not ws:
            continue
        data = ws.get_all_values()
        current_round = None
        for row in data:
            if any("ROUND" in str(cell).upper() for cell in row if cell):
                current_round = clean_round_name(" ".join([c for c in row if c]).strip())
                continue
            if len(row) >= 9 and row[2] and row[3]:
                home, away = row[2].strip(), row[3].strip()
                try:
                    home_leg1, away_leg1 = int(row[4]), int(row[5])
                except:
                    home_leg1, away_leg1 = None, None
                try:
                    home_leg2, away_leg2 = int(row[7]), int(row[8])
                except:
                    home_leg2, away_leg2 = None, None
                all_fixtures.append({
                    "season": season,
                    "division": division,
                    "round": current_round,
                    "home": home,
                    "away": away,
                    "home_leg1": home_leg1,
                    "away_leg1": away_leg1,
                    "home_leg2": home_leg2,
                    "away_leg2": away_leg2,
                })
    ws = safe_get_worksheet(cup_sheet)
    if ws:
        data = ws.get_all_values()
        current_round = None
        for row in data:
            if len([c for c in row if c]) == 1 and not row[2:4]:
                current_round = " ".join([c for c in row if c]).strip()
                continue
            if len(row) >= 9 and row[2] and row[3]:
                home, away = row[2].strip(), row[3].strip()
                try:
                    home_leg1, away_leg1 = int(row[4]), int(row[5])
                except:
                    home_leg1, away_leg1 = None, None
                try:
                    home_leg2, away_leg2 = int(row[7]), int(row[8])
                except:
                    home_leg2, away_leg2 = None, None
                all_fixtures.append({
                    "season": season,
                    "division": "Cup",
                    "round": current_round,
                    "home": home,
                    "away": away,
                    "home_leg1": home_leg1,
                    "away_leg1": away_leg1,
                    "home_leg2": home_leg2,
                    "away_leg2": away_leg2,
                })
    with open(cache_file, "wb") as f:
        pickle.dump(all_fixtures, f)
    return all_fixtures

@st.cache_data(show_spinner=False)
def load_table_by_url(sheet_url, season):
    cache_file = os.path.join(CACHE_DIR, f"table_cache_{season}.csv")
    cache_age = 24 * 3600  # 1 day
    if os.path.exists(cache_file):
        if time.time() - os.path.getmtime(cache_file) < cache_age:
            return pd.read_csv(cache_file)
    gc = get_gspread_client()
    sheet = gc.open_by_url(sheet_url)
    try:
        ws = sheet.worksheet(f"LEAGUE DASHBOARD-{season}")
    except:
        return pd.DataFrame()
    data = ws.get_all_values()
    df = pd.DataFrame(data)
    header_row = None
    for i, row in df.iterrows():
        if "Twitter Handles" in row.values:
            header_row = i
            break
    if header_row is None:
        return pd.DataFrame()
    df.columns = [str(c).strip() for c in df.iloc[header_row]]
    df = df[header_row + 1:]
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.reset_index(drop=True)
    df.to_csv(cache_file, index=False)
    return df

def load_table(sheet, season):
    try:
        ws = sheet.worksheet(f"LEAGUE DASHBOARD-{season}")
    except:
        return pd.DataFrame()

    data = ws.get_all_values()
    df = pd.DataFrame(data)

    header_row = None
    for i, row in df.iterrows():
        if "Twitter Handles" in row.values:
            header_row = i
            break
    if header_row is None:
        return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.iloc[header_row]]
    df = df[header_row + 1:]
    df = df.loc[:, ~df.columns.duplicated()]
    return df.reset_index(drop=True)

def get_h2h(fixtures, p1, p2):
    matches, w, d, l = [], 0, 0, 0
    for f in fixtures:
        if {f["home"], f["away"]} == {p1, p2}:
            for leg_home, leg_away in [(f["home_leg1"], f["away_leg1"]), (f["home_leg2"], f["away_leg2"])]:
                if leg_home is not None and leg_away is not None:
                    matches.append((f["season"], f["round"], f["home"], f["away"], leg_home, leg_away))
                    if leg_home > leg_away and f["home"] == p1: w += 1
                    elif leg_home < leg_away and f["away"] == p1: w += 1
                    elif leg_home == leg_away: d += 1
                    else: l += 1
    return matches, w, d, l