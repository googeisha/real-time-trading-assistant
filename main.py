"""
Launcher file for the Robinhood Market Researcher Application
This file provides a clean entry point to start the application
"""

def main():
    """
    Launch the Robinhood Market Researcher application
    """
    print("===============================================")
    print("[APP] Starting Robinhood Market Researcher Application...")
    print("This is the main launcher for the enhanced UI")
    print("===============================================")
    print()
    
    try:
        # Import and run the enhanced UI (the most feature-rich version)
        print("[DEBUG] Attempting to import robinhood_ui_enhanced...")
        from robinhood_ui_enhanced import main as enhanced_ui_main
        print("[DEBUG] Successfully imported enhanced UI")
        print("[DEBUG] Starting the application interface...")
        print()
        enhanced_ui_main()
    except ImportError as e:
        print(f"❌ Error importing enhanced UI: {e}")
        print("The application requires the robinhood_ui_enhanced.py file to run.")
        print("Please ensure all required files are present.")
        print()
        print("Required dependencies:")
        print("- tkinter (usually included with Python)")
        print("- pandas")
        print("- numpy")
        print("- matplotlib")
        print("- requests")
        print()
        print("Install with: pip install pandas numpy matplotlib requests")
    except Exception as e:
        print(f"❌ Unexpected error running application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("[LAUNCHER] Application starting via main entry point...")
    main()