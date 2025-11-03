import streamlit as st
import requests
import os

def roast_player_with_openrouter(player_name, player_stats, api_key=None):
    """
    Calls OpenRouter's deepseek/deepseek-chat-v3-0324:free model to roast a player based on their stats.
    Args:
        player_name (str): The player's name (can be a placeholder for anonymity).
        player_stats (str): A string summary of the player's stats.
        api_key (str, optional): OpenRouter API key. If None, will use st.secrets if available, then env var.
    Returns:
        str: The AI-generated roast, or an error message.
    """
    if api_key is None:
        try:
            api_key = st.secrets["openrouter"]["api_key"]
        except Exception:
            api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "[OpenRouter API key not set]"

    # Get prompt from secrets, fallback to default if not set
    try:
        prompt_template = st.secrets["openrouter"]["roast_prompt"]
    except Exception:
        prompt_template = (
            "A group of friends play the FC game on PS5 across different seasons, competing against each other. I need you to create witty, funny roasts for each player based on their in-game stats and performance. The tone should mix Nigerian and UK slang — playful banter, not mean-spirited.\n\nYou can also throw in jokes about:\n- Players relying on 'machineries' (unfair tactics or overpowered teams) to win.\n- Stirring drama or 'wahala' in the WhatsApp group.\n- Rage-quitting or leaving the group mid-season.\n\nKeep the roasts sharp, humorous, and full of football banter.\n\nStats context (do NOT repeat these directly, use them for inspiration only):\n{stats}"
        )
    prompt = prompt_template.format(stats=player_stats)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemma-3-4b-it",
        "messages": [
            {"role": "system", "content": "You are a witty football pundit. Never repeat stats directly. Always roast with banter, using the numbers only as inspiration. Always mention the player's name ('this player') at least once in the roast."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.9
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error contacting OpenRouter: {e}]"
