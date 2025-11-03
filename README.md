# H2H FC Tournix - Football Head-to-Head Analysis App

A Streamlit multipage application for analyzing football fixtures and league tables, with an integrated seed reveal system for knockout cup draws and a fun AI-powered roast feature.

## Project Structure

```
H2H_FC/
├── H2H.py                 # Main Streamlit app (league analysis, roasting, welcome)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml      # Streamlit secrets (credentials, config, roast prompt)
├── cache/                # Session-local cache files
│   ├── fixtures_cache_*.pkl
│   └── table_cache_*.csv
├── pages/
│   └── seed_reveal.py    # Seed reveal page for cup draws
└── utils/                # All utility modules
    ├── __init__.py
    ├── auth.py           # Google Sheets authentication
    ├── config.py         # App configuration
    ├── data_utils.py     # Data loading and processing
    ├── google_sheets.py  # Google Sheets integration
    ├── h2h.py            # Head-to-head results rendering
    ├── layout.py         # UI layout and styling components
    ├── openrouter_utils.py # OpenRouter AI roast integration
    ├── players.py        # Player data and codes
    ├── seeds.py          # Seed management
    └── sheet.py          # Sheet operations
```

## Features

### Main App (League Analysis & Roasting)
- Load fixtures and league tables from multiple seasons
- Case-insensitive player name handling to avoid duplicates
- Session-local caching for faster performance
- Head-to-head statistics and match history
- Combined league records across seasons
- **AI-powered Roast a Player:**
  - Select any player and generate a witty, banter-filled roast using OpenRouter AI
  - Player names are never sent to the AI model—only stats are used, and the feature is purely for fun

### Seed Reveal Page
- Interactive seed selection for knockout cup draws
- Player authentication system
- Real-time Google Sheets integration
- Randomized seed layout

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your Google Sheets credentials and OpenRouter API key in `secrets.toml`

3. Run the app:
   ```bash
   streamlit run H2H.py
   ```

## Configuration

All configuration is managed through `.streamlit/secrets.toml`:
- Season URLs for Google Sheets
- Google Cloud service account credentials
- Player lists and access codes
- External links
- OpenRouter API key and roast prompt

## Caching

The app uses two levels of caching:
- **Streamlit caching**: Built-in function caching with `@st.cache_data`
- **File caching**: Session-local pickle/CSV files in the `cache/` directory

## Development Notes

- All utilities are consolidated in the `utils/` package
- Imports use absolute paths from project root
- Player names are normalized to lowercase for consistency
- Cache files are temporary and cleared on app restart
- The roast feature is for entertainment only—no player names are sent to the AI model
