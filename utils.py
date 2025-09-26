import re
import pandas as pd

def clean_round_name(text):
    if not text:
        return ""
    match = re.search(r"(ROUND\s*\d+)", text.upper())
    return match.group(1).title() if match else text

def load_fixtures(sheet, season):
    ws = sheet.worksheet("Fixtures")
    data = ws.get_all_values()
    fixtures = []
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
