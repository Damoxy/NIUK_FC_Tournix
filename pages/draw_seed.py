# pages/draw_seed.py
import streamlit as st
from datetime import datetime

from utils.player import all_players, player_codes, link_url
from utils.seed import get_shuffled_seeds
from utils.sheet import load_assignments, append_assignment

# --- 1. Player and Code Setup ---
if "shuffled_seeds" not in st.session_state:
    st.session_state.shuffled_seeds = get_shuffled_seeds()

# --- 2. Load from Google Sheet ---
assignments, error = load_assignments()
if error:
    st.error(error)
    st.stop()

taken_seeds = set(assignments.values())
available_players = [p for p in all_players if p not in assignments]

# --- 3. Title ---
st.title("🏆 S4 Knockout Cup Draws")

# --- 4. Current Seed Status with Locked icons ---
st.subheader("Current Seed Status")

cols = st.columns(8)
for idx, seed in enumerate(st.session_state.shuffled_seeds):
    col = cols[idx % 8]
    with col:
        if seed in taken_seeds:
            st.button(seed, key=f"readonly_{seed}", disabled=True)
        else:
            st.button("🔒", key=f"locked_{seed}", disabled=True)

# --- 5. Authentication ---
st.subheader("🔐 Enter to Choose Your Tile")

selected_player = st.selectbox("👤 Select your name:", [""] + available_players)
access_code = st.text_input("🔑 Enter your access code:", type="password")

if st.button("✅ Submit"):
    if not selected_player:
        st.warning("Please select your name.")
    elif access_code != player_codes.get(selected_player):
        st.warning("❌ Incorrect access code.")
    elif selected_player in assignments:
        st.success(
            f"You have been seeded to **{assignments[selected_player]}**, "
            f"you can view the draws [here]({link_url})."
        )
    else:
        st.session_state.verified_player = selected_player
        st.rerun()

# --- 6. Tile selection after verification ---
if "verified_player" in st.session_state:
    player = st.session_state.verified_player

    if player in assignments:
        st.success(
            f"You have been seeded to **{assignments[player]}**, "
            f"you can view the draws [here]({link_url})."
        )
    else:
        st.success(f"Welcome {player}! Please select your seed:")
        cols = st.columns(8)

        for idx, seed in enumerate(st.session_state.shuffled_seeds):
            col = cols[idx % 8]
            with col:
                if seed in taken_seeds:
                    st.button(seed, key=f"select_disabled_{seed}", disabled=True)
                else:
                    if st.button("🔒", key=f"{player}_{seed}"):
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        append_assignment(player, seed, timestamp)
                        st.success(f"🎯 You have been seeded to **{seed}**!")
                        st.rerun()
