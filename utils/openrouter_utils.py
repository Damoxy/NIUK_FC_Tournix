import streamlit as st
import requests
import os

def fetch_gist_content(gist_url):
    # Convert gist page URL to API URL
    gist_id = gist_url.rstrip('/').split('/')[-1]
    api_url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(api_url)
    response.raise_for_status()
    gist_files = response.json()["files"]
    # Get the first file's content
    file_content = next(iter(gist_files.values()))["content"]
    return file_content


def load_prompts_from_gist():
    gist_url = st.secrets["github"]["gist_url"]
    content = fetch_gist_content(gist_url)
    # Parse markdown for system_message, user_template, ai_settings
    system_message, user_template, ai_settings = [], [], {}
    mode = None
    for line in content.splitlines():
        if line.strip().startswith('## System Message'):
            mode = 'system'
        elif line.strip().startswith('## User Template'):
            mode = 'user'
        elif line.strip().startswith('## AI Settings'):
            mode = 'ai'
        elif line.strip().startswith('```'):
            continue
        elif mode == 'system':
            if line.strip():
                system_message.append(line.rstrip())
        elif mode == 'user':
            if line.strip():
                user_template.append(line.rstrip())
        elif mode == 'ai':
            if ':' in line:
                k, v = line.split(':', 1)
                ai_settings[k.strip('- ').strip()] = v.strip()
    return {
        "system_message": '\n'.join(system_message),
        "user_template": '\n'.join(user_template),
        "ai_settings": ai_settings
    }


def roast_player_with_openrouter(player_name, player_stats, api_key=None):
    """
    Calls OpenRouter's AI model to roast a player based on their stats.
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

    prompts_config = load_prompts_from_gist()
    ai_settings = prompts_config["ai_settings"]
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": ai_settings["model"],
        "messages": [
            {"role": "system", "content": prompts_config["system_message"]},
            {"role": "user", "content": prompts_config["user_template"].format(stats=player_stats)}
        ],
        "max_tokens": int(ai_settings["max_tokens"]),
        "temperature": float(ai_settings["temperature"])
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        roast_content = result["choices"][0]["message"]["content"]
        roast_content = roast_content.replace('@', '')
        return roast_content
    except Exception as e:
        return f"[Error contacting OpenRouter: {e}]"
