import streamlit as st
import requests
import os

def roast_player_with_openrouter(player_name, player_stats, api_key=None):
    """
    Calls OpenRouter's deepseek/deepseek-chat-v3-0324:free model to roast a player based on their stats.
    Args:
        player_name (str): The player's name.
        player_stats (str): A string summary of the player's stats.
        api_key (str, optional): OpenRouter API key. If None, will use st.secrets if available, then env var.
    Returns:
        str: The AI-generated roast, or an error message.
    """
    # Try to get API key from Streamlit secrets first
    if api_key is None:
        try:
            api_key = st.secrets["openrouter"]["api_key"]
        except Exception:
            api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[OpenRouter API key not set]"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Roast the following football player in a witty, funny way based on their stats using Naija lingo.\nPlayer: {player_name}\nStats: {player_stats}"
    data = {
        "model": "google/gemma-3-4b-it",
        "messages": [
            {"role": "system", "content": "You are a witty football pundit who roasts players based on their stats using Naija lingo."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.9
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error contacting OpenRouter: {e}]"
