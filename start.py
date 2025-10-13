#!/usr/bin/env python3
"""
Start file for Robinhood Market Researcher
"""

import sys
import os

def main():
    print("Starting Robinhood Market Researcher...")
    print("Loading application...")
    
    try:
        # Import and run the main application
        from robinhood_ui_enhanced import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error: Could not import the application: {e}")
        print("Make sure all required files are in the same directory")
        print("Required files: robinhood_ui_enhanced.py, robinhood_market_researcher.py")
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()