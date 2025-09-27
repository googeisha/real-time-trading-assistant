"""
Continuous Market Watcher for the Advanced Trading Assistant
This script will continuously monitor your watchlist and update every few minutes
"""

import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from robinhood_market_researcher import MarketAnalyzer

def continuous_watcher():
    print("🎯 Advanced Trading Assistant - Continuous Market Watcher")
    print("=" * 60)
    print("Monitoring your watchlist for trading opportunities...")
    print("Press Ctrl+C to stop the monitoring\n")
    
    # Initialize the analyzer
    analyzer = MarketAnalyzer()
    
    # Clear any existing watchlist and add your stocks
    import sqlite3
    conn = sqlite3.connect("watchlist.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist")  # Clear existing watchlist
    conn.commit()
    conn.close()
    
    # Add your default watchlist
    default_stocks = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL"]
    
    print(f"Added to watchlist: {', '.join(default_stocks)}")
    for stock in default_stocks:
        analyzer.add_to_watchlist(stock)
    
    print(f"\nStarting continuous monitoring of {len(default_stocks)} stocks...")
    print("The system will update every 5 minutes with fresh analysis\n")
    
    try:
        cycle = 1
        while True:
            print(f"📈 Market Update #{cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
            # Get fresh analysis
            summary = analyzer.get_analysis_summary()
            print(summary)
            
            print(f"\nNext update in 5 minutes... (Press Ctrl+C to stop)\n")
            print("=" * 60)
            
            # Wait 5 minutes before next update
            time.sleep(300)  # 300 seconds = 5 minutes
            cycle += 1
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
        print("Your Advanced Trading Assistant will no longer update.")
        print("Your watchlist and data are preserved in the database.")

def interactive_setup():
    print("🎯 Advanced Trading Assistant - Setup Mode")
    print("=" * 50)
    
    print("Would you like to customize your watchlist?")
    print("1. Use default watchlist (NVDA, TSLA, AAPL, MSFT, AMZN, GOOGL)")
    print("2. Enter your own stocks")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        analyzer = MarketAnalyzer()
        
        # Clear any existing watchlist
        import sqlite3
        conn = sqlite3.connect("watchlist.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlist")
        conn.commit()
        conn.close()
        
        if choice == "2":
            print("\nEnter your stocks separated by commas (e.g., AAPL,MSFT,GOOGL):")
            user_input = input().strip()
            user_stocks = [s.strip().upper() for s in user_input.split(",") if s.strip()]
            
            if user_stocks:
                for stock in user_stocks:
                    analyzer.add_to_watchlist(stock)
                print(f"\nAdded your stocks to watchlist: {', '.join(user_stocks)}")
            else:
                print("No valid stocks entered. Using default watchlist.")
                default_stocks = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL"]
                for stock in default_stocks:
                    analyzer.add_to_watchlist(stock)
        else:
            # Default stocks
            default_stocks = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL"]
            for stock in default_stocks:
                analyzer.add_to_watchlist(stock)
            print(f"\nUsing default watchlist: {', '.join(default_stocks)}")
        
        return True
    except:
        print("Using default settings...")
        return True

if __name__ == "__main__":
    # Run setup first
    interactive_setup()
    
    # Then start continuous monitoring
    continuous_watcher()