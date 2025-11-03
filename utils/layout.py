import streamlit as st

def set_page_config():
    st.set_page_config(page_title="H2H", layout="wide", page_icon="⚽")

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
            /* Custom sidebar navigation styling */
            .stSidebar .css-1d391kg {
                background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
            }
            .stSidebar .stSelectbox label {
                display: none !important;
            }
            .css-1cypcdb.eczjsme11 {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                margin: 1rem 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .stSidebar [data-testid="stSidebarNav"] {
                background: transparent;
                padding: 1rem 0;
            }
            .stSidebar {
                background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
                padding: 0;
            }
            .stSidebar [data-testid="stSidebarNav"] ul {
                padding: 1rem 0;
            }
            .stSidebar [data-testid="stSidebarNav"] li {
                margin: 0.5rem 0;
            }
            .stSidebar [data-testid="stSidebarNav"] a {
                color: #ffffff !important;
                background: rgba(255, 255, 255, 0.05);
                padding: 12px 16px;
                border-radius: 8px;
                margin: 4px 8px;
                transition: all 0.3s ease;
                text-decoration: none;
                display: block;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .stSidebar [data-testid="stSidebarNav"] a:hover {
                background: rgba(52, 152, 219, 0.2);
                color: #ffffff !important;
                transform: translateX(5px);
            }
            .stSidebar [data-testid="stSidebarNav"] a[aria-current="page"] {
                background: rgba(52, 152, 219, 0.3);
                color: #ffffff !important;
                border-left: 4px solid #3498db;
            }
            .css-1cypcdb.eczjsme11 a {
                color: #bdc3c7 !important;
                text-decoration: none !important;
                padding: 12px 16px !important;
                border-radius: 8px !important;
                transition: all 0.3s ease !important;
                margin: 4px 0 !important;
                display: block !important;
            }
            .css-1cypcdb.eczjsme11 a:hover {
                background: rgba(52, 152, 219, 0.2) !important;
                color: #3498db !important;
                transform: translateX(5px) !important;
            }
            .css-1cypcdb.eczjsme11 a.active {
                background: rgba(52, 152, 219, 0.3) !important;
                color: #3498db !important;
                border-left: 4px solid #3498db !important;
            }
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
