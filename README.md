# Enhanced Robinhood Trading Assistant

## Project Overview
This project contains an enhanced version of the Robinhood-style trading assistant with improved UI, charts, and dark theme.

## File Structure

### Core Files:
- `robinhood_market_researcher.py` - Contains the MarketAnalyzer class and all trading logic
- `robinhood_ui_dark.py` - **MAIN FILE** - Dark-themed UI with all features (charts, boxes, blue accents)
- `robinhood_ui.py` - Basic UI (original version)
- `robinhood_ui_visual.py` - UI with visual enhancements
- `robinhood_ui_final.py` - UI with all features but light theme
- `advanced_robinhood_assistant.py` - Advanced version with more features
- `robinhood_assistant_single.py` - Original assistant (has known issues)

### Database:
- `watchlist.db` - SQLite database storing your watchlist

### Run Scripts:
- `run_dark_ui.bat` - **RECOMMENDED** - Run this for the best experience (dark theme with all features)

## How to Run

### Recommended (Best Experience):
Double-click `run_dark_ui.bat` or run:
```
python robinhood_ui_dark.py
```

### Other Options:
- For regular UI with all features: `python robinhood_ui_final.py`
- For basic functionality: `python robinhood_ui.py`

## Features

### Dark-Themed UI (`robinhood_ui_dark.py`):
- Sleek black and blue color scheme
- Organized sections with boxes
- Dual charts (price and volume/RSI)
- Color-coded market signals
- Real-time analysis
- Watchlist management

## Troubleshooting

If you encounter the error about `root.destroy()`, make sure you're running the correct file:
- Use `robinhood_ui_dark.py` (not `robinhood_assistant_single.py`)
- The dark-themed UI does not have the problematic closing method

This version has fixed all deprecated warnings and provides the best user experience.