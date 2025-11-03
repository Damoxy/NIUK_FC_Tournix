from .google_sheets import get_worksheet

def load_assignments():
    sheet = get_worksheet()
    try:
        records = sheet.get_all_records()
        return {row["Player"]: row["Seed"] for row in records}, None
    except KeyError as e:
        return None, f"❌ Google Sheet is missing column: {e}"

def append_assignment(player, seed, timestamp):
    sheet = get_worksheet()
    sheet.append_row([player, seed, timestamp])
