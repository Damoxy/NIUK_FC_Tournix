import streamlit as st
from utils.data_utils import get_h2h, display_division_name


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
