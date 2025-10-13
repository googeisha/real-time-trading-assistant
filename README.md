# Enhanced Robinhood Trading Assistant

## Project Overview
This project contains an enhanced version of the Robinhood-style trading assistant with improved UI, charts, and dark theme.

## File Structure

### Core Files:
- `robinhood_market_researcher.py` - Contains the MarketAnalyzer class and all trading logic
- `robinhood_ui_dark.py` - **MAIN FILE** - Dark-themed UI with all features (charts, boxes, blue accents)
- `advanced_robinhood_assistant.py` - Advanced version with more features

### Application Launch:
- `main.py` - **RECOMMENDED** - Main entry point (launches the best-working dark UI)
- `start_app.bat` - **RECOMMENDED** - Double-click to launch the application

### Alternative Launch:
- `run_dark_ui.bat` - Direct launch of dark-themed UI

### Database:
- `watchlist.db` - SQLite database storing your watchlist

## How to Run

### Recommended (Best Experience):
Double-click `start_app.bat` or run:
```
python main.py
```

This will launch the dark-themed UI which is the most stable version.

### Alternative:
Double-click `run_dark_ui.bat` or run:
```
python robinhood_ui_dark.py
```

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