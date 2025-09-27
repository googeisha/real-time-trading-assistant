"""
Enhanced Robinhood Trading Assistant - Recommended Runner

This is the main entry point for the enhanced Robinhood trading assistant
with dark theme and all features.
"""

def main():
    print(\"Starting Enhanced Robinhood Trading Assistant with Dark Theme...\")
    print(\"Features: Dark theme, organized sections, dual charts, market analysis\")
    print(\"Loading application, please wait...\\n\")
    
    try:
        import subprocess
        subprocess.run([\"python\", \"enhanced_robinhood_trading_assistant.py\"])
    except Exception as e:
        print(f\"An error occurred: {e}\")
        input(\"Press Enter to exit...\")

if __name__ == \"__main__\":
    main()