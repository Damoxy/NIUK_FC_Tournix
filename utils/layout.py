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
            
            /* Style navigation links */
            .stSidebar .stSelectbox label {
                display: none !important;
            }
            
            /* Custom page navigation styling */
            .css-1cypcdb.eczjsme11 {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 12px;
                margin: 1rem 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            /* Hide default navigation visually but keep functionality */
            .stSidebar [data-testid="stSidebarNav"] {
                position: absolute;
                opacity: 0;
                pointer-events: none;
                height: 0;
                overflow: hidden;
            }
            
            .stSidebar {
                background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
                padding: 0;
            }
            
            /* Custom navigation styling */
            .stSidebar [data-testid="stSidebarNav"] ul {
                padding: 1rem 0;
            }
            
            .stSidebar [data-testid="stSidebarNav"] li {
                margin: 0.5rem 0;
            }
            
            .stSidebar [data-testid="stSidebarNav"] a {
                color: #bdc3c7;
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
                color: #3498db;
                transform: translateX(5px);
            }
            
            .stSidebar [data-testid="stSidebarNav"] a[aria-current="page"] {
                background: rgba(52, 152, 219, 0.3);
                color: #3498db;
                border-left: 4px solid #3498db;
            }
            
            /* Replace navigation text with CSS */
            .stSidebar [data-testid="stSidebarNav"] a[href="/"] span {
                visibility: hidden;
                position: relative;
            }
            
            .stSidebar [data-testid="stSidebarNav"] a[href="/"] span::after {
                visibility: visible;
                position: absolute;
                top: 0;
                left: 0;
                content: "H2H";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            
            .stSidebar [data-testid="stSidebarNav"] a[href="/seed_reveal"] span {
                visibility: hidden;
                position: relative;
            }
            
            .stSidebar [data-testid="stSidebarNav"] a[href="/seed_reveal"] span::after {
                visibility: visible;
                position: absolute;
                top: 0;
                left: 0;
                content: "Seed Reveal";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            /* Style active and hover states */
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
        <script>
            // More aggressive navigation customization
            function customizeNavigation() {
                // Try multiple selectors to find navigation links
                const selectors = [
                    '[data-testid="stSidebarNav"] a',
                    '.css-1cypcdb a',
                    '.stSidebar a',
                    'nav a',
                    '.sidebar a'
                ];
                
                let navLinks = [];
                for (let selector of selectors) {
                    const links = document.querySelectorAll(selector);
                    if (links.length > 0) {
                        navLinks = Array.from(links);
                        break;
                    }
                }
                
                console.log('Found navigation links:', navLinks.length);
                
                navLinks.forEach(function(link, index) {
                    const href = link.getAttribute('href') || '';
                    const textElement = link.querySelector('span') || link;
                    const currentText = textElement.textContent.trim().toLowerCase();
                    
                    console.log(`Link ${index}: href="${href}", text="${currentText}"`);
                    
                    // Match main page (app)
                    if (href === '/' || href.includes('app') || currentText === 'app' || index === 0) {
                        textElement.textContent = 'H2H';
                        console.log('Changed to H2H');
                    }
                    // Match seed reveal page
                    else if (href.includes('seed') || currentText.includes('seed') || currentText.includes('reveal')) {
                        textElement.textContent = 'Seed Reveal';
                        console.log('Changed to Seed Reveal');
                    }
                });
            }
            
            // Run multiple times with different delays
            function runCustomization() {
                setTimeout(customizeNavigation, 100);
                setTimeout(customizeNavigation, 500);
                setTimeout(customizeNavigation, 1000);
                setTimeout(customizeNavigation, 2000);
            }
            
            // Enhanced observer
            function setupNavigationObserver() {
                const observer = new MutationObserver(function(mutations) {
                    customizeNavigation();
                });
                
                observer.observe(document.body, {
                    childList: true,
                    subtree: true,
                    attributes: true
                });
            }
            
            // Initial setup with multiple triggers
            runCustomization();
            document.addEventListener('DOMContentLoaded', runCustomization);
            window.addEventListener('load', runCustomization);
            setupNavigationObserver();
            
            // Also run periodically for the first 10 seconds
            let attempts = 0;
            const interval = setInterval(function() {
                customizeNavigation();
                attempts++;
                if (attempts > 20) {  // Stop after 20 attempts (10 seconds)
                    clearInterval(interval);
                }
            }, 500);
        </script>
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
