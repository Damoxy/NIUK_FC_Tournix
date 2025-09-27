import streamlit as st

def set_page_config():
    st.set_page_config(page_title="NIUK FC League", layout="wide")

def inject_css():
    st.markdown("""
        <style>
            .stApp { background-color: #ffffff; }
            .card {
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                text-align: center;
                font-size: 18px;
                font-weight: 600;
                color: #333333;
            }
            .card h3 { margin: 0; font-size: 24px; color: #007bff; }
        </style>
    """, unsafe_allow_html=True)

def show_header(title):
    st.markdown(f"<h1 style='text-align:center; color:#000000;'>{title}</h1>", unsafe_allow_html=True)

def render_combined_league_record(tables_filtered, players):
    st.markdown("<h2 style='text-align:center; color:#000000;'>Combined League Record</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    for col, player in zip([col1, col2], players):
        totals = {"MP":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Points":0}
        for season, df in tables_filtered.items():
            if df.empty or "Twitter Handles" not in df.columns: continue
            df.columns = [str(c).strip() for c in df.columns]
            df["Twitter Handles"] = df["Twitter Handles"].astype(str).str.strip()
            row = df[df["Twitter Handles"]==player]
            if not row.empty:
                for k in ["MP","W","D","L","Points"]:
                    if k in row:
                        try: totals[k]+=int(float(str(row[k].values[0]).replace(",","").strip()) or 0)
                        except: totals[k]+=0
                if "GF" in row.columns and "GA" in row.columns:
                    try:
                        totals["GF"]+=int(str(row["GF"].values[0]).replace(",","").strip())
                        totals["GA"]+=int(str(row["GA"].values[0]).replace(",","").strip())
                    except: pass
                elif "+ / -" in row.columns:
                    try:
                        gf, ga = str(row["+ / -"].values[0]).strip().split("/")
                        totals["GF"]+=int(gf.strip())
                        totals["GA"]+=int(ga.strip())
                    except: pass
        totals["GD"] = totals["GF"] - totals["GA"]
        with col:
            st.markdown(f"""
                <div class="card">
                    <h3>{player}</h3>
                    Matches: {totals['MP']}<br>
                    Wins: {totals['W']} | Draws: {totals['D']} | Losses: {totals['L']}<br>
                    GF: {totals['GF']} | GA: {totals['GA']} | GD: {totals['GD']}<br>
                    Points: {totals['Points']}
                </div>
            """, unsafe_allow_html=True)
