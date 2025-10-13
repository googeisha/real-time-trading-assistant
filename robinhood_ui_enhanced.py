"""
Enhanced Robinhood Market Researcher - Dark UI
A comprehensive tool for analyzing stocks with improved functionality and AI insights
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import robinhood_market_researcher  # Import our analysis functions
import matplotlib.dates as mdates
import threading
import time


class RobinhoodDarkUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robinhood Market Researcher - Enhanced Dark Mode")
        self.root.geometry("1400x900")
        
        # Set dark theme
        self.root.configure(bg="#1e1e1e")
        
        # Store current symbol and data
        self.current_symbol = "SPY"
        self.current_data = None
        self.current_analysis = None
        
        # Initialize AI settings
        self.auto_update_ai = True  # Default to True for auto-update AI insights
        
        # Create header
        header_frame = tk.Frame(self.root, bg="#1e1e1e", height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🪙 Robinhood Market Researcher", 
                              font=("Arial", 16, "bold"), fg="#64b5f6", bg="#1e1e1e")
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Stock symbol input
        input_frame = tk.Frame(main_frame, bg="#1e1e1e")
        input_frame.pack(fill=tk.X, pady=5)
        
        symbol_label = tk.Label(input_frame, text="Stock Symbol:", 
                               font=("Arial", 11), fg="#e0e0e0", bg="#1e1e1e")
        symbol_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.symbol_entry = tk.Entry(input_frame, font=("Arial", 11), 
                                    bg="#2d2d2d", fg="#e0e0e0", insertbackground="#e0e0e0", 
                                    relief=tk.FLAT, highlightthickness=1, 
                                    highlightcolor="#64b5f6")
        self.symbol_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.symbol_entry.insert(0, "SPY")  # Default value
        self.symbol_entry.bind("<Return>", lambda event: self.analyze_stock())  # Bind Enter key to analyze
        
        analyze_btn = tk.Button(input_frame, text="🔍 Analyze", command=self.analyze_stock,
                               bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                               relief=tk.FLAT, padx=15)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add real-time button
        self.real_time_btn = tk.Button(input_frame, text="▶ Start Real-Time", command=self.toggle_real_time,
                                      bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                                      relief=tk.FLAT, padx=15)
        self.real_time_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Add a search/completion button
        search_btn = tk.Button(input_frame, text="🔍 Search", command=self.search_ticker,
                               bg="#2196F3", fg="white", font=("Arial", 10),
                               relief=tk.FLAT, padx=10)
        search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Watchlist buttons
        add_to_watchlist_btn = tk.Button(input_frame, text="⭐ Add to Watchlist", 
                                        command=self.add_to_watchlist,
                                        bg="#FF9800", fg="white", font=("Arial", 10),
                                        relief=tk.FLAT, padx=10)
        add_to_watchlist_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        view_watchlist_btn = tk.Button(input_frame, text="📊 View Watchlist", 
                                      command=self.load_watchlist,
                                      bg="#2196F3", fg="white", font=("Arial", 10),
                                      relief=tk.FLAT, padx=10)
        view_watchlist_btn.pack(side=tk.LEFT)
        
        # Auto-refresh button
        self.auto_refresh_btn = tk.Button(input_frame, text="🔄 Live Updates", 
                                         command=self.toggle_auto_refresh,
                                         bg="#607D8B", fg="white", font=("Arial", 10),
                                         relief=tk.FLAT, padx=10)
        self.auto_refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Add the search tickers function after the existing functions
        
        # Create notebook for tabs
        try:
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        except Exception as e:
            print(f"Error creating notebook: {e}")
            messagebox.showerror("Critical Error", f"Failed to create UI components: {str(e)}")
            raise
        
        # Details tab
        self.details_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.details_frame, text="📊 Details")
        
        # Details text area
        self.details_text = scrolledtext.ScrolledText(self.details_frame, 
                                                     bg="#2d2d2d", fg="#e0e0e0",
                                                     font=("Consolas", 10),
                                                     relief=tk.FLAT,
                                                     insertbackground="#e0e0e0")
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure tags for color coding
        self.details_text.tag_configure("green", foreground="#4caf50", font=("Arial", 10))
        self.details_text.tag_configure("red", foreground="#f44336", font=("Arial", 10))
        self.details_text.tag_configure("normal", font=("Arial", 10), foreground="#e0e0e0")
        self.details_text.tag_configure("section", font=("Arial", 11, "bold"), foreground="#64b5f6")  # Light blue
        self.details_text.tag_configure("green_bold", foreground="#4caf50", font=("Arial", 11, "bold"))
        self.details_text.tag_configure("red_bold", foreground="#f44336", font=("Arial", 11, "bold"))
        self.details_text.tag_configure("normal_bold", font=("Arial", 11, "bold"), foreground="#e0e0e0")
        
        # Chart tab with enhanced functionality
        self.chart_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.chart_frame, text="📈 Enhanced Chart")
        
        # Create a frame for chart controls
        chart_control_frame = tk.Frame(self.chart_frame, bg="#1e1e1e")
        chart_control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Chart type selection
        tk.Label(chart_control_frame, text="Chart Type:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.chart_type_var = tk.StringVar(value="line")
        chart_type_combo = ttk.Combobox(chart_control_frame, textvariable=self.chart_type_var,
                                       values=["line", "candle", "area", "volume"], state="readonly", width=10)
        chart_type_combo.pack(side=tk.LEFT, padx=(5, 10))
        chart_type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_chart())
        
        # Timeframe selection
        tk.Label(chart_control_frame, text="Timeframe:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.timeframe_var = tk.StringVar(value="3M")
        timeframe_combo = ttk.Combobox(chart_control_frame, textvariable=self.timeframe_var,
                                      values=["1W", "1M", "3M", "6M", "1Y", "2Y", "5Y"], state="readonly", width=8)
        timeframe_combo.pack(side=tk.LEFT, padx=(5, 10))
        timeframe_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_chart())
        
        # Indicator toggles
        self.show_sma20_var = tk.BooleanVar(value=True)
        self.show_sma50_var = tk.BooleanVar(value=True)
        self.show_bollinger_var = tk.BooleanVar(value=True)
        self.show_volume_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(chart_control_frame, text="SMA20", variable=self.show_sma20_var,
                      fg="#e0e0e0", bg="#1e1e1e", selectcolor="#2d2d2d",
                      command=self.refresh_chart).pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Checkbutton(chart_control_frame, text="SMA50", variable=self.show_sma50_var,
                      fg="#e0e0e0", bg="#1e1e1e", selectcolor="#2d2d2d",
                      command=self.refresh_chart).pack(side=tk.LEFT, padx=(5, 5))
        
        tk.Checkbutton(chart_control_frame, text="Bollinger", variable=self.show_bollinger_var,
                      fg="#e0e0e0", bg="#1e1e1e", selectcolor="#2d2d2d",
                      command=self.refresh_chart).pack(side=tk.LEFT, padx=(5, 5))
        
        tk.Checkbutton(chart_control_frame, text="Volume", variable=self.show_volume_var,
                      fg="#e0e0e0", bg="#1e1e1e", selectcolor="#2d2d2d",
                      command=self.refresh_chart).pack(side=tk.LEFT, padx=(5, 5))
        
        # Create matplotlib figure for enhanced charts
        self.fig = Figure(figsize=(12, 7), facecolor='#1e1e1e')
        self.fig.patch.set_facecolor('#1e1e1e')
        
        # Create subplots
        self.ax1 = self.fig.add_subplot(2, 1, 1)  # Price chart
        self.ax2 = self.fig.add_subplot(2, 1, 2, sharex=self.ax1)  # Volume chart
        
        # Chart canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add refresh chart button
        chart_btn_frame = tk.Frame(self.chart_frame, bg="#1e1e1e")
        chart_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_chart_btn = tk.Button(chart_btn_frame, text="🔄 Refresh Chart", 
                                     command=self.refresh_chart,
                                     bg="#2196F3", fg="white", font=("Arial", 10),
                                     relief=tk.FLAT, padx=10)
        refresh_chart_btn.pack(side=tk.LEFT)
        
        # Percentage change checker
        percent_frame = tk.Frame(chart_btn_frame, bg="#1e1e1e")
        percent_frame.pack(side=tk.RIGHT)
        
        tk.Label(percent_frame, text="Calculate Change:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.start_price_entry = tk.Entry(percent_frame, font=("Arial", 10), 
                                         bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.start_price_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.start_price_entry.insert(0, "Start Price")
        
        tk.Label(percent_frame, text="→", font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT, padx=(5, 0))
        
        self.end_price_entry = tk.Entry(percent_frame, font=("Arial", 10), 
                                       bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.end_price_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.end_price_entry.insert(0, "End Price")
        
        calc_btn = tk.Button(percent_frame, text="Calculate %", command=self.calculate_percentage_change,
                            bg="#FF9800", fg="white", font=("Arial", 10),
                            relief=tk.FLAT, padx=5)
        calc_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        self.percent_result_label = tk.Label(percent_frame, text="", 
                                           font=("Arial", 10, "bold"), bg="#1e1e1e")
        self.percent_result_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Options tab
        self.options_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.options_frame, text="📊 Options")
        
        # Options content
        options_content_frame = tk.Frame(self.options_frame, bg="#1e1e1e")
        options_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Options controls
        options_control_frame = tk.Frame(options_content_frame, bg="#1e1e1e")
        options_control_frame.pack(fill=tk.X, pady=5)
        
        # Expiration selector
        tk.Label(options_control_frame, text="Expiration Date:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        # Create a combobox for expiration dates
        self.expiration_var = tk.StringVar()
        self.expiration_combo = ttk.Combobox(options_control_frame, textvariable=self.expiration_var,
                                           state="readonly", width=12, font=("Arial", 10))
        self.expiration_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.expiration_combo.set("Select date")
        
        # Auto-refresh options when stock is analyzed
        refresh_options_btn = tk.Button(options_control_frame, text="Refresh Options", 
                                       command=self.refresh_options_data,
                                       bg="#9C27B0", fg="white", font=("Arial", 10),
                                       relief=tk.FLAT, padx=10)
        refresh_options_btn.pack(side=tk.LEFT)
        
        # Options display area
        self.options_text = scrolledtext.ScrolledText(options_content_frame, 
                                                     bg="#2d2d2d", fg="#e0e0e0",
                                                     font=("Consolas", 9),
                                                     relief=tk.FLAT,
                                                     insertbackground="#e0e0e0")
        self.options_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for options display
        self.options_text.tag_configure("strike", font=("Arial", 10, "bold"), foreground="#FFD54F")
        self.options_text.tag_configure("call", font=("Arial", 10), foreground="#81C784")
        self.options_text.tag_configure("put", font=("Arial", 10), foreground="#E57373")
        self.options_text.tag_configure("header", font=("Arial", 10, "bold"), foreground="#64B5F6")
        self.options_text.tag_configure("highlight", background="#3d3d3d")
        self.options_text.tag_configure("info", font=("Arial", 10), foreground="#A1887F")
        
        # Initialize with instructions
        self.options_text.config(state=tk.NORMAL)
        self.options_text.delete(1.0, tk.END)
        self.options_text.insert(tk.END, "Options Data\n", ("header",))
        self.options_text.insert(tk.END, "="*50 + "\n\n")
        self.options_text.insert(tk.END, "Options data will load automatically when you analyze a stock.\n")
        self.options_text.insert(tk.END, "Make sure you've analyzed a stock first.\n")
        self.options_text.config(state=tk.DISABLED)
        
    def refresh_options_data(self):
        """Refresh options data for the current symbol"""
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol first")
            return
        
        # Get expiration date from combobox if one is selected
        expiration = self.expiration_var.get()
        if expiration == "Select date":
            expiration = None
        
        try:
            # Get options data
            options_data = robinhood_market_researcher.get_options_data(symbol, expiration)
            
            # Update the expiration dates combobox
            if 'expiration_dates' in options_data and options_data['expiration_dates']:
                self.expiration_combo['values'] = options_data['expiration_dates']
                # If no specific expiration was selected, select the first one
                if not expiration and options_data['expiration_dates']:
                    self.expiration_var.set(options_data['expiration_dates'][0])
            
            # Display the options data
            self.display_options_data(symbol, options_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching options data: {str(e)}")
            print(f"Error in refresh_options_data: {e}")

    def display_options_data(self, symbol, options_data):
        """Display options data in the options text area"""
        try:
            self.options_text.config(state=tk.NORMAL)
            self.options_text.delete(1.0, tk.END)
            
            if 'error' in options_data and options_data['error']:
                self.options_text.insert(tk.END, f"Options Data for {symbol}\n", ("header",))
                self.options_text.insert(tk.END, "="*50 + "\n\n")
                self.options_text.insert(tk.END, f"Error: {options_data['error']}\n", ("info",))
                self.options_text.config(state=tk.DISABLED)
                return
            
            # Header information
            self.options_text.insert(tk.END, f"Options Data for {symbol}\n", ("header",))
            self.options_text.insert(tk.END, "="*50 + "\n")
            if 'current_price' in options_data and options_data['current_price']:
                self.options_text.insert(tk.END, f"Current Stock Price: ${options_data['current_price']:.2f}\n", ("info",))
            if 'selected_expiration' in options_data and options_data['selected_expiration']:
                self.options_text.insert(tk.END, f"Expiration Date: {options_data['selected_expiration']}\n", ("info",))
            self.options_text.insert(tk.END, f"Total Calls: {len(options_data.get('calls', []))}\n", ("info",))
            self.options_text.insert(tk.END, f"Total Puts: {len(options_data.get('puts', []))}\n\n", ("info",))
            
            # Display calls
            if options_data.get('calls'):
                self.options_text.insert(tk.END, "CALLS:\n", ("header",))
                header = f"{'Strike':<8} {'Last':<8} {'Bid':<8} {'Ask':<8} {'Vol':<8} {'OI':<10} {'IV':<8} {'Delta':<8}\n"
                self.options_text.insert(tk.END, header, ("header",))
                self.options_text.insert(tk.END, "-"*80 + "\n")
                
                for call in options_data['calls']:
                    self.options_text.insert(tk.END, f"{call.get('strike', 0):<8.2f} ")
                    self.options_text.insert(tk.END, f"{call.get('last', 0):<8.2f} ", ("call",))
                    self.options_text.insert(tk.END, f"{call.get('bid', 0):<8.2f} ", ("call",))
                    self.options_text.insert(tk.END, f"{call.get('ask', 0):<8.2f} ", ("call",))
                    self.options_text.insert(tk.END, f"{call.get('volume', 0):<8} ", ("call",))
                    self.options_text.insert(tk.END, f"{call.get('open_interest', 0):<10} ", ("call",))
                    self.options_text.insert(tk.END, f"{call.get('iv', 0)*100:<7.2f}% ", ("call",))
                    self.options_text.insert(tk.END, f"{call.get('delta', 0):<8.3f} ", ("call",))
                    self.options_text.insert(tk.END, "\n")
            else:
                self.options_text.insert(tk.END, "CALLS: No call options available\n\n", ("info",))
            
            # Add some space between calls and puts
            self.options_text.insert(tk.END, "\n")
            
            # Display puts
            if options_data.get('puts'):
                self.options_text.insert(tk.END, "PUTS:\n", ("header",))
                header = f"{'Strike':<8} {'Last':<8} {'Bid':<8} {'Ask':<8} {'Vol':<8} {'OI':<10} {'IV':<8} {'Delta':<8}\n"
                self.options_text.insert(tk.END, header, ("header",))
                self.options_text.insert(tk.END, "-"*80 + "\n")
                
                for put in options_data['puts']:
                    self.options_text.insert(tk.END, f"{put.get('strike', 0):<8.2f} ")
                    self.options_text.insert(tk.END, f"{put.get('last', 0):<8.2f} ", ("put",))
                    self.options_text.insert(tk.END, f"{put.get('bid', 0):<8.2f} ", ("put",))
                    self.options_text.insert(tk.END, f"{put.get('ask', 0):<8.2f} ", ("put",))
                    self.options_text.insert(tk.END, f"{put.get('volume', 0):<8} ", ("put",))
                    self.options_text.insert(tk.END, f"{put.get('open_interest', 0):<10} ", ("put",))
                    self.options_text.insert(tk.END, f"{put.get('iv', 0)*100:<7.2f}% ", ("put",))
                    self.options_text.insert(tk.END, f"{put.get('delta', 0):<8.3f} ", ("put",))
                    self.options_text.insert(tk.END, "\n")
            else:
                self.options_text.insert(tk.END, "PUTS: No put options available\n", ("info",))
            
            self.options_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.options_text.config(state=tk.NORMAL)
            self.options_text.delete(1.0, tk.END)
            self.options_text.insert(tk.END, f"Error displaying options data: {str(e)}", ("info",))
            self.options_text.config(state=tk.DISABLED)
            print(f"Error in display_options_data: {e}")
        
        # Enhanced AI Insights tab
        self.ai_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.ai_frame, text="🤖 Enhanced AI Insights")
        
        # AI Insights content
        ai_content_frame = tk.Frame(self.ai_frame, bg="#1e1e1e")
        ai_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # AI Controls
        ai_control_frame = tk.Frame(ai_content_frame, bg="#1e1e1e")
        ai_control_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ai_control_frame, text="AI Analysis:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        analyze_ai_btn = tk.Button(ai_control_frame, text="Run Enhanced AI Analysis", 
                                  command=self.run_enhanced_ai_analysis,
                                  bg="#FF9800", fg="white", font=("Arial", 10),
                                  relief=tk.FLAT, padx=10)
        analyze_ai_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Add a button to auto-update AI insights when analyzing a stock
        auto_ai_btn = tk.Button(ai_control_frame, text="Auto-Update AI Insights", 
                               command=self.toggle_auto_ai,
                               bg="#4CAF50", fg="white", font=("Arial", 10),
                               relief=tk.FLAT, padx=10)
        auto_ai_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # AI Insights display area
        self.ai_text = scrolledtext.ScrolledText(ai_content_frame, 
                                                bg="#2d2d2d", fg="#e0e0e0",
                                                font=("Consolas", 10),
                                                relief=tk.FLAT,
                                                insertbackground="#e0e0e0")
        self.ai_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for AI insights
        self.ai_text.tag_configure("ai_header", font=("Arial", 12, "bold"), foreground="#FFD54F")
        self.ai_text.tag_configure("ai_recommendation", font=("Arial", 11, "bold"), foreground="#81C784")
        self.ai_text.tag_configure("ai_warning", font=("Arial", 10, "bold"), foreground="#E57373")
        self.ai_text.tag_configure("ai_neutral", font=("Arial", 10), foreground="#64B5F6")
        self.ai_text.tag_configure("ai_signal", font=("Arial", 10, "bold"), foreground="#FFB74D")
        self.ai_text.tag_configure("ai_buy", font=("Arial", 10, "bold"), foreground="#AED581")
        self.ai_text.tag_configure("ai_sell", font=("Arial", 10, "bold"), foreground="#FF8A65")
        self.ai_text.tag_configure("ai_strong", font=("Arial", 10, "bold"), foreground="#FFF176")
        
        # Investment/Paper Trading tab
        self.investment_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.investment_frame, text="💰 Advanced Paper Trading")
        
        # Investment/Paper Trading content
        investment_content_frame = tk.Frame(self.investment_frame, bg="#1e1e1e")
        investment_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main Controls Frame
        main_control_frame = tk.Frame(investment_content_frame, bg="#1e1e1e")
        main_control_frame.pack(fill=tk.X, pady=5)
        
        # Primary Trading Controls
        primary_control_frame = tk.Frame(main_control_frame, bg="#1e1e1e")
        primary_control_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        tk.Label(primary_control_frame, text="Account Balance ($):", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.account_balance_entry = tk.Entry(primary_control_frame, font=("Arial", 10), 
                                            bg="#2d2d2d", fg="#e0e0e0", width=12)
        self.account_balance_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.account_balance_entry.insert(0, "100000.00")
        
        tk.Label(primary_control_frame, text="Shares:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.shares_entry = tk.Entry(primary_control_frame, font=("Arial", 10), 
                                   bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.shares_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.shares_entry.insert(0, "0")
        
        tk.Label(primary_control_frame, text="Entry Price ($):", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.entry_price_entry = tk.Entry(primary_control_frame, font=("Arial", 10), 
                                        bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.entry_price_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.entry_price_entry.insert(0, "0.00")
        
        # Advanced Order Controls
        order_control_frame = tk.Frame(main_control_frame, bg="#1e1e1e")
        order_control_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        tk.Label(order_control_frame, text="Stop Loss ($):", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.stop_loss_entry = tk.Entry(order_control_frame, font=("Arial", 10), 
                                       bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.stop_loss_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.stop_loss_entry.insert(0, "0.00")
        
        tk.Label(order_control_frame, text="Take Profit ($):", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.take_profit_entry = tk.Entry(order_control_frame, font=("Arial", 10), 
                                         bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.take_profit_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.take_profit_entry.insert(0, "0.00")
        
        tk.Label(order_control_frame, text="Risk %:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.risk_percent_entry = tk.Entry(order_control_frame, font=("Arial", 10), 
                                          bg="#2d2d2d", fg="#e0e0e0", width=6)
        self.risk_percent_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.risk_percent_entry.insert(0, "2.0")
        
        # Investment action buttons
        action_btn_frame = tk.Frame(main_control_frame, bg="#1e1e1e")
        action_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        btn_row_frame = tk.Frame(action_btn_frame, bg="#1e1e1e")
        btn_row_frame.pack()
        
        buy_btn = tk.Button(btn_row_frame, text="📈 Buy", 
                           command=lambda: self.execute_paper_trade("BUY"),
                           bg="#4CAF50", fg="white", font=("Arial", 10),
                           relief=tk.FLAT, padx=10)
        buy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        sell_btn = tk.Button(btn_row_frame, text="📉 Sell", 
                            command=lambda: self.execute_paper_trade("SELL"),
                            bg="#f44336", fg="white", font=("Arial", 10),
                            relief=tk.FLAT, padx=10)
        sell_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear position button
        clear_btn = tk.Button(btn_row_frame, text="🔄 Clear", 
                             command=self.clear_paper_position,
                             bg="#FF9800", fg="white", font=("Arial", 10),
                             relief=tk.FLAT, padx=10)
        clear_btn.pack(side=tk.LEFT, padx=(5, 5))
        
        # Auto-order button
        auto_order_btn = tk.Button(btn_row_frame, text="🤖 Auto Orders", 
                                  command=self.setup_auto_orders,
                                  bg="#9C27B0", fg="white", font=("Arial", 10),
                                  relief=tk.FLAT, padx=10)
        auto_order_btn.pack(side=tk.LEFT, padx=(5, 5))
        
        # Portfolio Summary button
        portfolio_btn = tk.Button(btn_row_frame, text="📊 Portfolio", 
                                 command=self.show_portfolio_summary,
                                 bg="#2196F3", fg="white", font=("Arial", 10),
                                 relief=tk.FLAT, padx=10)
        portfolio_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Paper trading display area
        self.investment_text = scrolledtext.ScrolledText(investment_content_frame, 
                                                        bg="#2d2d2d", fg="#e0e0e0",
                                                        font=("Consolas", 10),
                                                        relief=tk.FLAT,
                                                        insertbackground="#e0e0e0")
        self.investment_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for investment display
        self.investment_text.tag_configure("invest_header", font=("Arial", 12, "bold"), foreground="#FFD54F")
        self.investment_text.tag_configure("invest_profit", font=("Arial", 10), foreground="#81C784")
        self.investment_text.tag_configure("invest_loss", font=("Arial", 10), foreground="#E57373")
        self.investment_text.tag_configure("invest_info", font=("Arial", 10), foreground="#64B5F6")
        self.investment_text.tag_configure("invest_highlight", font=("Arial", 10, "bold"), foreground="#FFB74D")
        self.investment_text.tag_configure("invest_warning", font=("Arial", 10, "bold"), foreground="#FF8A65")
        self.investment_text.tag_configure("invest_success", font=("Arial", 10, "bold"), foreground="#AED581")
        
        # Initialize with instructions
        self.investment_text.config(state=tk.NORMAL)
        self.investment_text.delete(1.0, tk.END)
        self.investment_text.insert(tk.END, "💼 ADVANCED PAPER TRADING SIMULATOR\n", ("invest_header",))
        self.investment_text.insert(tk.END, "="*50 + "\n\n")
        self.investment_text.insert(tk.END, "• Enter account balance, number of shares, and entry price\n")
        self.investment_text.insert(tk.END, "• Set stop-loss and take-profit levels for risk management\n")
        self.investment_text.insert(tk.END, "• Use Auto Orders to set conditional orders\n")
        self.investment_text.insert(tk.END, "• Click 'Portfolio' to view your holdings summary\n\n")
        self.investment_text.insert(tk.END, "Account Balance: $100,000.00\n")
        self.investment_text.insert(tk.END, "Portfolio Value: $100,000.00\n")
        self.investment_text.insert(tk.END, "Positions: None\n")
        self.investment_text.insert(tk.END, "Total P&L: $0.00\n")
        self.investment_text.config(state=tk.DISABLED)
        
        # Initialize advanced paper trading data
        self.paper_positions = {}  # Store all positions
        self.auto_orders = {}  # Store auto orders
        self.portfolio_history = []  # Track portfolio history
        
        # Add backtest strategy variable
        self.backtest_strategy_var = tk.StringVar(value="All Strategies")

    def run_backtest(self):
        """Run backtest for the selected strategy"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol first")
                return
            
            strategy_selection = self.backtest_strategy_var.get()
            
            # Get the analyzer
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            
            # Run backtest
            if strategy_selection == "All Strategies":
                results = analyzer.backtest_all_strategies(symbol)
            else:
                results = analyzer.backtest_strategy(symbol, strategy_selection)
            
            # Display results in the investment text area
            self.investment_text.config(state=tk.NORMAL)
            self.investment_text.insert(tk.END, f"\n🧪 BACKTEST RESULTS FOR {symbol}\n", ("invest_backtest",))
            self.investment_text.insert(tk.END, "="*50 + "\n")
            
            if 'error' in results:
                self.investment_text.insert(tk.END, f"❌ Error: {results['error']}\n", ("invest_warning",))
            else:
                if strategy_selection == "All Strategies":
                    # Display comparison of all strategies
                    for strategy_name, result in results.items():
                        if 'error' in result:
                            self.investment_text.insert(tk.END, f"❌ {strategy_name}: {result['error']}\n", ("invest_warning",))
                        else:
                            metrics = result.get('metrics', {})
                            self.investment_text.insert(tk.END, f"📊 {strategy_name}:\n", ("invest_backtest",))
                            self.investment_text.insert(tk.END, f"   • Total Return: {metrics.get('total_return', 0)*100:.2f}%\n")
                            self.investment_text.insert(tk.END, f"   • Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}\n")
                            self.investment_text.insert(tk.END, f"   • Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%\n")
                            self.investment_text.insert(tk.END, f"   • Total Trades: {metrics.get('total_trades', 0)}\n\n")
                else:
                    # Display results for single strategy
                    metrics = results.get('metrics', {})
                    self.investment_text.insert(tk.END, f"📊 {strategy_selection} Results:\n", ("invest_backtest",))
                    self.investment_text.insert(tk.END, f"   • Total Return: {metrics.get('total_return', 0)*100:.2f}%\n")
                    self.investment_text.insert(tk.END, f"   • Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}\n")
                    self.investment_text.insert(tk.END, f"   • Max Drawdown: {metrics.get('max_drawdown', 0)*100:.2f}%\n")
                    self.investment_text.insert(tk.END, f"   • Total Trades: {metrics.get('total_trades', 0)}\n")
            
            self.investment_text.config(state=tk.DISABLED)
            self.investment_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error running backtest: {str(e)}")
            print(f"Error in run_backtest: {e}")
            import traceback
            traceback.print_exc()

    def toggle_real_time(self):
        """Toggle real-time market data updates"""
        try:
            # Check current button text to determine action
            current_text = self.real_time_btn.cget("text")
            
            if "Start" in current_text:
                # Start real-time updates
                self.start_real_time_updates()
            else:
                # Stop real-time updates
                self.stop_real_time_updates()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error toggling real-time updates: {str(e)}")
            print(f"Error in toggle_real_time: {e}")

    def start_real_time_updates(self):
        """Start real-time market data updates"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol first")
                return
            
            # Subscribe to real-time updates
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            success = analyzer.subscribe_to_real_time_updates(symbol, self.handle_real_time_update)
            
            if success:
                print(f"Subscribed to real-time updates for {symbol}")
                # Update UI to show real-time mode is active
                self.real_time_btn.config(text="⏹ Stop Real-Time", bg="#f44336")
            else:
                messagebox.showerror("Error", f"Failed to subscribe to real-time updates for {symbol}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error starting real-time updates: {str(e)}")
            print(f"Error in start_real_time_updates: {e}")

    def stop_real_time_updates(self):
        """Stop real-time market data updates"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                return
            
            # Unsubscribe from real-time updates
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            analyzer.unsubscribe_from_real_time_updates(symbol)
            
            print(f"Unsubscribed from real-time updates for {symbol}")
            # Update UI to show real-time mode is inactive
            self.real_time_btn.config(text="▶ Start Real-Time", bg="#4CAF50")
            
        except Exception as e:
            print(f"Error in stop_real_time_updates: {e}")

    def handle_real_time_update(self, data: dict):
        """Handle incoming real-time data updates"""
        try:
            # Update the current data display
            self.root.after(0, self.update_real_time_display, data)
        except Exception as e:
            print(f"Error handling real-time update: {e}")

    def update_real_time_display(self, data: dict):
        """Update the UI with real-time data"""
        try:
            symbol = data.get('symbol', 'N/A')
            price = data.get('price', 0)
            bid = data.get('bid', 0)
            ask = data.get('ask', 0)
            change = data.get('change', 0)
            change_pct = data.get('change_percent', 0)
            volume = data.get('volume', 0)
            
            # Update the main symbol entry if it matches
            current_symbol = self.symbol_entry.get().strip().upper()
            if current_symbol == symbol:
                # Update the price display in real-time
                if hasattr(self, 'price_label'):
                    # Update price label with real-time data
                    color = "#4CAF50" if change >= 0 else "#f44336"
                    self.price_label.config(text=f"${price:.2f} ({change:+.2f} {change_pct:+.2f}%)", fg=color)
            
            # Update any other relevant displays that show real-time data
            # For example, update watchlist or portfolio displays if they are visible
            
        except Exception as e:
            print(f"Error updating real-time display: {e}")
        
        # Interactive Assistant tab
        self.assistant_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.assistant_frame, text="💬 Trading Assistant")
        
        # Assistant content
        assistant_content_frame = tk.Frame(self.assistant_frame, bg="#1e1e1e")
        assistant_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Assistant controls
        assistant_control_frame = tk.Frame(assistant_content_frame, bg="#1e1e1e")
        assistant_control_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(assistant_control_frame, text="Ask the Trading Assistant:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.assistant_question_entry = tk.Entry(assistant_control_frame, font=("Arial", 10), 
                                               bg="#2d2d2d", fg="#e0e0e0", width=50)
        self.assistant_question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.assistant_question_entry.bind("<Return>", lambda e: self.get_assistant_response())
        
        assistant_btn = tk.Button(assistant_control_frame, text="Ask", 
                                 command=self.get_assistant_response,
                                 bg="#9C27B0", fg="white", font=("Arial", 10),
                                 relief=tk.FLAT, padx=10)
        assistant_btn.pack(side=tk.LEFT)
        
        # Assistant response display area
        self.assistant_text = scrolledtext.ScrolledText(assistant_content_frame, 
                                                       bg="#2d2d2d", fg="#e0e0e0",
                                                       font=("Consolas", 10),
                                                       relief=tk.FLAT,
                                                       insertbackground="#e0e0e0")
        self.assistant_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for assistant responses
        self.assistant_text.tag_configure("assistant_header", font=("Arial", 12, "bold"), foreground="#FFD54F")
        self.assistant_text.tag_configure("assistant_response", font=("Arial", 10), foreground="#64B5F6")
        self.assistant_text.tag_configure("assistant_action", font=("Arial", 10, "bold"), foreground="#81C784")
        self.assistant_text.tag_configure("assistant_caution", font=("Arial", 10, "bold"), foreground="#E57373")
        self.assistant_text.tag_configure("assistant_highlight", font=("Arial", 10, "bold"), foreground="#FFB74D")
        
        # Initialize with assistant welcome message
        self.assistant_text.config(state=tk.NORMAL)
        self.assistant_text.delete(1.0, tk.END)
        self.assistant_text.insert(tk.END, "🤖 Trading Assistant\n", ("assistant_header",))
        self.assistant_text.insert(tk.END, "="*30 + "\n\n")
        self.assistant_text.insert(tk.END, "Hello! I'm your trading assistant.\n\n", ("assistant_response",))
        self.assistant_text.insert(tk.END, "You can ask me questions like:\n", ("assistant_response",))
        self.assistant_text.insert(tk.END, "• Should I buy/sell [stock symbol]?\n", ("assistant_action",))
        self.assistant_text.insert(tk.END, "• What's the outlook for [stock symbol]?\n", ("assistant_action",))
        self.assistant_text.insert(tk.END, "• Should I add to my position in [stock symbol]?\n", ("assistant_action",))
        self.assistant_text.insert(tk.END, "• What's my best next move?\n", ("assistant_action",))
        self.assistant_text.insert(tk.END, "\nI'll analyze technical indicators and provide actionable recommendations.\n", ("assistant_response",))
        self.assistant_text.config(state=tk.DISABLED)
        
    def execute_paper_trade(self, action):
        """Execute a paper trade simulation"""
        try:
            # Get current stock price
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol first")
                return
            
            # Get current price from analysis
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            current_data = analyzer.watchlist.get_stock_data(symbol)
            
            if current_data is None or current_data.empty:
                messagebox.showerror("Error", f"Could not get current price for {symbol}")
                return
            
            current_price = current_data['Close'][-1]  # Latest closing price
            
            # Get user inputs
            try:
                account_balance = float(self.account_balance_entry.get())
                shares = int(self.shares_entry.get())
                entry_price = float(self.entry_price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
                return
            
            # Calculate P&L and update position
            if action == "BUY":
                # Validate purchase
                total_cost = shares * current_price
                if total_cost > account_balance:
                    messagebox.showerror("Error", f"Insufficient funds. Need ${total_cost:.2f}, have ${account_balance:.2f}")
                    return
                
                # Update entry price in field to current price (for newly bought shares)
                self.entry_price_entry.delete(0, tk.END)
                self.entry_price_entry.insert(0, f"{current_price:.2f}")
                
                # Update display
                self.investment_text.config(state=tk.NORMAL)
                # Keep the existing content and append new trade
                current_content = self.investment_text.get(1.0, tk.END)
                if "ADVANCED PAPER TRADING SIMULATOR" not in current_content or "Enter account balance" in current_content:
                    # If it's the initial content, replace it
                    self.investment_text.delete(1.0, tk.END)
                    self.investment_text.insert(tk.END, f"💼 ADVANCED PAPER TRADING - {symbol}\n", ("invest_header",))
                    self.investment_text.insert(tk.END, "="*50 + "\n\n")
                
                # Add the new trade
                self.investment_text.insert(tk.END, f"✅ TRADE EXECUTED: {action} {shares} shares of {symbol}\n", ("invest_success",))
                self.investment_text.insert(tk.END, f"Entry Price: ${current_price:.2f}\n")
                self.investment_text.insert(tk.END, f"Total Cost: ${total_cost:.2f}\n")
                self.investment_text.insert(tk.END, f"Remaining Balance: ${account_balance - total_cost:.2f}\n\n")
                
                # Calculate and show potential P&L
                self.investment_text.insert(tk.END, "📊 POSITION SUMMARY:\n", ("invest_header",))
                self.investment_text.insert(tk.END, f"Shares: {shares}\n")
                self.investment_text.insert(tk.END, f"Entry Price: ${current_price:.2f}\n")
                self.investment_text.insert(tk.END, f"Current Price: ${current_price:.2f}\n")
                
                # Add stop loss and take profit info if set
                try:
                    stop_loss = float(self.stop_loss_entry.get()) if self.stop_loss_entry.get() != "0.00" else None
                    take_profit = float(self.take_profit_entry.get()) if self.take_profit_entry.get() != "0.00" else None
                    
                    if stop_loss:
                        self.investment_text.insert(tk.END, f"Stop Loss: ${stop_loss:.2f}\n")
                        risk_percent = ((current_price - stop_loss) / current_price) * 100
                        self.investment_text.insert(tk.END, f"Risk per Share: {risk_percent:.2f}%\n", ("invest_loss",))
                    
                    if take_profit:
                        self.investment_text.insert(tk.END, f"Take Profit: ${take_profit:.2f}\n")
                        profit_percent = ((take_profit - current_price) / current_price) * 100
                        self.investment_text.insert(tk.END, f"Potential Profit per Share: {profit_percent:.2f}%\n", ("invest_profit",))
                except:
                    pass  # Ignore if stop loss/take profit fields are invalid
                
                # Calculate current P&L
                unrealized_pnl = (current_price - current_price) * shares  # Will be 0 for new position
                self.investment_text.insert(tk.END, f"Unrealized P&L: $0.00 (0.00%)\n", ("invest_info",))
                
                self.investment_text.config(state=tk.DISABLED)
                
            elif action == "SELL":
                # Calculate profit/loss
                total_value = shares * current_price
                total_cost = shares * entry_price
                realized_pnl = total_value - total_cost
                total_return_pct = ((current_price - entry_price) / entry_price) * 100
                
                # Update display
                self.investment_text.config(state=tk.NORMAL)
                # Keep existing content and append new trade
                current_content = self.investment_text.get(1.0, tk.END)
                if "ADVANCED PAPER TRADING SIMULATOR" not in current_content or "Enter account balance" in current_content:
                    # If it's the initial content, replace it
                    self.investment_text.delete(1.0, tk.END)
                    self.investment_text.insert(tk.END, f"💼 ADVANCED PAPER TRADING - {symbol}\n", ("invest_header",))
                    self.investment_text.insert(tk.END, "="*50 + "\n\n")
                
                # Add the new trade
                self.investment_text.insert(tk.END, f"✅ TRADE EXECUTED: {action} {shares} shares of {symbol}\n", ("invest_success",))
                self.investment_text.insert(tk.END, f"Sell Price: ${current_price:.2f}\n")
                self.investment_text.insert(tk.END, f"Entry Price: ${entry_price:.2f}\n")
                self.investment_text.insert(tk.END, f"Total Proceeds: ${total_value:.2f}\n")
                
                # Calculate and show profit/loss
                self.investment_text.insert(tk.END, "\n📊 TRADE SUMMARY:\n", ("invest_header",))
                if realized_pnl >= 0:
                    self.investment_text.insert(tk.END, f"Realized P&L: +${abs(realized_pnl):.2f}\n", ("invest_profit",))
                    self.investment_text.insert(tk.END, f"Total Return: +{abs(total_return_pct):.2f}%\n", ("invest_profit",))
                else:
                    self.investment_text.insert(tk.END, f"Realized P&L: -${abs(realized_pnl):.2f}\n", ("invest_loss",))
                    self.investment_text.insert(tk.END, f"Total Return: {total_return_pct:.2f}%\n", ("invest_loss",))
                
                self.investment_text.insert(tk.END, f"Initial Investment: ${total_cost:.2f}\n")
                self.investment_text.insert(tk.END, f"Final Value: ${total_value:.2f}\n")
                
                # Update account balance
                new_balance = account_balance + realized_pnl
                self.account_balance_entry.delete(0, tk.END)
                self.account_balance_entry.insert(0, f"{new_balance:.2f}")
                
                # Clear position
                self.shares_entry.delete(0, tk.END)
                self.shares_entry.insert(0, "0")
                self.entry_price_entry.delete(0, tk.END)
                self.entry_price_entry.insert(0, "0.00")
                
                # Note that stop loss and take profit orders are not cleared - user may want to keep them
                self.investment_text.insert(tk.END, f"\n💰 New Account Balance: ${new_balance:.2f}\n")
                
                self.investment_text.config(state=tk.DISABLED)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error executing paper trade: {str(e)}")
            print(f"Error in execute_paper_trade: {e}")
    
    def clear_paper_position(self):
        """Clear the current paper trading position"""
        # Reset fields
        self.shares_entry.delete(0, tk.END)
        self.shares_entry.insert(0, "0")
        self.entry_price_entry.delete(0, tk.END)
        self.entry_price_entry.insert(0, "0.00")
        
        # Update display
        symbol = self.symbol_entry.get().strip().upper()
        self.investment_text.config(state=tk.NORMAL)
        self.investment_text.delete(1.0, tk.END)
        self.investment_text.insert(tk.END, f"💼 Paper Trading Simulator - {symbol}\n", ("invest_header",))
        self.investment_text.insert(tk.END, "="*50 + "\n\n")
        self.investment_text.insert(tk.END, "Position cleared successfully.\n\n")
        self.investment_text.insert(tk.END, "Enter account balance, number of shares, and entry price.\n")
        self.investment_text.insert(tk.END, "Click 'Buy' to enter a long position or 'Sell' to close it.\n")
        self.investment_text.insert(tk.END, "Current stock price will be fetched automatically.\n")
        self.investment_text.config(state=tk.DISABLED)
        
        # Don't preload any default symbol - start blank
        # Initialize with empty content
        print("DEBUG: Starting with empty fields - no default preload")  # Debug print
        
        # Set up empty text areas initially
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Enter a stock symbol and click 'Analyze' to get started.")
        self.details_text.config(state=tk.DISABLED)
        
        # Check if ai_text was properly created and initialize it
        if hasattr(self, 'ai_text'):
            self.ai_text.config(state=tk.NORMAL)
            self.ai_text.delete(1.0, tk.END)
            self.ai_text.insert(tk.END, "Enter a stock symbol and click 'Analyze' to see AI insights.")
            self.ai_text.config(state=tk.DISABLED)
        else:
            print("WARNING: ai_text was not created during initialization")
        
        # Don't load chart initially - wait for user to enter a symbol
        # Load empty chart with instructions
        self.refresh_chart_empty()
        
        # Optionally set the default tab to AI Insights to make it more prominent
        try:
            # Find and select the AI Insights tab (index of 3 based on order of addition)
            # Details(0), Chart(1), Options(2), AI Insights(3), Investment(4), Assistant(5)
            self.notebook.select(3)  # Select AI Insights tab by index
        except Exception:
            # If there's an issue selecting the specific tab, continue with default
            pass
        
        # Setup auto-refresh functionality
        self.setup_auto_refresh()
        
    def setup_auto_orders(self):
        """Setup automatic stop-loss and take-profit orders"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol first")
                return
                
            # Get values from entry fields
            try:
                current_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() != "0.00" else 0
                stop_loss = float(self.stop_loss_entry.get()) if self.stop_loss_entry.get() != "0.00" else 0
                take_profit = float(self.take_profit_entry.get()) if self.take_profit_entry.get() != "0.00" else 0
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for prices")
                return
            
            # Validate the orders make sense
            if stop_loss != 0 and take_profit != 0:
                if current_price != 0:
                    if current_price > stop_loss and current_price < take_profit:
                        # Valid long position orders
                        self.auto_orders[symbol] = {
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'position_type': 'long',
                            'entry_price': current_price
                        }
                        messagebox.showinfo("Auto Orders", f"Auto orders set for {symbol}:\nStop Loss: ${stop_loss}\nTake Profit: ${take_profit}")
                    elif current_price < stop_loss and current_price > take_profit:
                        # Valid short position orders
                        self.auto_orders[symbol] = {
                            'stop_loss': stop_loss,
                            'take_profit': take_profit,
                            'position_type': 'short',
                            'entry_price': current_price
                        }
                        messagebox.showinfo("Auto Orders", f"Auto orders set for {symbol}:\nStop Loss: ${stop_loss}\nTake Profit: ${take_profit}")
                    else:
                        messagebox.showwarning("Auto Orders", "Stop loss and take profit levels don't make sense for your position.\nFor long positions: Stop Loss < Entry Price < Take Profit")
                        return
                else:
                    messagebox.showwarning("Auto Orders", "Please execute a trade first to set entry price automatically")
                    return
            else:
                messagebox.showwarning("Auto Orders", "Please set both stop loss and take profit values")
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Error setting up auto orders: {str(e)}")
    
    def monitor_auto_orders(self):
        """Monitor positions and execute auto orders when triggered"""
        try:
            for symbol, orders in self.auto_orders.items():
                # Get current price for the symbol
                analyzer = robinhood_market_researcher.MarketAnalyzer()
                current_data = analyzer.watchlist.get_stock_data(symbol)
                
                if current_data is not None and not current_data.empty:
                    current_price = current_data['Close'][-1]  # Latest closing price
                    
                    # Check if stop loss or take profit has been triggered
                    if orders['position_type'] == 'long':
                        if current_price <= orders['stop_loss'] or current_price >= orders['take_profit']:
                            # Execute sell order
                            self.execute_auto_trade(symbol, "SELL", current_price, orders)
                    elif orders['position_type'] == 'short':
                        if current_price >= orders['stop_loss'] or current_price <= orders['take_profit']:
                            # Execute buy-to-cover order
                            self.execute_auto_trade(symbol, "BUY", current_price, orders)
        except Exception as e:
            print(f"Error monitoring auto orders: {e}")
    
    def execute_auto_trade(self, symbol, action, current_price, orders):
        """Execute an auto trade when triggered"""
        try:
            # Remove the order since it's triggered
            del self.auto_orders[symbol]
            
            # Log the execution
            trigger_price = orders['stop_loss'] if ((orders['position_type'] == 'long' and current_price <= orders['stop_loss']) or 
                                                     (orders['position_type'] == 'short' and current_price >= orders['stop_loss'])) else orders['take_profit']
            order_type = "STOP LOSS" if trigger_price == orders['stop_loss'] else "TAKE PROFIT"
            
            # Update the trading interface with the execution
            self.investment_text.config(state=tk.NORMAL)
            self.investment_text.insert(tk.END, f"\n🚨 AUTO {order_type} TRIGGERED for {symbol}\n", ("invest_warning",))
            self.investment_text.insert(tk.END, f"Action: {action} at ${current_price:.2f}\n", ("invest_highlight",))
            self.investment_text.insert(tk.END, f"Original Entry: ${orders['entry_price']:.2f}\n", ("invest_info",))
            self.investment_text.config(state=tk.DISABLED)
            
            # Execute the actual trade (selling the held position)
            # For now, we'll just log it. In a real implementation, this would close the position
            print(f"Auto trade executed: {action} {symbol} at ${current_price}")
            
        except Exception as e:
            print(f"Error executing auto trade: {e}")
    
    def show_portfolio_summary(self):
        """Show enhanced portfolio summary with comprehensive risk management"""
        portfolio_window = tk.Toplevel(self.root)
        portfolio_window.title("Portfolio Summary")
        portfolio_window.geometry("700x500")
        portfolio_window.configure(bg="#1e1e1e")
        
        # Add title
        title = tk.Label(portfolio_window, text="📊 Portfolio Summary", 
                        font=("Arial", 14, "bold"), fg="#64b5f6", bg="#1e1e1e")
        title.pack(pady=10)
        
        # Create a frame for the portfolio
        portfolio_frame = tk.Frame(portfolio_window, bg="#1e1e1e")
        portfolio_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget to display portfolio
        portfolio_text = scrolledtext.ScrolledText(portfolio_frame, 
                                                 bg="#2d2d2d", fg="#e0e0e0",
                                                 font=("Consolas", 10),
                                                 relief=tk.FLAT,
                                                 insertbackground="#e0e0e0")
        portfolio_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags
        portfolio_text.tag_configure("header", font=("Arial", 12, "bold"), foreground="#FFD54F")
        portfolio_text.tag_configure("profit", font=("Arial", 10), foreground="#81C784")
        portfolio_text.tag_configure("loss", font=("Arial", 10), foreground="#E57373")
        portfolio_text.tag_configure("info", font=("Arial", 10), foreground="#64B5F6")
        portfolio_text.tag_configure("highlight", font=("Arial", 10, "bold"), foreground="#FFB74D")
        
        # Calculate and display portfolio summary
        portfolio_text.insert(tk.END, "📈 PORTFOLIO SUMMARY\n", ("header",))
        portfolio_text.insert(tk.END, "="*60 + "\n\n")
        
        try:
            total_value = float(self.account_balance_entry.get()) if self.account_balance_entry.get() else 100000.00
            total_unrealized_pnl = 0
            
            # Check if we have current positions
            current_symbol = self.symbol_entry.get().strip().upper()
            current_shares = int(self.shares_entry.get()) if self.shares_entry.get().isdigit() else 0
            entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
            
            if current_symbol and current_shares > 0:
                # Get current price
                analyzer = robinhood_market_researcher.MarketAnalyzer()
                current_data = analyzer.watchlist.get_stock_data(current_symbol)
                
                if current_data is not None and not current_data.empty:
                    current_price = current_data['Close'][-1]
                    current_value = current_shares * current_price
                    entry_value = current_shares * entry_price if entry_price else current_value
                    pnl = current_value - entry_value
                    
                    total_value += current_value  # Add position value to total
                    total_unrealized_pnl += pnl
                    
                    portfolio_text.insert(tk.END, f"SYMBOL: {current_symbol}\n", ("highlight",))
                    portfolio_text.insert(tk.END, f"  Shares: {current_shares}\n", ("info",))
                    portfolio_text.insert(tk.END, f"  Entry Price: ${entry_price:.2f}\n", ("info",))
                    portfolio_text.insert(tk.END, f"  Current Price: ${current_price:.2f}\n", ("info",))
                    portfolio_text.insert(tk.END, f"  Current Value: ${current_value:.2f}\n", ("info",))
                    pnl_tag = "profit" if pnl >= 0 else "loss"
                    portfolio_text.insert(tk.END, f"  Unrealized P&L: ${pnl:.2f}", (pnl_tag,))
                    portfolio_text.insert(tk.END, f" ({((current_price-entry_price)/entry_price)*100:.2f}%)\n\n", (pnl_tag,))
            
            # Show auto orders if any
            if self.auto_orders:
                portfolio_text.insert(tk.END, "🎯 ACTIVE AUTO ORDERS:\n", ("highlight",))
                for symbol, order in self.auto_orders.items():
                    portfolio_text.insert(tk.END, f"  {symbol}: ", ("info",))
                    portfolio_text.insert(tk.END, f"SL: ${order['stop_loss']:.2f}, ", ("loss",))
                    portfolio_text.insert(tk.END, f"TP: ${order['take_profit']:.2f}\n", ("profit",))
                portfolio_text.insert(tk.END, "\n")
            
            # Show summary
            portfolio_text.insert(tk.END, "💰 SUMMARY:\n", ("highlight",))
            portfolio_text.insert(tk.END, f"  Account Balance: ${float(self.account_balance_entry.get()):.2f}\n", ("info",))
            portfolio_text.insert(tk.END, f"  Total Positions Value: ${total_value - float(self.account_balance_entry.get()):.2f}\n", ("info",))
            portfolio_text.insert(tk.END, f"  Total Portfolio Value: ${total_value:.2f}\n", ("info",))
            
            pnl_tag = "profit" if total_unrealized_pnl >= 0 else "loss"
            portfolio_text.insert(tk.END, f"  Total Unrealized P&L: ${total_unrealized_pnl:.2f}", (pnl_tag,))
            if (float(self.account_balance_entry.get()) + total_unrealized_pnl) != 0:
                portfolio_text.insert(tk.END, f" ({(total_unrealized_pnl/float(self.account_balance_entry.get()))*100:.2f}%)\n", (pnl_tag,))
            else:
                portfolio_text.insert(tk.END, "\n", (pnl_tag,))
            
        except Exception as e:
            portfolio_text.insert(tk.END, f"Error calculating portfolio: {str(e)}\n", ("loss",))
        
        portfolio_text.config(state=tk.DISABLED)
    
    def calculate_position_size(self):
        """Calculate optimal position size based on risk parameters"""
        try:
            # Get risk parameters
            try:
                account_balance = float(self.account_balance_entry.get()) if self.account_balance_entry.get() else 100000.00
                risk_pct = float(self.risk_percent_entry.get()) / 100 if self.risk_percent_entry.get() else 0.02  # 2% default
                entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
                stop_loss = float(self.stop_loss_entry.get()) if self.stop_loss_entry.get() and self.stop_loss_entry.get() != "0.00" else 0
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
                return
            
            if entry_price == 0 or stop_loss == 0:
                messagebox.showwarning("Position Sizing", "Please enter entry price and stop loss to calculate position size")
                return
            
            # Calculate risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            # Calculate position size based on risk
            max_risk_amount = account_balance * risk_pct
            position_size = int(max_risk_amount / risk_per_share) if risk_per_share != 0 else 0
            
            # Update shares field with calculated value
            self.shares_entry.delete(0, tk.END)
            self.shares_entry.insert(0, str(position_size))
            
            # Update display
            self.investment_text.config(state=tk.NORMAL)
            self.investment_text.insert(tk.END, f"\n💡 Position Sizing Suggestion:\n", ("invest_highlight",))
            self.investment_text.insert(tk.END, f"Risk Amount: ${max_risk_amount:.2f} ({risk_pct*100:.2f}% of account)\n", ("invest_info",))
            self.investment_text.insert(tk.END, f"Risk Per Share: ${risk_per_share:.2f}\n", ("invest_info",))
            self.investment_text.insert(tk.END, f"Suggested Position Size: {position_size} shares\n\n", ("invest_success",))
            self.investment_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating position size: {str(e)}")

    def toggle_auto_ai(self):
        """Toggle auto-update AI insights"""
        # Ensure the attribute exists, if not initialize it
        if not hasattr(self, 'auto_update_ai'):
            self.auto_update_ai = True  # Default to True as per initialization
        self.auto_update_ai = not self.auto_update_ai
        status = "ON" if self.auto_update_ai else "OFF"
        messagebox.showinfo("Auto AI Update", f"Auto-update AI Insights is now {status}")

    def setup_auto_refresh(self):
        """Setup enhanced auto-refresh functionality for live updates with configurable intervals"""
        # Initialize auto-refresh settings
        self.auto_refresh_enabled = False
        self.refresh_interval = 30000  # 30 seconds in milliseconds (more frequent updates)
        self.auto_refresh_job = None
        self.last_refresh_time = None
        self.refresh_count = 0
        self.refresh_failures = 0
        self.max_consecutive_failures = 5  # Stop after 5 consecutive failures
        
        # Add to settings frame or create controls for auto-refresh
        # We'll add a button or setting to toggle auto-refresh
        
        # Add refresh interval configuration
        self.min_refresh_interval = 5000   # 5 seconds minimum
        self.max_refresh_interval = 300000 # 5 minutes maximum
        self.default_refresh_interval = 30000 # 30 seconds default
        
    def update_refresh_interval(self, new_interval_ms):
        """Update the refresh interval with validation"""
        if self.min_refresh_interval <= new_interval_ms <= self.max_refresh_interval:
            self.refresh_interval = new_interval_ms
            print(f"Refresh interval updated to {new_interval_ms/1000:.1f} seconds")
            return True
        else:
            print(f"Invalid refresh interval: {new_interval_ms}ms. Must be between {self.min_refresh_interval/1000:.1f}s and {self.max_refresh_interval/1000:.1f}s")
            return False

    def toggle_auto_refresh(self):
        """Toggle auto-refresh for live price updates"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        status = "ENABLED" if self.auto_refresh_enabled else "DISABLED"
        
        if self.auto_refresh_enabled:
            # Start the auto-refresh cycle
            self.start_auto_refresh()
            messagebox.showinfo("Auto Refresh", f"Live updates {status}. Refreshing every {self.refresh_interval/1000:.0f} seconds.")
        else:
            # Stop the auto-refresh cycle
            self.stop_auto_refresh()
            messagebox.showinfo("Auto Refresh", f"Live updates {status}.")

    def start_auto_refresh(self):
        """Start the auto-refresh cycle"""
        if self.auto_refresh_enabled and self.symbol_entry.get().strip():
            self.perform_auto_refresh()
    
    def stop_auto_refresh(self):
        """Stop the auto-refresh cycle"""
        if self.auto_refresh_job:
            self.root.after_cancel(self.auto_refresh_job)
            self.auto_refresh_job = None

    def perform_auto_refresh(self):
        """Perform a single refresh cycle with enhanced error handling and schedule the next one"""
        if not self.auto_refresh_enabled:
            return
            
        # Track refresh timing
        from datetime import datetime
        current_time = datetime.now()
        self.last_refresh_time = current_time
        self.refresh_count += 1
        
        symbol = self.symbol_entry.get().strip().upper()
        if symbol:
            # Only update if symbol is valid
            refresh_successful = False
            try:
                # Perform analysis update (non-blocking)
                self.update_live_data(symbol)
                # Monitor auto orders (stop losses, take profits)
                self.monitor_auto_orders()
                refresh_successful = True
                
                # Log successful refresh
                if self.refresh_count % 10 == 0:  # Log every 10th refresh
                    print(f"AUTO-REFRESH: Cycle {self.refresh_count} completed successfully for {symbol}")
                    
            except Exception as e:
                error_msg = f"Error in auto refresh cycle {self.refresh_count} for {symbol}: {e}"
                print(error_msg)
                self.refresh_failures += 1
                
                # Handle consecutive failures
                if self.refresh_failures >= self.max_consecutive_failures:
                    print(f"CRITICAL: {self.max_consecutive_failures} consecutive auto-refresh failures. Disabling auto-refresh.")
                    self.auto_refresh_enabled = False
                    self.refresh_failures = 0  # Reset counter
                    # Notify user
                    try:
                        messagebox.showerror("Auto-Refresh Disabled", 
                                            f"Auto-refresh has been disabled due to {self.max_consecutive_failures} consecutive failures.\n\n"
                                            f"Last error: {str(e)}\n\n"
                                            f"Please check your connection and restart auto-refresh manually.")
                    except:
                        pass
                    return
                else:
                    # Log failure but continue
                    print(f"Auto-refresh failure {self.refresh_failures}/{self.max_consecutive_failures}")
                    
            finally:
                # Reset failure counter on success
                if refresh_successful:
                    self.refresh_failures = 0
        
        # Adaptive refresh interval based on market hours
        try:
            # Simple market hours detection (9:30 AM - 4:00 PM EST)
            hour = current_time.hour
            minute = current_time.minute
            # Convert to EST if needed (simplified)
            est_hour = hour  # Assuming local time is EST for simplicity
            
            # During market hours, use shorter intervals
            if 9 <= est_hour <= 16:
                # Regular market hours - normal refresh rate
                effective_interval = self.refresh_interval
            elif 8 <= est_hour < 9 or 16 < est_hour <= 17:
                # Pre-market or after-hours - slower refresh rate
                effective_interval = min(self.refresh_interval * 2, self.max_refresh_interval)
            else:
                # Overnight - much slower refresh rate
                effective_interval = self.max_refresh_interval
                
            # Apply adaptive interval
            actual_interval = effective_interval
        except:
            # Fallback to default interval
            actual_interval = self.refresh_interval
        
        # Schedule the next refresh
        if self.auto_refresh_enabled:
            self.auto_refresh_job = self.root.after(actual_interval, self.perform_auto_refresh)
        else:
            print("AUTO-REFRESH: Stopped as auto_refresh_enabled is False")

    def update_live_data(self, symbol):
        """Update live data with enhanced real-time feeds and better error handling"""
        try:
            # Get current data with enhanced error handling
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            
            # Try to get data from multiple sources for redundancy
            stock_data = None
            fallback_attempts = 0
            
            # Primary data source
            try:
                stock_data = analyzer.watchlist.get_stock_data(symbol)
            except Exception as primary_error:
                print(f"Primary data source failed for {symbol}: {primary_error}")
                fallback_attempts += 1
                
            # Fallback data sources if primary fails
            if stock_data is None or stock_data.empty:
                try:
                    # Try direct API call as fallback
                    from robinhood_market_researcher import MarketDataAPI
                    api = MarketDataAPI()
                    stock_data = api.get_stock_data(symbol)
                    if stock_data is not None and not stock_data.empty:
                        print(f"Fallback to direct API successful for {symbol}")
                except Exception as api_error:
                    print(f"Direct API fallback failed for {symbol}: {api_error}")
                    fallback_attempts += 1
            
            # If still no data, try cached data with warning
            if (stock_data is None or stock_data.empty) and hasattr(self, 'current_data') and self.current_data is not None:
                # Use cached data with timestamp warning
                old_timestamp = getattr(self.current_data, 'timestamp', None) if hasattr(self.current_data, 'timestamp') else None
                if old_timestamp:
                    from datetime import datetime
                    time_diff = (datetime.now() - old_timestamp).total_seconds()
                    if time_diff < 300:  # Use cached data if less than 5 minutes old
                        stock_data = self.current_data
                        print(f"Using cached data for {symbol} (age: {time_diff:.0f}s)")
            
            if stock_data is not None and not stock_data.empty:
                # Update current data with timestamp for freshness tracking
                from datetime import datetime
                stock_data.timestamp = datetime.now()
                self.current_data = stock_data
                
                # Get the latest close price and additional metrics for display
                latest_close = stock_data['Close'][-1] if len(stock_data) > 0 else 0
                latest_open = stock_data['Open'][-1] if len(stock_data) > 0 and 'Open' in stock_data.columns else 0
                latest_high = stock_data['High'][-1] if len(stock_data) > 0 and 'High' in stock_data.columns else 0
                latest_low = stock_data['Low'][-1] if len(stock_data) > 0 and 'Low' in stock_data.columns else 0
                latest_volume = stock_data['Volume'][-1] if len(stock_data) > 0 and 'Volume' in stock_data.columns else 0
                
                # Calculate intraday metrics
                daily_change = latest_close - latest_open if latest_open != 0 else 0
                daily_change_pct = (daily_change / latest_open * 100) if latest_open != 0 else 0
                
                # Log data freshness
                data_points = len(stock_data)
                print(f"LIVE UPDATE: {symbol} - Price: ${latest_close:.2f} (Δ{daily_change_pct:+.2f}%) - Points: {data_points}")
                
                # Update paper trading positions if holding this symbol
                self.update_paper_position_live(symbol, latest_close, {
                    'open': latest_open,
                    'high': latest_high,
                    'low': latest_low,
                    'volume': latest_volume,
                    'change': daily_change,
                    'change_pct': daily_change_pct
                })
                
                # Update the details panel with latest price (if needed)
                # This could be done more efficiently by just updating price info
                
                # Update chart with latest data if on the chart tab
                current_tab = self.notebook.tab(self.notebook.select(), "text")
                if "Chart" in current_tab:
                    self.refresh_chart()
                
                # Update AI insights if auto-update is enabled and on AI tab
                if self.auto_update_ai and "AI" in current_tab:
                    self.run_enhanced_ai_analysis()
                
                # Update paper trading display if on that tab
                if "Investment" in current_tab or "Paper" in current_tab:
                    self.update_paper_trading_display_live(symbol, latest_close, {
                        'open': latest_open,
                        'high': latest_high,
                        'low': latest_low,
                        'volume': latest_volume,
                        'change': daily_change,
                        'change_pct': daily_change_pct
                    })
                    
                # Update portfolio summary if open
                if hasattr(self, 'portfolio_window') and self.portfolio_window and self.portfolio_window.winfo_exists():
                    self.update_portfolio_summary_live(symbol, latest_close)
                    
            else:
                # No data available - log warning but continue
                print(f"WARN: No data available for {symbol} after {fallback_attempts} attempts")
                # Still update UI to show stale/no data status
                self.update_ui_no_data_status(symbol)
                    
        except Exception as e:
            error_msg = f"CRITICAL ERROR updating live data for {symbol}: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            # Update UI to show error status
            self.update_ui_error_status(symbol, str(e))
    
    def update_ui_no_data_status(self, symbol):
        """Update UI to show no data status"""
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            
            # Update details panel
            if hasattr(self, 'details_text'):
                self.details_text.config(state=tk.NORMAL)
                current_content = self.details_text.get(1.0, tk.END)
                if "NO DATA AVAILABLE" not in current_content:
                    self.details_text.insert(tk.END, f"\n⚠️ NO DATA AVAILABLE for {symbol} at this time.\n")
                self.details_text.config(state=tk.DISABLED)
            
            # Update investment panel if on that tab
            if ("Investment" in current_tab or "Paper" in current_tab) and hasattr(self, 'investment_text'):
                self.investment_text.config(state=tk.NORMAL)
                self.investment_text.insert(tk.END, f"\n⚠️ NO DATA AVAILABLE for {symbol} - Live updates paused.\n", ("invest_warning",))
                self.investment_text.config(state=tk.DISABLED)
                
        except Exception as ui_error:
            print(f"Error updating UI no-data status: {ui_error}")
    
    def update_ui_error_status(self, symbol, error_message):
        """Update UI to show error status"""
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            
            # Update details panel
            if hasattr(self, 'details_text'):
                self.details_text.config(state=tk.NORMAL)
                self.details_text.insert(tk.END, f"\n❌ ERROR: {error_message}\n", ("error",))
                self.details_text.config(state=tk.DISABLED)
            
            # Update investment panel if on that tab
            if ("Investment" in current_tab or "Paper" in current_tab) and hasattr(self, 'investment_text'):
                self.investment_text.config(state=tk.NORMAL)
                self.investment_text.insert(tk.END, f"\n❌ LIVE UPDATE ERROR: {error_message}\n", ("invest_loss",))
                self.investment_text.config(state=tk.DISABLED)
                
        except Exception as ui_error:
            print(f"Error updating UI error status: {ui_error}")
    
    def update_portfolio_summary_live(self, symbol, current_price):
        """Update portfolio summary with live price data"""
        try:
            # Only update if portfolio summary window is open
            if hasattr(self, 'portfolio_window') and self.portfolio_window and self.portfolio_window.winfo_exists():
                # Get current position data
                current_shares = int(self.shares_entry.get()) if self.shares_entry.get().isdigit() and self.shares_entry.get() != "0" else 0
                entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
                
                if current_shares > 0 and entry_price > 0:
                    # Calculate live portfolio metrics
                    current_value = current_shares * current_price
                    entry_value = current_shares * entry_price
                    pnl = current_value - entry_value
                    pnl_percent = ((current_price - entry_price) / entry_price) * 100 if entry_price != 0 else 0
                    
                    # Update portfolio summary if it exists
                    if hasattr(self, 'portfolio_text') and self.portfolio_text:
                        # Update the live data section in portfolio summary
                        self.portfolio_text.config(state=tk.NORMAL)
                        # Add live update marker
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.portfolio_text.insert(tk.END, f"\n🔄 LIVE UPDATE [{timestamp}]: {symbol}\n", ("highlight",))
                        self.portfolio_text.insert(tk.END, f"Current Price: ${current_price:.2f}\n", ("info",))
                        self.portfolio_text.insert(tk.END, f"Position Value: ${current_value:.2f}\n", ("info",))
                        pnl_tag = "profit" if pnl >= 0 else "loss"
                        self.portfolio_text.insert(tk.END, f"Live P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)\n\n", (pnl_tag,))
                        self.portfolio_text.config(state=tk.DISABLED)
                        
                        # Auto-scroll to show latest update
                        self.portfolio_text.see(tk.END)
                        
        except Exception as e:
            print(f"Error updating portfolio summary live: {e}")
            
    def update_paper_position_live(self, symbol, current_price, additional_data=None):
        """Update paper trading position with live price data and enhanced metrics"""
        try:
            # Check if user has a current position in this symbol
            current_symbol = self.symbol_entry.get().strip().upper()
            if current_symbol == symbol:
                current_shares = int(self.shares_entry.get()) if self.shares_entry.get().isdigit() and self.shares_entry.get() != "0" else 0
                entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
                
                if current_shares > 0 and entry_price > 0:
                    # Calculate current value and P&L
                    current_value = current_shares * current_price
                    entry_value = current_shares * entry_price
                    pnl = current_value - entry_value
                    pnl_percent = ((current_price - entry_price) / entry_price) * 100 if entry_price != 0 else 0
                    
                    # Enhanced metrics from additional data
                    open_price = additional_data.get('open', current_price) if additional_data else current_price
                    high_price = additional_data.get('high', current_price) if additional_data else current_price
                    low_price = additional_data.get('low', current_price) if additional_data else current_price
                    volume = additional_data.get('volume', 0) if additional_data else 0
                    
                    # Calculate enhanced metrics
                    day_range = high_price - low_price if high_price != low_price else 0.01
                    position_in_day_range = ((current_price - low_price) / day_range * 100) if day_range != 0 else 50
                    
                    # Volatility-based risk assessment
                    atr = day_range  # Simplified ATR calculation
                    position_risk = abs(current_price - entry_price) / atr if atr != 0 else 0
                    
                    # Check if stop loss or take profit is triggered
                    stop_loss = float(self.stop_loss_entry.get()) if self.stop_loss_entry.get() != "0.00" else None
                    take_profit = float(self.take_profit_entry.get()) if self.take_profit_entry.get() != "0.00" else None
                    
                    # Enhanced stop loss logic with trailing stops consideration
                    if stop_loss is not None:
                        # Check for standard stop loss
                        stop_loss_triggered = False
                        if entry_price > stop_loss and current_price <= stop_loss:  # Long position stop loss
                            stop_loss_triggered = True
                        elif entry_price < stop_loss and current_price >= stop_loss:  # Short position stop loss
                            stop_loss_triggered
                        
                        # Check for trailing stop (simplified implementation)
                        trailing_stop_distance = abs(current_price - entry_price) * 0.1  # 10% of move as trailing distance
                        trailing_stop_level = entry_price + trailing_stop_distance if current_price > entry_price else entry_price - trailing_stop_distance
                        
                        if not stop_loss_triggered and (
                            (current_price > entry_price and current_price <= trailing_stop_level) or
                            (current_price < entry_price and current_price >= trailing_stop_level)
                        ):
                            print(f"Trailing stop consideration for {symbol}: Price {current_price}, Trailing Level {trailing_stop_level}")
                            # For now, just log - could implement trailing stop logic here
                        
                        if stop_loss_triggered:
                            self.execute_stop_loss(symbol, current_price)
                    
                    if take_profit is not None:
                        if entry_price < take_profit and current_price >= take_profit:  # Long position take profit
                            self.execute_take_profit(symbol, current_price)
                        elif entry_price > take_profit and current_price <= take_profit:  # Short position take profit
                            self.execute_take_profit(symbol, current_price)
                    
        except Exception as e:
            print(f"Error updating paper position live: {e}")
    
    def execute_stop_loss(self, symbol, current_price):
        """Execute stop loss order"""
        try:
            # This would sell the position at the current price
            current_shares = int(self.shares_entry.get()) if self.shares_entry.get().isdigit() and self.shares_entry.get() != "0" else 0
            entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
            
            if current_shares > 0:
                proceeds = current_shares * current_price
                cost = current_shares * entry_price
                pnl = proceeds - cost
                
                # Update account balance
                current_balance = float(self.account_balance_entry.get())
                new_balance = current_balance + pnl
                
                self.account_balance_entry.delete(0, tk.END)
                self.account_balance_entry.insert(0, f"{new_balance:.2f}")
                
                # Clear position
                self.shares_entry.delete(0, tk.END)
                self.shares_entry.insert(0, "0")
                self.entry_price_entry.delete(0, tk.END)
                self.entry_price_entry.insert(0, "0.00")
                
                # Update display
                self.investment_text.config(state=tk.NORMAL)
                self.investment_text.insert(tk.END, f"\n🚨 STOP LOSS TRIGGERED for {symbol}\n", ("invest_warning",))
                self.investment_text.insert(tk.END, f"Sold {current_shares} shares at ${current_price:.2f}\n", ("invest_highlight",))
                self.investment_text.insert(tk.END, f"P&L: ${pnl:.2f} ({((current_price-entry_price)/entry_price)*100:.2f}%)\n", ("invest_loss" if pnl < 0 else "invest_profit",))
                self.investment_text.insert(tk.END, f"New Balance: ${new_balance:.2f}\n\n", ("invest_info",))
                self.investment_text.config(state=tk.DISABLED)
                
                messagebox.showwarning("Stop Loss Executed", f"Stop loss triggered for {symbol}.\nSold at ${current_price:.2f}")
                
        except Exception as e:
            print(f"Error executing stop loss: {e}")
    
    def execute_take_profit(self, symbol, current_price):
        """Execute take profit order"""
        try:
            # This would sell the position at the current price
            current_shares = int(self.shares_entry.get()) if self.shares_entry.get().isdigit() and self.shares_entry.get() != "0" else 0
            entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
            
            if current_shares > 0:
                proceeds = current_shares * current_price
                cost = current_shares * entry_price
                pnl = proceeds - cost
                
                # Update account balance
                current_balance = float(self.account_balance_entry.get())
                new_balance = current_balance + pnl
                
                self.account_balance_entry.delete(0, tk.END)
                self.account_balance_entry.insert(0, f"{new_balance:.2f}")
                
                # Clear position
                self.shares_entry.delete(0, tk.END)
                self.shares_entry.insert(0, "0")
                self.entry_price_entry.delete(0, tk.END)
                self.entry_price_entry.insert(0, "0.00")
                
                # Update display
                self.investment_text.config(state=tk.NORMAL)
                self.investment_text.insert(tk.END, f"\n✅ TAKE PROFIT EXECUTED for {symbol}\n", ("invest_success",))
                self.investment_text.insert(tk.END, f"Sold {current_shares} shares at ${current_price:.2f}\n", ("invest_highlight",))
                self.investment_text.insert(tk.END, f"P&L: ${pnl:.2f} ({((current_price-entry_price)/entry_price)*100:.2f}%)\n", ("invest_profit" if pnl > 0 else "invest_loss",))
                self.investment_text.insert(tk.END, f"New Balance: ${new_balance:.2f}\n\n", ("invest_info",))
                self.investment_text.config(state=tk.DISABLED)
                
                messagebox.showinfo("Take Profit Executed", f"Take profit executed for {symbol}.\nSold at ${current_price:.2f}")
                
        except Exception as e:
            print(f"Error executing take profit: {e}")
    
    def update_paper_trading_display_live(self, symbol, current_price, additional_data=None):
        """Update paper trading display with live data and enhanced metrics when on the investment tab"""
        try:
            current_shares = int(self.shares_entry.get()) if self.shares_entry.get().isdigit() and self.shares_entry.get() != "0" else 0
            entry_price = float(self.entry_price_entry.get()) if self.entry_price_entry.get() and self.entry_price_entry.get() != "0.00" else 0
            
            if current_shares > 0 and entry_price > 0:
                # Calculate live P&L
                current_value = current_shares * current_price
                entry_value = current_shares * entry_price
                pnl = current_value - entry_value
                pnl_percent = ((current_price - entry_price) / entry_price) * 100 if entry_price != 0 else 0
                
                # Enhanced metrics from additional data
                open_price = additional_data.get('open', current_price) if additional_data else current_price
                high_price = additional_data.get('high', current_price) if additional_data else current_price
                low_price = additional_data.get('low', current_price) if additional_data else current_price
                volume = additional_data.get('volume', 0) if additional_data else 0
                daily_change = additional_data.get('change', 0) if additional_data else 0
                daily_change_pct = additional_data.get('change_pct', 0) if additional_data else 0
                
                # Calculate enhanced metrics
                day_range = high_price - low_price if high_price != low_price else 0.01
                position_in_day_range = ((current_price - low_price) / day_range * 100) if day_range != 0 else 50
                distance_from_entry = abs(current_price - entry_price)
                atr = day_range  # Simplified ATR calculation
                risk_reward_ratio = distance_from_entry / atr if atr != 0 else 1
                
                # Get stop loss and take profit levels
                stop_loss = float(self.stop_loss_entry.get()) if self.stop_loss_entry.get() != "0.00" else None
                take_profit = float(self.take_profit_entry.get()) if self.take_profit_entry.get() != "0.00" else None
                
                # Calculate risk/reward if both levels are set
                risk_reward = "N/A"
                if stop_loss is not None and take_profit is not None:
                    risk = abs(entry_price - stop_loss)
                    reward = abs(take_profit - entry_price)
                    if risk != 0:
                        risk_reward = f"{reward/risk:.2f}:1"
                
                # Update the display with live P&L and enhanced metrics
                self.investment_text.config(state=tk.NORMAL)
                
                # Add timestamp and enhanced metrics
                from datetime import datetime
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Only add live update if there's an active position
                self.investment_text.insert(tk.END, f"\n🔄 LIVE UPDATE: {symbol} [{timestamp}]\n", ("invest_highlight",))
                self.investment_text.insert(tk.END, f"Current Price: ${current_price:.2f} ({daily_change_pct:+.2f}%)\n", ("invest_info",))
                self.investment_text.insert(tk.END, f"Day Range: ${low_price:.2f} - ${high_price:.2f}\n", ("invest_info",))
                self.investment_text.insert(tk.END, f"Position in Day Range: {position_in_day_range:.1f}%\n", ("invest_info",))
                self.investment_text.insert(tk.END, f"Volume: {volume:,}\n", ("invest_info",))
                self.investment_text.insert(tk.END, f"Total Value: ${current_value:.2f}\n", ("invest_info",))
                
                # Enhanced P&L display with color coding
                pnl_tag = "invest_profit" if pnl >= 0 else "invest_loss"
                self.investment_text.insert(tk.END, f"Live P&L: ${pnl:.2f} ({pnl_percent:+.2f}%)\n", (pnl_tag,))
                
                # Add risk/reward information
                if risk_reward != "N/A":
                    rr_tag = "invest_profit" if float(risk_reward.split(":")[0]) > 2 else "invest_warning" if float(risk_reward.split(":")[0]) > 1 else "invest_loss"
                    self.investment_text.insert(tk.END, f"Risk/Reward: {risk_reward}\n", (rr_tag,))
                
                # Add position status based on current market conditions
                if stop_loss is not None or take_profit is not None:
                    status_lines = []
                    if stop_loss is not None:
                        sl_distance = abs(current_price - stop_loss)
                        sl_pct = (sl_distance / current_price) * 100
                        status_lines.append(f"Stop Loss: ${stop_loss:.2f} ({sl_pct:.1f}% away)")
                    if take_profit is not None:
                        tp_distance = abs(current_price - take_profit)
                        tp_pct = (tp_distance / current_price) * 100
                        status_lines.append(f"Take Profit: ${take_profit:.2f} ({tp_pct:.1f}% away)")
                    
                    for line in status_lines:
                        self.investment_text.insert(tk.END, f"{line}\n", ("invest_info",))
                
                # Add market context
                market_context = ""
                if daily_change_pct > 2:
                    market_context = "🚀 Strong Up Day"
                elif daily_change_pct > 1:
                    market_context = "📈 Up Day"
                elif daily_change_pct < -2:
                    market_context = "📉 Strong Down Day"
                elif daily_change_pct < -1:
                    market_context = "🔻 Down Day"
                else:
                    market_context = "➡️ Sideways"
                
                self.investment_text.insert(tk.END, f"Market Context: {market_context}\n\n", ("invest_highlight",))
                self.investment_text.config(state=tk.DISABLED)
                
                # Auto-scroll to bottom to show latest update
                self.investment_text.see(tk.END)
                
        except Exception as e:
            error_msg = f"Error updating paper trading display: {e}"
            print(error_msg)
            # Try to show error in UI
            try:
                if hasattr(self, 'investment_text'):
                    self.investment_text.config(state=tk.NORMAL)
                    self.investment_text.insert(tk.END, f"\n❌ DISPLAY ERROR: {error_msg}\n", ("invest_loss",))
                    self.investment_text.config(state=tk.DISABLED)
            except:
                pass

    def get_assistant_response(self):
        """Get response from the trading assistant based on user question"""
        question = self.assistant_question_entry.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question for the assistant")
            return
            
        try:
            # Clear the question entry
            self.assistant_question_entry.delete(0, tk.END)
            
            # Add the question to the assistant display
            self.assistant_text.config(state=tk.NORMAL)
            self.assistant_text.insert(tk.END, f"\n👤 You: {question}\n", ("assistant_caution",))
            
            # Process the question and generate a response
            response = self.process_assistant_question(question)
            
            # Add the response to the assistant display
            self.assistant_text.insert(tk.END, f"🤖 Assistant: {response}\n\n", ("assistant_response",))
            self.assistant_text.config(state=tk.DISABLED)
            
            # Scroll to the bottom to see the new response
            self.assistant_text.yview_moveto(1)
            
        except Exception as e:
            self.assistant_text.config(state=tk.NORMAL)
            self.assistant_text.insert(tk.END, f"\n🤖 Assistant: Sorry, I encountered an error processing your question: {str(e)}\n\n", ("assistant_caution",))
            self.assistant_text.config(state=tk.DISABLED)
            print(f"Error in get_assistant_response: {e}")

    def process_assistant_question(self, question):
        """Process the user's question and generate a sophisticated, context-aware response"""
        question_lower = question.lower()
        symbol = self.symbol_entry.get().strip().upper()
        
        # Default response
        response = "I'm your advanced trading assistant, powered by sophisticated technical analysis. I can provide detailed market insights, trading recommendations, and risk management advice. Please analyze a stock first by entering a symbol and clicking 'Analyze' for specific recommendations."
        
        # Check if user is asking about a specific symbol
        import re
        # Look for stock symbols in the question (usually 1-5 uppercase letters)
        symbol_match = re.search(r'\b([A-Z]{1,5})\b', question)
        if symbol_match:
            symbol = symbol_match.group(1)
            
        # Enhanced symbol extraction with company name matching
        company_symbols = {
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'google': 'GOOGL',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'nvidia': 'NVDA',
            'alphabet': 'GOOGL',
            'netflix': 'NFLX',
            'disney': 'DIS',
            'jpmorgan': 'JPM',
            'bank of america': 'BAC',
            'walmart': 'WMT',
            'coca cola': 'KO',
            'mcdonalds': 'MCD',
            'starbucks': 'SBUX',
            'boeing': 'BA',
            'intel': 'INTC',
            'paypal': 'PYPL',
            'shopify': 'SHOP',
            'square': 'SQ',
            'spotify': 'SPOT',
            'zoom': 'ZM',
            'uber': 'UBER',
            'lyft': 'LYFT',
            'snapchat': 'SNAP',
            'twitter': 'TWTR',
            'facebook': 'META',
            'robinhood': 'HOOD'
        }
        
        # Check for company names in the question
        question_lower_no_punct = re.sub(r'[^\w\s]', '', question_lower)
        for company_name, company_symbol in company_symbols.items():
            if company_name in question_lower_no_punct:
                symbol = company_symbol
                break
        
        # Advanced context-aware question processing
        context_keywords = {
            'buy': ['buy', 'purchase', 'acquire', 'long', 'go long'],
            'sell': ['sell', 'short', 'liquidate', 'exit', 'close'],
            'hold': ['hold', 'keep', 'maintain', 'retain', 'position'],
            'analysis': ['analyze', 'analysis', 'review', 'assessment', 'evaluate'],
            'risk': ['risk', 'danger', 'volatile', 'safe', 'protect'],
            'target': ['target', 'goal', 'objective', 'expectation'],
            'timing': ['when', 'time', 'momentum', 'opportunity', 'entry', 'exit'],
            'strategy': ['strategy', 'approach', 'plan', 'method', 'technique'],
            'technical': ['technical', 'indicator', 'rsi', 'macd', 'moving average', 'sma', 'ema', 'bollinger', 'stochastic'],
            'fundamental': ['fundamental', 'earnings', 'revenue', 'eps', 'dividend', 'p/e', 'valuation'],
            'market': ['market', 'sector', 'industry', 'economy', 'fed', 'interest rate'],
            'portfolio': ['portfolio', 'allocation', 'diversification', 'weighting'],
            'news': ['news', 'event', 'announcement', 'report', 'headline'],
            'sentiment': ['sentiment', 'mood', 'feeling', 'emotion'],
            'volume': ['volume', 'liquidity', 'trading', 'activity'],
            'trend': ['trend', 'direction', 'momentum', 'movement'],
            'support': ['support', 'resistance', 'level', 'zone'],
            'pattern': ['pattern', 'formation', 'setup', 'structure']
        }
        
        # Identify question type based on keywords
        question_type = "general"
        detected_topics = []
        
        for topic, keywords in context_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    detected_topics.append(topic)
                    if topic in ['buy', 'sell', 'hold']:
                        question_type = topic
                    elif topic in ['analysis', 'technical']:
                        question_type = "technical"
                    elif topic in ['strategy', 'risk']:
                        question_type = "strategy"
        
        # If we have current analysis data, use it to answer the question with enhanced intelligence
        if self.current_analysis and self.current_analysis.get('current_price'):
            current_price = self.current_analysis.get('current_price', 0)
            indicators = self.current_analysis.get('indicators', {})
            rsi = indicators.get('rsi', 0)
            sma_20 = indicators.get('sma_20', 0) 
            sma_50 = indicators.get('sma_50', 0)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            volume = self.current_analysis.get('volume', 0)
            prev_close = self.current_analysis.get('prev_close', 0)
            volatility = self.current_analysis.get('risk_metrics', {}).get('volatility', 0)
            
            # Extract additional advanced indicators
            ema_12 = indicators.get('ema_12', 0)
            ema_26 = indicators.get('ema_26', 0)
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            bb_middle = indicators.get('bb_middle', 0)
            stochastic_k = indicators.get('stochastic_k', 0)
            stochastic_d = indicators.get('stochastic_d', 0)
            adx = indicators.get('adx', 0)
            cci = indicators.get('cci', 0)
            
            # Calculate additional metrics
            price_change = ((current_price - prev_close) / prev_close * 100) if prev_close and prev_close != 0 else 0
            
            # Initialize response variables with enhanced context awareness
            action_advice = ""
            confidence = ""
            reasoning = []
            confidence_score = 0
            
            # Enhanced multi-dimensional analysis based on question type
            if question_type == "buy":
                # Sophisticated buy analysis with multiple factors
                buy_signals = 0
                buy_reasoning = []
                
                # RSI-based buy signals with enhanced logic
                if rsi < 20:  # Extremely oversold
                    buy_signals += 2.0
                    buy_reasoning.append(f"RSI extremely oversold ({rsi:.2f}) - strong reversal potential")
                elif rsi < 30:  # Very oversold
                    buy_signals += 1.5
                    buy_reasoning.append(f"RSI very oversold ({rsi:.2f}) - good buying opportunity")
                elif 30 <= rsi <= 40:  # Approaching oversold
                    buy_signals += 0.5
                    buy_reasoning.append(f"RSI approaching oversold ({rsi:.2f}) - moderate opportunity")
                
                # Moving average-based buy signals with multi-timeframe analysis
                if current_price > sma_20 > sma_50:  # Golden Cross pattern
                    buy_signals += 2.0
                    buy_reasoning.append("Golden Cross pattern - strong bullish momentum")
                elif sma_20 > sma_50 and current_price > sma_50 and current_price > sma_20 * 0.98:  # Near golden cross
                    buy_signals += 1.0
                    buy_reasoning.append("Approaching golden cross - bullish alignment")
                elif current_price > sma_20 > sma_50 * 0.99:  # Bullish near-term
                    buy_signals += 0.5
                    buy_reasoning.append("Near-term bullish trend emerging")
                
                # MACD-based buy signals with histogram analysis
                if macd > macd_signal and macd > 0:  # Strong bullish MACD
                    buy_signals += 1.5
                    buy_reasoning.append("MACD strongly bullish with positive momentum")
                elif macd > macd_signal:  # Bullish MACD crossover
                    buy_signals += 1.0
                    buy_reasoning.append("MACD bullish crossover detected")
                elif macd > macd_signal * 0.95:  # Near bullish crossover
                    buy_signals += 0.5
                    buy_reasoning.append("MACD approaching bullish crossover")
                
                # Bollinger Band-based buy signals
                if current_price != 0 and bb_lower != 0 and bb_upper != 0:
                    position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                    if position_in_bands < 0.15:  # Near lower band (support)
                        buy_signals += 1.0
                        buy_reasoning.append("Price near lower Bollinger Band (support zone)")
                    elif position_in_bands < 0.25:  # Lower half of bands
                        buy_signals += 0.5
                        buy_reasoning.append("Price in lower half of Bollinger Bands")
                
                # Stochastic-based buy signals
                if stochastic_k != 0 and stochastic_d != 0:
                    if stochastic_k < 20 and stochastic_d < 20:  # Both in oversold
                        buy_signals += 1.0
                        buy_reasoning.append("Stochastic in oversold zone - potential bullish crossover")
                    elif stochastic_k < stochastic_d and stochastic_k < 30:  # Bullish crossover in oversold
                        buy_signals += 1.5
                        buy_reasoning.append("Stochastic bullish crossover in oversold territory")
                
                # ADX-based trend strength confirmation
                if adx != 0:
                    if adx > 25:  # Strong trend
                        buy_signals += 0.5
                        buy_reasoning.append(f"ADX indicates strong trend ({adx:.2f})")
                    elif adx > 20:  # Moderate trend
                        buy_signals += 0.3
                        buy_reasoning.append(f"ADX indicates moderate trend ({adx:.2f})")
                
                # Volume confirmation
                if volume > 1000000:  # High volume (simplified)
                    buy_signals += 0.3
                    buy_reasoning.append("High volume confirming price action")
                
                # Calculate confidence and generate buy advice
                max_buy_signals = 10.0  # Adjusted for weighted signals
                confidence_score = min(100, (buy_signals / max_buy_signals) * 100)
                
                if buy_signals >= 3.0:
                    action_advice = f"🟢 STRONG BUY RECOMMENDATION for {symbol} at ${current_price:.2f}"
                    confidence = f"with {confidence_score:.1f}% confidence based on multiple confirming factors"
                    reasoning.extend(buy_reasoning[:5])  # Top 5 strongest reasons
                elif buy_signals >= 1.5:
                    action_advice = f"🔵 MODERATE BUY OPPORTUNITY for {symbol} at ${current_price:.2f}"
                    confidence = f"with {confidence_score:.1f}% confidence - proceed with caution"
                    reasoning.extend(buy_reasoning[:3])  # Top 3 reasons
                else:
                    action_advice = f"🟡 NEUTRAL ON {symbol} at ${current_price:.2f}"
                    confidence = f"limited buy signals detected at current levels"
                    if buy_reasoning:
                        reasoning.append(f"Weak buy factors: {', '.join(buy_reasoning[:2])}")
            
            elif question_type == "sell":
                # Sophisticated sell analysis with multiple factors
                sell_signals = 0
                sell_reasoning = []
                
                # RSI-based sell signals with enhanced logic
                if rsi > 80:  # Extremely overbought
                    sell_signals += 2.0
                    sell_reasoning.append(f"RSI extremely overbought ({rsi:.2f}) - strong reversal potential")
                elif rsi > 70:  # Very overbought
                    sell_signals += 1.5
                    sell_reasoning.append(f"RSI very overbought ({rsi:.2f}) - good selling opportunity")
                elif 60 <= rsi <= 70:  # Approaching overbought
                    sell_signals += 0.5
                    sell_reasoning.append(f"RSI approaching overbought ({rsi:.2f}) - moderate opportunity")
                
                # Moving average-based sell signals with multi-timeframe analysis
                if current_price < sma_20 < sma_50:  # Death Cross pattern
                    sell_signals += 2.0
                    sell_reasoning.append("Death Cross pattern - strong bearish momentum")
                elif sma_20 < sma_50 and current_price < sma_50 and current_price < sma_20 * 1.02:  # Near death cross
                    sell_signals += 1.0
                    sell_reasoning.append("Approaching death cross - bearish alignment")
                elif current_price < sma_20 < sma_50 * 1.01:  # Bearish near-term
                    sell_signals += 0.5
                    sell_reasoning.append("Near-term bearish trend emerging")
                
                # MACD-based sell signals with histogram analysis
                if macd < macd_signal and macd < 0:  # Strong bearish MACD
                    sell_signals += 1.5
                    sell_reasoning.append("MACD strongly bearish with negative momentum")
                elif macd < macd_signal:  # Bearish MACD crossover
                    sell_signals += 1.0
                    sell_reasoning.append("MACD bearish crossover detected")
                elif macd < macd_signal * 1.05:  # Near bearish crossover
                    sell_signals += 0.5
                    sell_reasoning.append("MACD approaching bearish crossover")
                
                # Bollinger Band-based sell signals
                if current_price != 0 and bb_lower != 0 and bb_upper != 0:
                    position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                    if position_in_bands > 0.85:  # Near upper band (resistance)
                        sell_signals += 1.0
                        sell_reasoning.append("Price near upper Bollinger Band (resistance zone)")
                    elif position_in_bands > 0.75:  # Upper half of bands
                        sell_signals += 0.5
                        sell_reasoning.append("Price in upper half of Bollinger Bands")
                
                # Stochastic-based sell signals
                if stochastic_k != 0 and stochastic_d != 0:
                    if stochastic_k > 80 and stochastic_d > 80:  # Both in overbought
                        sell_signals += 1.0
                        sell_reasoning.append("Stochastic in overbought zone - potential bearish crossover")
                    elif stochastic_k > stochastic_d and stochastic_k > 70:  # Bearish crossover in overbought
                        sell_signals += 1.5
                        sell_reasoning.append("Stochastic bearish crossover in overbought territory")
                
                # ADX-based trend strength confirmation
                if adx != 0:
                    if adx > 25:  # Strong trend
                        sell_signals += 0.5
                        sell_reasoning.append(f"ADX indicates strong trend ({adx:.2f})")
                    elif adx > 20:  # Moderate trend
                        sell_signals += 0.3
                        sell_reasoning.append(f"ADX indicates moderate trend ({adx:.2f})")
                
                # Volume confirmation
                if volume > 1000000:  # High volume (simplified)
                    sell_signals += 0.3
                    sell_reasoning.append("High volume confirming price action")
                
                # Calculate confidence and generate sell advice
                max_sell_signals = 10.0  # Adjusted for weighted signals
                confidence_score = min(100, (sell_signals / max_sell_signals) * 100)
                
                if sell_signals >= 3.0:
                    action_advice = f"🔴 STRONG SELL RECOMMENDATION for {symbol} at ${current_price:.2f}"
                    confidence = f"with {confidence_score:.1f}% confidence based on multiple confirming factors"
                    reasoning.extend(sell_reasoning[:5])  # Top 5 strongest reasons
                elif sell_signals >= 1.5:
                    action_advice = f"🟠 MODERATE SELL OPPORTUNITY for {symbol} at ${current_price:.2f}"
                    confidence = f"with {confidence_score:.1f}% confidence - proceed with caution"
                    reasoning.extend(sell_reasoning[:3])  # Top 3 reasons
                else:
                    action_advice = f"🟡 NEUTRAL ON {symbol} at ${current_price:.2f}"
                    confidence = f"limited sell signals detected at current levels"
                    if sell_reasoning:
                        reasoning.append(f"Weak sell factors: {', '.join(sell_reasoning[:2])}")
            
            elif question_type == "hold" or question_type == "technical":
                # Enhanced hold analysis and technical assessment
                technical_signals = 0
                technical_reasoning = []
                
                # Price action analysis
                technical_reasoning.append(f"Current Price: ${current_price:.2f} ({price_change:+.2f}% today)")
                
                # RSI neutral zone analysis
                if 30 <= rsi <= 70:
                    technical_signals += 1.0
                    technical_reasoning.append(f"RSI in neutral zone ({rsi:.2f}) - no extreme conditions")
                elif rsi < 30:
                    technical_reasoning.append(f"RSI oversold ({rsi:.2f}) - potential for upward movement")
                elif rsi > 70:
                    technical_reasoning.append(f"RSI overbought ({rsi:.2f}) - potential for downward movement")
                
                # Moving average consolidation
                if sma_20 != 0 and sma_50 != 0:
                    ma_spread = abs(sma_20 - sma_50) / ((sma_20 + sma_50) / 2)
                    if ma_spread < 0.02:  # Less than 2% spread - consolidation
                        technical_signals += 1.0
                        technical_reasoning.append("Moving averages converging - consolidation phase")
                    elif current_price > sma_20 > sma_50:
                        technical_reasoning.append("Bullish trend confirmed (Golden Cross)")
                    elif current_price < sma_20 < sma_50:
                        technical_reasoning.append("Bearish trend confirmed (Death Cross)")
                
                # MACD neutral analysis
                if macd != 0 and macd_signal != 0:
                    macd_spread = abs(macd - macd_signal) / max(abs(macd), 0.001)
                    if macd_spread < 0.1:  # Near zero crossover
                        technical_signals += 0.5
                        technical_reasoning.append("MACD near neutral - momentum transitioning")
                    elif macd > macd_signal:
                        technical_reasoning.append("Bullish momentum trend continuing")
                    else:
                        technical_reasoning.append("Bearish momentum trend continuing")
                
                # Bollinger Band width analysis for volatility
                if bb_upper != 0 and bb_lower != 0 and bb_middle != 0:
                    bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle != 0 else 0
                    if bb_width < 0.05:  # Tight bands - low volatility/squeeze
                        technical_reasoning.append("Bollinger Bands tight - potential breakout imminent")
                    elif bb_width > 0.1:  # Wide bands - high volatility
                        technical_reasoning.append("Bollinger Bands wide - high volatility environment")
                
                # ADX trend strength
                if adx != 0:
                    if adx > 25:
                        technical_reasoning.append(f"Trend strength strong (ADX: {adx:.2f})")
                    elif adx < 20:
                        technical_reasoning.append(f"Trend strength weak (ADX: {adx:.2f}) - range-bound market")
                    else:
                        technical_reasoning.append(f"Trend strength moderate (ADX: {adx:.2f})")
                
                # Generate hold recommendation with technical context
                if technical_signals >= 1.5:
                    action_advice = f"🟡 HOLD RECOMMENDATION for {symbol} at ${current_price:.2f}"
                    confidence = "market in consolidation phase - wait for breakout confirmation"
                    reasoning.extend(technical_reasoning[:5])
                else:
                    action_advice = f"⚖️ ASSESS YOUR CURRENT POSITION in {symbol} at ${current_price:.2f}"
                    confidence = "mixed technical signals - evaluate risk/reward carefully"
                    reasoning.extend(technical_reasoning[:4])
            
            else:
                # General question about the stock with comprehensive overview
                action_advice = f"📊 COMPREHENSIVE OVERVIEW for {symbol} at ${current_price:.2f}"
                
                # Add technical summary with enhanced insights
                tech_summary = []
                
                if rsi != 0:
                    if rsi < 20:
                        tech_summary.append(f"RSI extremely oversold ({rsi:.2f}) - potential reversal")
                    elif rsi < 30:
                        tech_summary.append(f"RSI very oversold ({rsi:.2f}) - buying opportunity")
                    elif rsi > 80:
                        tech_summary.append(f"RSI extremely overbought ({rsi:.2f}) - potential pullback")
                    elif rsi > 70:
                        tech_summary.append(f"RSI very overbought ({rsi:.2f}) - selling pressure")
                    else:
                        tech_summary.append(f"RSI neutral ({rsi:.2f}) - balanced market")
                
                if current_price != 0 and sma_20 != 0 and sma_50 != 0:
                    if current_price > sma_20 > sma_50:
                        tech_summary.append("Strong bullish trend (Golden Cross)")
                    elif current_price < sma_20 < sma_50:
                        tech_summary.append("Strong bearish trend (Death Cross)")
                    elif sma_20 > sma_50:
                        tech_summary.append("Bullish bias in moving averages")
                    elif sma_20 < sma_50:
                        tech_summary.append("Bearish bias in moving averages")
                    else:
                        tech_summary.append("Moving averages neutral")
                
                if macd != 0 and macd_signal != 0:
                    if macd > macd_signal:
                        tech_summary.append("Bullish MACD momentum")
                    else:
                        tech_summary.append("Bearish MACD momentum")
                
                if volatility != 0:
                    if volatility < 0.015:
                        risk_assessment = "Very Low Risk"
                    elif volatility < 0.03:
                        risk_assessment = "Low Risk"
                    elif volatility < 0.06:
                        risk_assessment = "Moderate Risk"
                    else:
                        risk_assessment = "High Risk"
                    tech_summary.append(f"Risk Level: {risk_assessment} (Volatility: {volatility:.5f})")
                
                if price_change != 0:
                    tech_summary.append(f"Daily Performance: {price_change:+.2f}%")
                
                # Generate response with comprehensive overview
                action_advice = f"📊 TECHNICAL OVERVIEW for {symbol}"
                confidence = f"Current Price: ${current_price:.2f} ({price_change:+.2f}% today)"
                reasoning = tech_summary[:6]  # Limit to top 6 insights
            
            # Try to get enhanced ML insights if available
            try:
                # Import the enhanced AI from the market researcher
                from robinhood_market_researcher import AdvancedAIInsights
                ai_insights = AdvancedAIInsights()
                comprehensive_insights = ai_insights.generate_comprehensive_insights(symbol, analysis)
                
                # If we have enhanced ML insights, incorporate them into the response
                if 'ml_insights' in comprehensive_insights and comprehensive_insights['ml_insights']:
                    ml_insights = comprehensive_insights['ml_insights']
                    
                    # Update action advice with ML-based recommendation if needed
                    if 'ensemble_prediction' in ml_insights:
                        ensemble_pred = ml_insights['ensemble_prediction']
                        
                        # Only update the decision if the ML model has high confidence
                        if ensemble_pred['confidence'] > 0.7:  # High confidence threshold
                            action_advice = f"🤖 ENHANCED ML RECOMMENDATION: {ensemble_pred['recommendation']} for {symbol} at ${current_price:.2f}"
                            ml_confidence = f"with {ensemble_pred['confidence'] * 100:.1f}% confidence - ML ensemble model"
                            
                            # Replace the previous confidence if needed
                            confidence = ml_confidence
                            
                            # Add ML-specific reasoning if available
                            if ensemble_pred['score'] != 0:
                                ml_reasoning = []
                                if ensemble_pred['momentum_component'] != 0:
                                    direction = "Bullish" if ensemble_pred['momentum_component'] > 0 else "Bearish"
                                    strength = "Strong" if abs(ensemble_pred['momentum_component']) > 0.3 else "Moderate"
                                    ml_reasoning.append(f"{strength} {direction} Momentum Component")
                                
                                if ensemble_pred['mean_reversion_component'] != 0:
                                    direction = "Bullish" if ensemble_pred['mean_reversion_component'] > 0 else "Bearish"
                                    strength = "Strong" if abs(ensemble_pred['mean_reversion_component']) > 0.3 else "Moderate"
                                    ml_reasoning.append(f"{strength} {direction} Mean Reversion Component")
                                
                                if ensemble_pred['trend_component'] != 0:
                                    direction = "Bullish" if ensemble_pred['trend_component'] > 0 else "Bearish"
                                    strength = "Strong" if abs(ensemble_pred['trend_component']) > 0.3 else "Moderate"
                                    ml_reasoning.append(f"{strength} {direction} Trend Component")
                                
                                if ml_reasoning:
                                    reasoning = ml_reasoning  # Replace technical reasoning with ML reasoning for high-confidence decisions
                            
                            # Add pattern recognition insights
                            if 'pattern_recognition' in ml_insights and ml_insights['pattern_recognition']:
                                patterns = list(ml_insights['pattern_recognition'].values())
                                if patterns:
                                    reasoning.extend(patterns[:2])  # Add up to 2 pattern insights
                            
                            # Add price targets from ML model
                            if 'price_targets' in ml_insights:
                                targets = ml_insights['price_targets']
                                response_parts.append(f"\\n🎯 ML-BASED PRICE TARGETS:")
                                response_parts.append(f"   • Short-term: ${targets['short_term']:.2f}")
                                response_parts.append(f"   • Medium-term: ${targets['medium_term']:.2f}")
                                response_parts.append(f"   • Stop loss: ${targets['stop_loss']:.2f}")
                
                # Include sentiment analysis in the response
                if 'sentiment_insights' in comprehensive_insights:
                    sentiment_data = comprehensive_insights['sentiment_insights']
                    
                    # Add sentiment to the response
                    response_parts.append(f"\\n🧠 MARKET SENTIMENT ANALYSIS:")
                    response_parts.append(f"   • News Sentiment: {sentiment_data.get('news_sentiment', {}).get('sentiment_label', 'N/A')}")
                    response_parts.append(f"   • Social Sentiment: {sentiment_data.get('social_sentiment', {}).get('sentiment_label', 'N/A')}")
                    response_parts.append(f"   • Combined Sentiment: {sentiment_data.get('sentiment_label', 'N/A')}")
                    
                    # Add sentiment impact to reasoning
                    combined_sentiment = sentiment_data.get('combined_sentiment', 0)
                    if abs(combined_sentiment) > 0.3:  # Strong sentiment
                        sentiment_direction = "Positive" if combined_sentiment > 0 else "Negative"
                        reasoning.append(f"Strong {sentiment_direction.lower()} market sentiment")
            except ImportError:
                # If AdvancedAIInsights is not available, continue with original analysis
                pass
            
            # Construct the enhanced response with multiple layers of information
            response_parts = [f"🤖 ADVANCED AI ASSISTANT RESPONSE FOR {symbol.upper()}"]
            response_parts.append("="*50)
            response_parts.append("")
            response_parts.append(action_advice)
            
            if confidence:
                response_parts.append(f"({confidence})")
            
            if reasoning:
                response_parts.append("")
                response_parts.append("📋 ANALYSIS FACTORS:")
                for i, reason in enumerate(reasoning, 1):
                    response_parts.append(f"   {i}. {reason}")
            
            # Add contextual recommendations based on topics mentioned in question
            if detected_topics:
                response_parts.append("")
                response_parts.append("🎯 CONTEXT-SPECIFIC INSIGHTS:")
                
                # Add recommendations based on detected topics
                for topic in detected_topics[:3]:  # Limit to top 3 topics
                    if topic == "risk":
                        if volatility != 0:
                            if volatility < 0.015:
                                response_parts.append("   🔒 Low volatility environment - consider larger position sizes")
                            elif volatility > 0.06:
                                response_parts.append("   🔒 High volatility environment - use smaller positions and tight stops")
                            else:
                                response_parts.append("   🔒 Moderate risk profile - standard position sizing appropriate")
                    elif topic == "timing":
                        if rsi < 30 or rsi > 70:
                            response_parts.append("   ⏰ Market at extremes - consider mean reversion timing")
                        else:
                            response_parts.append("   ⏰ Market neutral - wait for clearer signals")
                    elif topic == "volume":
                        if volume > 1000000:
                            response_parts.append("   🔊 High volume confirms price action reliability")
                        elif volume < 100000:
                            response_parts.append("   🔇 Low volume may indicate unreliable price movements")
                    elif topic == "trend":
                        if adx != 0:
                            if adx > 25:
                                response_parts.append("   📈 Strong trend confirmed - follow momentum")
                            elif adx < 20:
                                response_parts.append("   📈 Weak trend - consider range trading approach")
            
            # Add actionable next steps
            response_parts.append("")
            response_parts.append("🚀 ACTIONABLE NEXT STEPS:")
            
            if "buy" in detected_topics or question_type == "buy":
                response_parts.append("   • Set protective stop-loss at key support levels")
                response_parts.append("   • Consider scaling into position with multiple entries")
                response_parts.append("   • Monitor volume confirmation on entry")
            elif "sell" in detected_topics or question_type == "sell":
                response_parts.append("   • Set profit-taking targets at key resistance levels")
                response_parts.append("   • Consider partial exits to lock in gains")
                response_parts.append("   • Monitor for reversal signals before complete exit")
            else:
                response_parts.append("   • Continue monitoring key technical levels")
                response_parts.append("   • Adjust stops based on recent price action")
                response_parts.append("   • Reassess position on significant technical changes")
            
            # Add timestamp and confidence metrics
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response_parts.append("")
            response_parts.append(f"📅 Analysis Timestamp: {timestamp}")
            response_parts.append(f"🧠 AI Confidence Score: {confidence_score:.1f}/100.0")
            
            response = "\n".join(response_parts)
        
        else:
            # No current analysis, prompt user to analyze a stock with enhanced guidance
            if symbol:
                response = (f"🤖 To provide specific, data-driven recommendations for {symbol}, "
                          f"I need current market data. Please click the 'Analyze' button to load "
                          f"real-time technical indicators and generate a comprehensive analysis.\n\n"
                          f"Once analyzed, I can provide:\n"
                          f"   • Advanced buy/sell recommendations\n"
                          f"   • Risk-adjusted position sizing\n"
                          f"   • Multi-timeframe technical insights\n"
                          f"   • Market context and timing guidance\n"
                          f"   • Custom risk management strategies")
            else:
                response = ("🤖 To get personalized trading insights, please enter a stock symbol "
                          "and click 'Analyze' first. This will load real-time market data and enable "
                          "me to provide specific, actionable recommendations tailored to current conditions.\n\n"
                          "I can help with:\n"
                          "   • Technical analysis interpretation\n"
                          "   • Trading opportunity identification\n"
                          "   • Risk management strategies\n"
                          "   • Market timing guidance\n"
                          "   • Portfolio positioning advice")
        
        return response

    def search_ticker(self):
        """Search for stock ticker by company name or validate ticker symbol"""
        # Create a new window for searching
        search_window = tk.Toplevel(self.root)
        search_window.title("Search for Stock Ticker")
        search_window.geometry("500x400")
        search_window.configure(bg="#1e1e1e")
        
        # Add title
        title_label = tk.Label(search_window, text="🔍 Search for Company or Ticker", 
                              font=("Arial", 14, "bold"), fg="#64b5f6", bg="#1e1e1e")
        title_label.pack(pady=10)
        
        # Search input
        search_frame = tk.Frame(search_window, bg="#1e1e1e")
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        search_label = tk.Label(search_frame, text="Enter company name or ticker:", 
                               font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e")
        search_label.pack(anchor=tk.W)
        
        search_entry = tk.Entry(search_frame, font=("Arial", 11), 
                               bg="#2d2d2d", fg="#e0e0e0", insertbackground="#e0e0e0",
                               relief=tk.FLAT, highlightthickness=1, 
                               highlightcolor="#64b5f6", width=30)
        search_entry.pack(fill=tk.X, pady=5)
        
        # Search results area
        results_frame = tk.Frame(search_window, bg="#1e1e1e")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        results_label = tk.Label(results_frame, text="Search Results:", 
                                font=("Arial", 10, "bold"), fg="#e0e0e0", bg="#1e1e1e")
        results_label.pack(anchor=tk.W)
        
        results_text = scrolledtext.ScrolledText(results_frame, 
                                                bg="#2d2d2d", fg="#e0e0e0",
                                                font=("Consolas", 9),
                                                relief=tk.FLAT,
                                                insertbackground="#e0e0e0")
        results_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for results
        results_text.tag_configure("ticker", font=("Arial", 10, "bold"), foreground="#64b5f6")
        results_text.tag_configure("name", font=("Arial", 9), foreground="#e0e0e0")
        results_text.tag_configure("action", font=("Arial", 9, "bold"), foreground="#4CAF50")
        
        def perform_search():
            query = search_entry.get().strip()
            if not query:
                messagebox.showwarning("Warning", "Please enter a search term")
                return
            
            # Clear previous results
            results_text.config(state=tk.NORMAL)
            results_text.delete(1.0, tk.END)
            
            # In a real implementation, we would connect to a ticker lookup service
            # For now, we'll use a basic demo with some common tickers
            # This is a simplified version - in production, connect to an API like Alpha Vantage, Finnhub, etc.
            
            # Common ticker symbols for demonstration
            common_tickers = {
                "AAPL": "Apple Inc.",
                "MSFT": "Microsoft Corporation", 
                "GOOGL": "Alphabet Inc.",
                "AMZN": "Amazon.com Inc.",
                "TSLA": "Tesla, Inc.",
                "META": "Meta Platforms, Inc.",
                "NVDA": "NVIDIA Corporation",
                "JPM": "JPMorgan Chase & Co.",
                "JNJ": "Johnson & Johnson",
                "V": "Visa Inc.",
                "PG": "Procter & Gamble Co.",
                "UNH": "UnitedHealth Group Inc.",
                "HD": "The Home Depot, Inc.",
                "MA": "Mastercard Incorporated",
                "DIS": "The Walt Disney Company",
                "ADBE": "Adobe Inc.",
                "CRM": "Salesforce, Inc.",
                "NFLX": "Netflix, Inc.",
                "PYPL": "PayPal Holdings, Inc.",
                "BAC": "Bank of America Corporation",
                "VZ": "Verizon Communications Inc.",
                "KO": "The Coca-Cola Company",
                "XOM": "Exxon Mobil Corporation",
                "PFE": "Pfizer Inc.",
                "INTC": "Intel Corporation",
                "CSCO": "Cisco Systems, Inc.",
                "WMT": "Walmart Inc.",
                "MRK": "Merck & Co., Inc.",
                "T": "AT&T Inc.",
                "ABBV": "AbbVie Inc.",
                "CVX": "Chevron Corporation",
                "LLY": "Eli Lilly and Company",
                "AVGO": "Broadcom Inc.",
                "ACN": "Accenture plc",
                "TXN": "Texas Instruments Incorporated",
                "CMCSA": "Comcast Corporation",
                "DHR": "Danaher Corporation",
                "COST": "Costco Wholesale Corporation",
                "QCOM": "Qualcomm Incorporated",
                "HON": "Honeywell International Inc.",
                "NEE": "NextEra Energy, Inc.",
                "BMY": "Bristol-Myers Squibb Company",
                "SPY": "SPDR S&P 500 ETF Trust",
                "QQQ": "Invesco QQQ Trust",
                "IWM": "iShares Russell 2000 ETF",
                "EFA": "iShares MSCI EAFE ETF",
                "TLT": "iShares 20+ Year Treasury Bond ETF",
                "GLD": "SPDR Gold Shares",
                "SLV": "iShares Silver Trust",
                "USO": "United States Oil Fund",
                "VXX": "iPath Series B S&P 500 VIX Short-Term Futures ETN",
                "GDX": "VanEck Gold Miners ETF",
                "XLE": "Energy Select Sector SPDR Fund",
                "XLF": "Financial Select Sector SPDR Fund",
                "XLK": "Technology Select Sector SPDR Fund",
                "XLY": "Consumer Discretionary Select Sector SPDR Fund",
                "XLP": "Consumer Staples Select Sector SPDR Fund",
                "XLV": "Health Care Select Sector SPDR Fund",
                "XLI": "Industrial Select Sector SPDR Fund",
                "XLB": "Materials Select Sector SPDR Fund",
                "XLRE": "Real Estate Select Sector SPDR Fund",
                "XLU": "Utilities Select Sector SPDR Fund",
                "XLC": "Communication Services Select Sector SPDR Fund",
                "SNAP": "Snap Inc.",
                "HBM": "Hudbay Minerals Inc.",
                "GME": "GameStop Corp.",
                "AMC": "AMC Entertainment Holdings, Inc.",
                "NOK": "Nokia Corporation",
                "BB": "BlackBerry Limited",
                "PLTR": "Palantir Technologies Inc.",
                "RIVN": "Rivian Automotive, Inc.",
                "LCID": "Lucid Group, Inc.",
                "HOOD": "Robinhood Markets, Inc.",
                "COIN": "Coinbase Global, Inc."
            }
            
            # Search for matches
            found_matches = []
            query_lower = query.lower()
            
            for ticker, name in common_tickers.items():
                if query_lower in ticker.lower() or query_lower in name.lower():
                    found_matches.append((ticker, name))
                    
                    # Add to results text
                    results_text.insert(tk.END, f"{ticker}", ("ticker",))
                    results_text.insert(tk.END, f" - {name}\n", ("name",))
            
            if found_matches:
                results_text.insert(tk.END, f"\n{len(found_matches)} result(s) found.\n\n", ("name",))
                
                # Add buttons to select each result
                for ticker, name in found_matches:
                    select_btn = tk.Button(results_frame, text=f"Select {ticker}", 
                                          command=lambda t=ticker: self._select_ticker(t, search_entry, search_window),
                                          bg="#4CAF50", fg="white", font=("Arial", 9),
                                          relief=tk.FLAT)
                    results_text.window_create(tk.END, window=select_btn)
                    results_text.insert(tk.END, "\n")
            else:
                results_text.insert(tk.END, f"No matches found for '{query}'.\n\nTry a different search term or enter a ticker symbol directly.", ("name",))
            
            results_text.config(state=tk.DISABLED)
        
        # Add search button
        search_btn = tk.Button(search_frame, text="🔍 Search", command=perform_search,
                              bg="#2196F3", fg="white", font=("Arial", 10),
                              relief=tk.FLAT)
        search_btn.pack(pady=5)
        
        # Bind Enter key to search
        search_entry.bind("<Return>", lambda event: perform_search())
        
        # Focus on the search entry
        search_entry.focus()

    def _select_ticker(self, ticker, search_entry, window):
        """Helper function to select a ticker and close the search window"""
        self.symbol_entry.delete(0, tk.END)
        self.symbol_entry.insert(0, ticker)
        window.destroy()
        # Automatically analyze the selected ticker
        self.analyze_stock()

    def analyze_stock(self):
        """Analyze the entered stock symbol with improved updates"""
        symbol = self.symbol_entry.get().strip().upper()
        print(f"DEBUG: Starting analysis for symbol: {symbol}")  # Debug print
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return
        
        try:
            # Store current symbol for reference
            self.current_symbol = symbol
            print(f"DEBUG: Current symbol set to: {self.current_symbol}")  # Debug print
            
            # Fetch data once and store it for consistent use across all components
            print(f"DEBUG: Fetching data for {symbol} to use across all components")  # Debug print
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            stock_data = analyzer.watchlist.get_stock_data(symbol)
            
            if stock_data is not None and not stock_data.empty:
                print(f"DEBUG: Successfully fetched data for {symbol}, length: {len(stock_data)}")  # Debug print
                # Store the data for use by other components
                self.current_data = stock_data
            else:
                print(f"DEBUG: Failed to fetch data for {symbol}")  # Debug print
                # If we can't get data, at least try to update the UI with what we have
                self.current_data = None
            
            # Display stock info first
            print(f"DEBUG: Calling display_stock_info for {symbol}")  # Debug print
            self.display_stock_info(symbol)
            
            # Update chart immediately (no delay)
            print(f"DEBUG: Refreshing chart for {symbol}")  # Debug print
            self.refresh_chart()
            
            # Update AI insights when user explicitly analyzes (regardless of auto-update setting)
            print(f"DEBUG: Calling run_enhanced_ai_analysis for {symbol}")  # Debug print
            # Run immediately instead of after delay to ensure it happens right away
            self.run_enhanced_ai_analysis()
                
            print(f"DEBUG: Successfully analyzed {symbol} - All updates completed")
            
            # AGGRESSIVE VISUAL UI REFRESH - Force complete visual update
            # Store current tab index before forcing refresh
            try:
                current_tab = self.notebook.index(self.notebook.select())
                
                # Check if all required frames exist before accessing them
                required_frames = []
                if hasattr(self, 'details_frame'):
                    required_frames.append(self.details_frame)
                if hasattr(self, 'chart_frame'):
                    required_frames.append(self.chart_frame)
                if hasattr(self, 'options_frame'):
                    required_frames.append(self.options_frame)
                if hasattr(self, 'ai_frame'):
                    required_frames.append(self.ai_frame)
                if hasattr(self, 'investment_frame'):
                    required_frames.append(self.investment_frame)
                
                # Force refresh of the currently visible tab by switching away and back
                all_tabs = required_frames
                
                # Find a different tab to switch to temporarily
                temp_tab = None
                for tab in all_tabs:
                    if self.notebook.index(tab) != current_tab:
                        temp_tab = tab
                        break
            except Exception as e:
                print(f"Error during UI refresh: {e}")
                # Continue execution even if UI refresh fails
            
            # Switch to a different tab and back to force refresh of content
            if temp_tab:
                self.notebook.select(temp_tab)
                self.root.update_idletasks()
                self.root.update()
                
                # Switch back to original tab
                self.notebook.select(current_tab)
                
            # Additional force refresh for the text widgets in the current tab
            self.root.update_idletasks()
            self.root.update()
            
            # Also try to force focus on the current tab's content
            current_widget = self.notebook.nametowidget(self.notebook.select())
            if current_widget:
                current_widget.update_idletasks()
                current_widget.focus_force()
            
            # Refresh options data for the new symbol
            self.root.after(100, self.refresh_options_data)  # Refresh options after other updates
            
            # Final comprehensive update
            self.root.update_idletasks()
            self.root.update()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze {symbol}: {str(e)}")
            print(f"DEBUG: Error in analyze_stock: {e}")
            import traceback
            traceback.print_exc()

    def display_stock_info(self, symbol):
        """Display detailed stock information"""
        print(f"DEBUG: display_stock_info called for symbol: {symbol}")  # Debug print
        try:
            # Use the analysis function from our module for consistency
            print(f"DEBUG: Calling robinhood_market_researcher.analyze_stock for {symbol}")  # Debug print
            analysis = robinhood_market_researcher.analyze_stock(symbol)
            print(f"DEBUG: Analysis received for {symbol}, type: {type(analysis)}")  # Debug print
            if analysis:
                print(f"DEBUG: Analysis symbol: {analysis.get('symbol', 'N/A')}")  # Debug print
            
            # Store current analysis for other functions
            self.current_analysis = analysis
            print(f"DEBUG: Current analysis stored for symbol: {self.current_analysis.get('symbol', 'N/A') if self.current_analysis else 'None'}")  # Debug print
            
            if analysis:
                # Clear the text area
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                
                # Display basic stock info
                self.details_text.insert(tk.END, f"📈 {symbol.upper()} - ", ("section",))
                self.details_text.insert(tk.END, f"{analysis.get('company_name', 'Company Name Unknown')}\n\n", ("normal",))
                
                # Current price with color coding
                latest_close = analysis.get('current_price', 0)
                if 'prev_close' in analysis and analysis.get('prev_close'):
                    price_change = latest_close - analysis['prev_close']
                    price_change_percent = (price_change / analysis['prev_close']) * 100 if analysis['prev_close'] != 0 else 0
                else:
                    price_change = 0
                    price_change_percent = 0
                
                # Color-code the price based on movement
                if price_change >= 0:
                    self.details_text.insert(tk.END, f"Current Price: ", ("normal",))
                    self.details_text.insert(tk.END, f"${latest_close:.2f}", ("green",))
                    self.details_text.insert(tk.END, f" (+{price_change_percent:.2f}%)", ("green",))
                    self.details_text.insert(tk.END, f"  [UP]\n\n")
                else:
                    self.details_text.insert(tk.END, f"Current Price: ", ("normal",))
                    self.details_text.insert(tk.END, f"${latest_close:.2f}", ("red",))
                    self.details_text.insert(tk.END, f" ({price_change_percent:.2f}%)", ("red",))
                    self.details_text.insert(tk.END, f"  [DOWN]\n\n")
                
                # Technical Indicators with better formatting
                self.details_text.insert(tk.END, "📊 TECHNICAL INDICATORS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                
                # Safely get indicators
                indicators = analysis.get('indicators', {})
                
                # RSI with color coding
                rsi = indicators.get('rsi', 0)
                if rsi != 0:  # Only show RSI if it exists
                    rsi_status = "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL"
                    rsi_color = "green" if rsi < 30 else "red" if rsi > 70 else "normal"
                    self.details_text.insert(tk.END, f"RSI (14): {rsi:.2f} ({rsi_status})\n", (rsi_color,))
                else:
                    self.details_text.insert(tk.END, f"RSI: N/A\n")
                
                # Moving averages
                sma_20 = indicators.get('sma_20', 0)
                sma_50 = indicators.get('sma_50', 0)
                ema_12 = indicators.get('ema_12', 0)
                ema_26 = indicators.get('ema_26', 0)
                
                if sma_20 != 0 and sma_50 != 0:  # Only show if valid values exist
                    if sma_20 > sma_50:
                        self.details_text.insert(tk.END, f"SMA 20: ", ("normal",))
                        self.details_text.insert(tk.END, f"{sma_20:.2f}", ("green",))  # Bullish
                        self.details_text.insert(tk.END, f" | SMA 50: {sma_50:.2f}  [BULLISH CROSSED]\n")
                    else:
                        self.details_text.insert(tk.END, f"SMA 20: ", ("normal",))
                        self.details_text.insert(tk.END, f"{sma_20:.2f}", ("red",))  # Bearish
                        self.details_text.insert(tk.END, f" | SMA 50: {sma_50:.2f}  [BEARISH CROSSED]\n")
                else:
                    self.details_text.insert(tk.END, f"SMA 20: N/A | SMA 50: N/A\n")
                
                # EMA trend
                if ema_12 != 0 and ema_26 != 0:  # Only show if valid values exist
                    if ema_12 > ema_26:
                        self.details_text.insert(tk.END, f"EMA 12: ", ("normal",))
                        self.details_text.insert(tk.END, f"{ema_12:.2f}", ("green",))
                        self.details_text.insert(tk.END, f" | EMA 26: {ema_26:.2f}  [BULLISH]\n")
                    else:
                        self.details_text.insert(tk.END, f"EMA 12: ", ("normal",))
                        self.details_text.insert(tk.END, f"{ema_12:.2f}", ("red",))
                        self.details_text.insert(tk.END, f" | EMA 26: {ema_26:.2f}  [BEARISH]\n")
                else:
                    self.details_text.insert(tk.END, f"EMA 12: N/A | EMA 26: N/A\n")
                
                # MACD
                macd = indicators.get('macd', 0)
                macd_signal = indicators.get('macd_signal', 0)
                macd_histogram = indicators.get('macd_histogram', 0)
                if macd != 0 or macd_signal != 0:  # Only show if valid values exist
                    if macd > macd_signal:
                        self.details_text.insert(tk.END, f"MACD: {macd:.4f} | Signal: {macd_signal:.4f} | Histogram: {macd_histogram:.4f}  [BULLISH]\n")
                    else:
                        self.details_text.insert(tk.END, f"MACD: {macd:.4f} | Signal: {macd_signal:.4f} | Histogram: {macd_histogram:.4f}  [BEARISH]\n")
                else:
                    self.details_text.insert(tk.END, f"MACD: N/A | Signal: N/A | Histogram: N/A\n")
                
                # Bollinger Bands
                current_price = analysis.get('current_price', 0)
                bb_upper = indicators.get('bb_upper', 0)
                bb_lower = indicators.get('bb_lower', 0)
                bb_middle = indicators.get('bb_middle', 0)
                
                if bb_upper != 0 and bb_lower != 0 and current_price != 0:  # Only show if valid values exist
                    position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                    bb_status = ""
                    if current_price > bb_upper:
                        bb_status = "ABOVE UPPER BAND [CONSIDER SELLING]"
                    elif current_price < bb_lower:
                        bb_status = "BELOW LOWER BAND [CONSIDER BUYING]"
                    elif position_in_bands > 0.8:
                        bb_status = "NEAR UPPER BAND [CONSIDER SELLING]"
                    elif position_in_bands < 0.2:
                        bb_status = "NEAR LOWER BAND [CONSIDER BUYING]"
                    else:
                        bb_status = "MIDDLE BANDS [NEUTRAL]"
                    
                    self.details_text.insert(tk.END, f"BB Upper: {bb_upper:.2f} | Middle: {bb_middle:.2f} | Lower: {bb_lower:.2f}\n")
                    self.details_text.insert(tk.END, f"BB Position: {position_in_bands:.2%} ({bb_status})\n\n")
                else:
                    self.details_text.insert(tk.END, f"BB Upper: N/A | Middle: N/A | Lower: N/A\n\n")
                
                # Signals with better formatting
                self.details_text.insert(tk.END, "💡 TRADING SIGNALS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                
                signals = analysis.get('signals', [])
                if signals:
                    for signal in signals:
                        if "OVERBOUGHT" in signal or "BEARISH" in signal or "SIGNAL" in signal:
                            self.details_text.insert(tk.END, f"• {signal}  [SELL INDICATOR]\n", ("red",))
                        elif "OVERSOLD" in signal or "BULLISH" in signal or "BUY" in signal:
                            self.details_text.insert(tk.END, f"• {signal}  [BUY INDICATOR]\n", ("green",))
                        else:
                            self.details_text.insert(tk.END, f"• {signal}\n")
                else:
                    self.details_text.insert(tk.END, f"• No trading signals available\n")
                
                # Patterns
                patterns = analysis.get('patterns', [])
                if patterns:
                    self.details_text.insert(tk.END, "\n🔍 CHART PATTERNS\n", ("section",))
                    self.details_text.insert(tk.END, "─" * 40 + "\n")
                    for pattern in patterns:
                        self.details_text.insert(tk.END, f"• {pattern}\n")
                else:
                    self.details_text.insert(tk.END, "\n🔍 CHART PATTERNS\n", ("section",))
                    self.details_text.insert(tk.END, "─" * 40 + "\n")
                    self.details_text.insert(tk.END, "No specific patterns detected\n")
                
                # Risk Metrics
                self.details_text.insert(tk.END, "\n⚠️ RISK METRICS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                
                risk = analysis.get('risk_metrics', {})
                volatility = risk.get('volatility', 0)
                if volatility != 0:
                    volatility_desc = "LOW" if volatility < 0.02 else "MODERATE" if volatility < 0.05 else "HIGH"
                    avg_return = risk.get('avg_return', 0)
                    sharpe_ratio = risk.get('sharpe_ratio', 0)
                    
                    self.details_text.insert(tk.END, f"Volatility: {volatility:.4f} ({volatility_desc})\n")
                    self.details_text.insert(tk.END, f"Average Return: {avg_return:.4f} ({avg_return*100:.2f}%)\n")
                    self.details_text.insert(tk.END, f"Sharpe Ratio: {sharpe_ratio:.4f}\n")
                else:
                    self.details_text.insert(tk.END, f"Volatility: N/A\n")
                    self.details_text.insert(tk.END, f"Average Return: N/A\n")
                    self.details_text.insert(tk.END, f"Sharpe Ratio: N/A\n")
                
                # Price levels and support/resistance
                self.details_text.insert(tk.END, "\n🎯 KEY LEVELS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                
                # Calculate approximate support and resistance based on recent high/low
                analyzer = robinhood_market_researcher.MarketAnalyzer()
                stock_data = analyzer.watchlist._get_stock_data(symbol)
                if stock_data is not None and not stock_data.empty:
                    recent_high = stock_data['High'][-20:].max() if len(stock_data) >= 20 else bb_upper
                    recent_low = stock_data['Low'][-20:].min() if len(stock_data) >= 20 else bb_lower
                    self.details_text.insert(tk.END, f"Recent High: ${recent_high:.2f}\n")
                    self.details_text.insert(tk.END, f"Recent Low: ${recent_low:.2f}\n")
                else:
                    self.details_text.insert(tk.END, f"Recent High: N/A\n")
                    self.details_text.insert(tk.END, f"Recent Low: N/A\n")
                
                # Overall trend summary - only calculate if we have the required data
                if rsi != 0 and sma_20 != 0 and sma_50 != 0 and macd != 0 and macd_signal != 0:
                    bull_signals = sum([
                        rsi < 30,  # Oversold
                        sma_20 > sma_50,  # Bullish trend
                        macd > macd_signal  # Bullish momentum
                    ])
                    bear_signals = sum([
                        rsi > 70,  # Overbought
                        sma_20 < sma_50,  # Bearish trend
                        macd < macd_signal  # Bearish momentum
                    ])
                    
                    if bull_signals > bear_signals:
                        self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: {bull_signals} BULLISH | {bear_signals} BEARISH  [BULLISH]\n", ("green",))
                        self.details_text.insert(tk.END, "Recommendation: BULLISH TREND - CONSIDER BUYING\n", ("green_bold",))
                    elif bear_signals > bull_signals:
                        self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: {bull_signals} BULLISH | {bear_signals} BEARISH  [BEARISH]\n", ("red",))
                        self.details_text.insert(tk.END, "Recommendation: BEARISH TREND - CONSIDER SELLING\n", ("red_bold",))
                    else:
                        self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: {bull_signals} BULLISH | {bear_signals} BEARISH  [NEUTRAL]\n", ("normal",))
                        self.details_text.insert(tk.END, "Recommendation: NEUTRAL TREND - WAIT FOR SIGNAL\n", ("normal_bold",))
                else:
                    self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: Insufficient data to calculate\n", ("normal",))
                    self.details_text.insert(tk.END, "Recommendation: Insufficient data - Wait for signal\n", ("normal_bold",))
                
                # Additional insights - only if we have required data
                self.details_text.insert(tk.END, "\n💬 DETAILED ANALYST INSIGHTS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                
                # Generate comprehensive insights based on current data
                insights = []
                if rsi != 0:
                    if rsi < 30:
                        insights.append("RSI indicates strong buying opportunity (oversold territory)")
                    elif rsi > 70:
                        insights.append("RSI indicates strong selling opportunity (overbought territory)")
                    else:
                        rsi_strength = "weak" if abs(rsi - 50) < 10 else "moderate" if abs(rsi - 50) < 20 else "strong"
                        insights.append(f"RSI shows {rsi_strength} momentum toward {'buying' if rsi < 50 else 'selling'}")

                if sma_20 != 0 and sma_50 != 0:
                    if sma_20 > sma_50:
                        insights.append("Short-term trend is bullish with SMA 20 above SMA 50 (Golden Cross possible)")
                    elif sma_20 < sma_50:
                        insights.append("Short-term trend is bearish with SMA 20 below SMA 50 (Death Cross possible)")
                    else:
                        insights.append("Moving averages are aligned, indicating neutral trend")

                if current_price != 0 and bb_middle != 0:
                    if current_price > bb_middle:
                        insights.append("Price above middle Bollinger Band shows positive bias")
                    else:
                        insights.append("Price below middle Bollinger Band shows negative bias")

                if macd != 0 and macd_signal != 0:
                    if macd > macd_signal:
                        insights.append("MACD bullish crossover suggests upward momentum")
                    else:
                        insights.append("MACD bearish crossover suggests downward momentum")

                for insight in insights:
                    self.details_text.insert(tk.END, f"• {insight}\n")
                
                if not insights:
                    self.details_text.insert(tk.END, "• No strong technical signals identified\n")
                
                self.details_text.config(state=tk.DISABLED)
                # Force UI update to ensure the change is visible
                self.details_text.update_idletasks()
                # Scroll to top to ensure content is visible
                self.details_text.yview_moveto(0)
            else:
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, "No data available for this stock.")
                self.details_text.config(state=tk.DISABLED)
                # Force UI update to ensure the change is visible
                self.details_text.update_idletasks()
                # Scroll to top to ensure content is visible
                self.details_text.yview_moveto(0)
        except Exception as e:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Error fetching data: {str(e)}")
            self.details_text.config(state=tk.DISABLED)
            # Force UI update to ensure the change is visible
            self.details_text.update_idletasks()
            # Scroll to top to ensure content is visible
            self.details_text.yview_moveto(0)
            print(f"Error in display_stock_info: {e}")

    def refresh_chart_empty(self):
        """Display empty chart with instructions"""
        try:
            # Clear the chart area and show instructions
            self.ax1.clear()
            if hasattr(self, 'ax2'):
                self.ax2.clear()
            
            # Show instructions on the chart
            self.ax1.text(0.5, 0.5, 'Enter a stock symbol and click "Analyze" to view chart', 
                         horizontalalignment='center', verticalalignment='center',
                         transform=self.ax1.transAxes, fontsize=14, color='#e0e0e0')
            self.ax1.set_title('No Chart Data', color='#e0e0e0', fontsize=12)
            
            # Set background colors
            self.ax1.set_facecolor('#2d2d2d')
            if hasattr(self, 'ax2'):
                self.ax2.set_facecolor('#2d2d2d')
            
            # Update canvas
            self.canvas.draw()
            print("DEBUG: Empty chart displayed")  # Debug print
        except Exception as e:
            print(f"Error in refresh_chart_empty: {e}")
            import traceback
            traceback.print_exc()

    def refresh_chart(self):
        """Refresh the stock chart with current data"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            print(f"DEBUG: refresh_chart called for symbol: '{symbol}'")  # Debug print
            if not symbol or symbol == "":
                print("DEBUG: No symbol in entry field, skipping chart refresh")  # Debug print
                # Optionally, display a message or blank chart when no symbol is entered
                return
            
            # Use the stored current_data if available (from analyze_stock) for consistency
            if hasattr(self, 'current_data') and self.current_data is not None and not self.current_data.empty:
                data = self.current_data
                print(f"DEBUG: Using stored current_data for chart")  # Debug print
            else:
                # Otherwise, fetch data independently
                print(f"DEBUG: No stored data, fetching fresh data for chart")  # Debug print
                # Use the analyzer to get comprehensive historical data
                analyzer = robinhood_market_researcher.MarketAnalyzer()
                data = analyzer.watchlist.get_stock_data(symbol)  # Use the public method to get data
                
                # If that doesn't work, try the API directly
                if data is None or data.empty:
                    print(f"DEBUG: No data from watchlist, trying API")  # Debug print
                    api = robinhood_market_researcher.MarketDataAPI()
                    data = api.get_stock_data(symbol)
                
                # Store for potential future use
                self.current_data = data
            
            print(f"DEBUG: Chart data fetched, type: {type(data)}, length: {len(data) if data is not None else 'None'}")  # Debug print

            if data is not None and not data.empty and len(data) > 1:
                # Filter data based on selected timeframe  
                timeframe = self.timeframe_var.get()
                try:
                    if timeframe == "1W":
                        cutoff = datetime.now() - timedelta(weeks=1)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                    elif timeframe == "1M":
                        cutoff = datetime.now() - timedelta(days=30)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                    elif timeframe == "3M":
                        cutoff = datetime.now() - timedelta(days=90)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                    elif timeframe == "6M":
                        cutoff = datetime.now() - timedelta(days=180)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                    elif timeframe == "1Y":
                        cutoff = datetime.now() - timedelta(days=365)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                    elif timeframe == "2Y":
                        cutoff = datetime.now() - timedelta(days=730)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                    elif timeframe == "5Y":
                        cutoff = datetime.now() - timedelta(days=1825)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle datetime comparison robustly by converting both to timezone-naive
                        try:
                            # Convert data index to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            # Convert cutoff to timezone-naive for safe comparison
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            # Perform comparison with timezone-naive datetimes
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            print(f"DEBUG: Timezone conversion failed, using fallback comparison: {tz_error}")
                            # Ultimate fallback - convert everything to naive for comparison
                            try:
                                if hasattr(data.index, 'tz') and data.index.tz is not None:
                                    data.index = data.index.tz_localize(None).tz_localize(None)
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                                data = data[data.index >= cutoff_ts]
                            except Exception as fallback_error:
                                print(f"DEBUG: Fallback comparison also failed: {fallback_error}")
                                # If all else fails, don't filter the data
                                pass
                except TypeError:
                    # If there's still a datetime comparison issue, fall back to date-only comparison
                    print("DEBUG: Handling timezone comparison issue with fallback method")
                    if timeframe == "1W":
                        cutoff_date = (datetime.now() - timedelta(weeks=1)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "1M":
                        cutoff_date = (datetime.now() - timedelta(days=30)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "3M":
                        cutoff_date = (datetime.now() - timedelta(days=90)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "6M":
                        cutoff_date = (datetime.now() - timedelta(days=180)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "1Y":
                        cutoff_date = (datetime.now() - timedelta(days=365)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "2Y":
                        cutoff_date = (datetime.now() - timedelta(days=730)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "5Y":
                        cutoff_date = (datetime.now() - timedelta(days=1825)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                
                # Clear previous plots
                self.ax1.clear()
                self.ax2.clear()
                
                # Ensure data is properly sorted by date
                data = data.sort_index()
                
                chart_type = self.chart_type_var.get()
                
                if chart_type == "candle":
                    # For candlestick, we need to implement a different approach since we're using simulated data
                    # Just plot the Close price with high/low indicators
                    self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                    if 'High' in data.columns and 'Low' in data.columns:
                        self.ax1.plot(data.index, data['High'], color='#81c784', alpha=0.6, linewidth=0.5, linestyle='--', label='High')
                        self.ax1.plot(data.index, data['Low'], color='#e57373', alpha=0.6, linewidth=0.5, linestyle='--', label='Low')
                elif chart_type == "area":
                    # Plot area chart
                    self.ax1.fill_between(data.index, data['Close'], color='#64b5f6', alpha=0.3)
                    self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                elif chart_type == "volume":
                    # Just plot volume
                    if 'Volume' in data.columns:
                        self.ax1.bar(data.index, data['Volume'], color='#90a4ae', alpha=0.7)
                        self.ax1.set_ylabel('Volume', color='#e0e0e0')
                else:  # Line chart (default)
                    self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                    if 'High' in data.columns and 'Low' in data.columns:
                        self.ax1.plot(data.index, data['High'], label='High', color='#81c784', alpha=0.6, linewidth=0.8)
                        self.ax1.plot(data.index, data['Low'], label='Low', color='#e57373', alpha=0.6, linewidth=0.8)
                
                # Add technical indicators if it's not volume chart
                if chart_type != "volume":
                    # Add moving averages
                    if self.show_sma20_var.get() and 'Close' in data.columns and len(data) >= 20:
                        sma20 = data['Close'].rolling(window=20).mean()
                        self.ax1.plot(data.index, sma20, label='SMA 20', color='#ffb74d', linewidth=1)
                    if self.show_sma50_var.get() and 'Close' in data.columns and len(data) >= 50:
                        sma50 = data['Close'].rolling(window=50).mean()
                        self.ax1.plot(data.index, sma50, label='SMA 50', color='#ba68c8', linewidth=1)
                    
                    # Add Bollinger Bands
                    if self.show_bollinger_var.get() and 'Close' in data.columns and len(data) >= 20:
                        # Calculate Bollinger Bands
                        rolling_mean = data['Close'].rolling(window=20).mean()
                        rolling_std = data['Close'].rolling(window=20).std()
                        bb_upper = rolling_mean + (rolling_std * 2)
                        bb_lower = rolling_mean - (rolling_std * 2)
                        
                        self.ax1.plot(data.index, bb_upper, label='BB Upper', color='#f06292', linestyle='--', linewidth=1)
                        self.ax1.plot(data.index, bb_lower, label='BB Lower', color='#f06292', linestyle='--', linewidth=1)
                        self.ax1.fill_between(data.index, bb_upper, bb_lower, color='#f06292', alpha=0.1)
                
                self.ax1.set_title(f'{symbol} Price Chart [{timeframe}]', color='#e0e0e0', fontsize=12)
                self.ax1.set_ylabel('Price ($)', color='#e0e0e0')
                
                # Only add legend if there are multiple items to show
                lines = self.ax1.get_lines()
                if len(lines) > 0:  # Only show legend if we have plotted lines
                    self.ax1.legend(loc='upper left', facecolor='#2d2d2d', labelcolor='#e0e0e0')
                
                self.ax1.grid(True, color='#444444', linestyle='--', alpha=0.6)
                self.ax1.tick_params(colors='#e0e0e0')
                
                # Plot volume on second subplot if not volume chart type
                if chart_type != "volume" and self.show_volume_var.get():
                    if 'Volume' in data.columns:
                        self.ax2.bar(data.index, data['Volume'], color='#90a4ae', alpha=0.7)
                        self.ax2.set_ylabel('Volume', color='#e0e0e0')
                else:
                    # If volume chart type, we don't need the second subplot
                    pass
                
                # Only set x-label on the bottom subplot if we're showing both
                if chart_type != "volume":
                    self.ax2.set_xlabel('Date', color='#e0e0e0')
                    self.ax2.tick_params(colors='#e0e0e0', labelsize=8)
                    # Format x-axis dates  
                    self.fig.autofmt_xdate()
                else:
                    # If just volume chart, set xlabel on the main plot
                    self.ax1.set_xlabel('Date', color='#e0e0e0')
                    self.ax1.tick_params(colors='#e0e0e0', labelsize=8)
                    self.fig.autofmt_xdate()
                
                # Set background colors
                self.ax1.set_facecolor('#2d2d2d')
                if chart_type != "volume":
                    self.ax2.set_facecolor('#2d2d2d')
                
                # Update canvas
                self.canvas.draw()
                print(f"DEBUG: Chart updated successfully for {symbol}")  # Debug print
            else:
                # Create a simple chart as fallback
                self.ax1.clear()
                if hasattr(self, 'ax2'):
                    self.ax2.clear()

                # Create a simple test chart with fake data to ensure the chart functionality works
                dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                prices = [100 + np.random.normal(0, 2) for _ in range(30)]
                
                self.ax1.plot(dates, prices, label='Price', color='#64b5f6', linewidth=1.5)
                self.ax1.set_title(f'{symbol} - No Data (Test Chart)', color='#e0e0e0', fontsize=12)
                self.ax1.set_ylabel('Price ($)', color='#e0e0e0')
                self.ax1.grid(True, color='#444444', linestyle='--', alpha=0.6)
                self.ax1.tick_params(colors='#e0e0e0')
                
                # Format x-axis dates
                self.fig.autofmt_xdate()
                
                # Set background colors
                self.ax1.set_facecolor('#2d2d2d')
                
                # Update canvas
                self.canvas.draw()
                print(f"DEBUG: Fallback chart created for {symbol}")  # Debug print
            
            if data is not None and not data.empty and len(data) > 1:
                # Filter data based on selected timeframe
                timeframe = self.timeframe_var.get()
                try:
                    if timeframe == "1W":
                        cutoff = datetime.now() - timedelta(weeks=1)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                    elif timeframe == "1M":
                        cutoff = datetime.now() - timedelta(days=30)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                    elif timeframe == "3M":
                        cutoff = datetime.now() - timedelta(days=90)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                    elif timeframe == "6M":
                        cutoff = datetime.now() - timedelta(days=180)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                    elif timeframe == "1Y":
                        cutoff = datetime.now() - timedelta(days=365)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                    elif timeframe == "2Y":
                        cutoff = datetime.now() - timedelta(days=730)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                    elif timeframe == "5Y":
                        cutoff = datetime.now() - timedelta(days=1825)
                        cutoff_ts = pd.Timestamp(cutoff)
                        # Handle timezone-aware comparison properly
                        try:
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                # If data index is timezone-aware, make cutoff timezone-aware too
                                if cutoff_ts.tz is None:
                                    cutoff_ts = cutoff_ts.tz_localize(data.index.tz)
                            elif hasattr(data.index, 'tz') and data.index.tz is None:
                                # If data index is timezone-naive, make sure cutoff is also naive
                                if cutoff_ts.tz is not None:
                                    cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                        except Exception as tz_error:
                            # Fallback to naive comparison if timezone handling fails
                            print(f"DEBUG: Timezone comparison failed, using naive comparison: {tz_error}")
                            # Convert both to timezone-naive for safe comparison
                            if hasattr(data.index, 'tz') and data.index.tz is not None:
                                data.index = data.index.tz_localize(None)
                            if cutoff_ts.tz is not None:
                                cutoff_ts = cutoff_ts.tz_localize(None)
                            data = data[data.index >= cutoff_ts]
                except TypeError:
                    # If there's still a datetime comparison issue, fall back to date-only comparison
                    print("DEBUG: Handling timezone comparison issue with fallback method in second block")
                    if timeframe == "1W":
                        cutoff_date = (datetime.now() - timedelta(weeks=1)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "1M":
                        cutoff_date = (datetime.now() - timedelta(days=30)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "3M":
                        cutoff_date = (datetime.now() - timedelta(days=90)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "6M":
                        cutoff_date = (datetime.now() - timedelta(days=180)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "1Y":
                        cutoff_date = (datetime.now() - timedelta(days=365)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "2Y":
                        cutoff_date = (datetime.now() - timedelta(days=730)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                    elif timeframe == "5Y":
                        cutoff_date = (datetime.now() - timedelta(days=1825)).date()
                        data = data[pd.to_datetime(data.index.date) >= cutoff_date]
                
                # Clear previous plots
                self.ax1.clear()
                self.ax2.clear()
                
                # Ensure data is properly sorted by date
                data = data.sort_index()
                
                chart_type = self.chart_type_var.get()
                
                if chart_type == "candle":
                    # For candlestick, we need to implement a different approach since we're using simulated data
                    # Just plot the Close price with high/low indicators
                    self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                    if 'High' in data.columns and 'Low' in data.columns:
                        self.ax1.plot(data.index, data['High'], color='#81c784', alpha=0.6, linewidth=0.5, linestyle='--', label='High')
                        self.ax1.plot(data.index, data['Low'], color='#e57373', alpha=0.6, linewidth=0.5, linestyle='--', label='Low')
                elif chart_type == "area":
                    # Plot area chart
                    self.ax1.fill_between(data.index, data['Close'], color='#64b5f6', alpha=0.3)
                    self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                elif chart_type == "volume":
                    # Just plot volume
                    if 'Volume' in data.columns:
                        self.ax1.bar(data.index, data['Volume'], color='#90a4ae', alpha=0.7)
                        self.ax1.set_ylabel('Volume', color='#e0e0e0')
                else:  # Line chart (default)
                    self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                    if 'High' in data.columns and 'Low' in data.columns:
                        self.ax1.plot(data.index, data['High'], label='High', color='#81c784', alpha=0.6, linewidth=0.8)
                        self.ax1.plot(data.index, data['Low'], label='Low', color='#e57373', alpha=0.6, linewidth=0.8)
                
                # Add technical indicators if it's not volume chart
                if chart_type != "volume":
                    # Add moving averages
                    if self.show_sma20_var.get() and 'Close' in data.columns and len(data) >= 20:
                        sma20 = data['Close'].rolling(window=20).mean()
                        self.ax1.plot(data.index, sma20, label='SMA 20', color='#ffb74d', linewidth=1)
                    if self.show_sma50_var.get() and 'Close' in data.columns and len(data) >= 50:
                        sma50 = data['Close'].rolling(window=50).mean()
                        self.ax1.plot(data.index, sma50, label='SMA 50', color='#ba68c8', linewidth=1)
                    
                    # Add Bollinger Bands
                    if self.show_bollinger_var.get() and 'Close' in data.columns and len(data) >= 20:
                        # Calculate Bollinger Bands
                        rolling_mean = data['Close'].rolling(window=20).mean()
                        rolling_std = data['Close'].rolling(window=20).std()
                        bb_upper = rolling_mean + (rolling_std * 2)
                        bb_lower = rolling_mean - (rolling_std * 2)
                        
                        self.ax1.plot(data.index, bb_upper, label='BB Upper', color='#f06292', linestyle='--', linewidth=1)
                        self.ax1.plot(data.index, bb_lower, label='BB Lower', color='#f06292', linestyle='--', linewidth=1)
                        self.ax1.fill_between(data.index, bb_upper, bb_lower, color='#f06292', alpha=0.1)
                
                self.ax1.set_title(f'{symbol} Price Chart [{timeframe}]', color='#e0e0e0', fontsize=12)
                self.ax1.set_ylabel('Price ($)', color='#e0e0e0')
                
                # Only add legend if there are multiple items to show
                lines = self.ax1.get_lines()
                if len(lines) > 0:  # Only show legend if we have plotted lines
                    self.ax1.legend(loc='upper left', facecolor='#2d2d2d', labelcolor='#e0e0e0')
                
                self.ax1.grid(True, color='#444444', linestyle='--', alpha=0.6)
                self.ax1.tick_params(colors='#e0e0e0')
                
                # Plot volume on second subplot if not volume chart type
                if chart_type != "volume" and self.show_volume_var.get():
                    if 'Volume' in data.columns:
                        self.ax2.bar(data.index, data['Volume'], color='#90a4ae', alpha=0.7)
                        self.ax2.set_ylabel('Volume', color='#e0e0e0')
                else:
                    # If volume chart type, we don't need the second subplot
                    pass
                
                # Only set x-label on the bottom subplot if we're showing both
                if chart_type != "volume":
                    self.ax2.set_xlabel('Date', color='#e0e0e0')
                    self.ax2.tick_params(colors='#e0e0e0', labelsize=8)
                    # Format x-axis dates  
                    self.fig.autofmt_xdate()
                else:
                    # If just volume chart, set xlabel on the main plot
                    self.ax1.set_xlabel('Date', color='#e0e0e0')
                    self.ax1.tick_params(colors='#e0e0e0', labelsize=8)
                    self.fig.autofmt_xdate()
                
                # Set background colors
                self.ax1.set_facecolor('#2d2d2d')
                if chart_type != "volume":
                    self.ax2.set_facecolor('#2d2d2d')
                
                # Update canvas
                self.canvas.draw()
            else:
                # Create a simple chart as fallback
                self.ax1.clear()
                if hasattr(self, 'ax2'):
                    self.ax2.clear()
                
                # Create a simple test chart with fake data to ensure the chart functionality works
                dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
                prices = [100 + np.random.normal(0, 2) for _ in range(30)]
                
                self.ax1.plot(dates, prices, label='Price', color='#64b5f6', linewidth=1.5)
                self.ax1.set_title(f'{symbol} - No Data (Test Chart)', color='#e0e0e0', fontsize=12)
                self.ax1.set_ylabel('Price ($)', color='#e0e0e0')
                self.ax1.grid(True, color='#444444', linestyle='--', alpha=0.6)
                self.ax1.tick_params(colors='#e0e0e0')
                
                # Format x-axis dates
                self.fig.autofmt_xdate()
                
                # Set background colors
                self.ax1.set_facecolor('#2d2d2d')
                
                # Update canvas
                self.canvas.draw()
                
        except Exception as e:
            print(f"Error in refresh_chart: {e}")
            # Create a simple fallback chart
            self.ax1.clear()
            if hasattr(self, 'ax2'):
                self.ax2.clear()
            
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            prices = [100 + np.random.normal(0, 1) for _ in range(30)]
            
            self.ax1.plot(dates, prices, label='Test Data', color='#64b5f6', linewidth=1.5)
            self.ax1.set_title('Chart Error - Test Display', color='#e0e0e0', fontsize=12)
            self.ax1.set_ylabel('Price ($)', color='#e0e0e0')
            self.ax1.grid(True, color='#444444', linestyle='--', alpha=0.6)
            self.ax1.tick_params(colors='#e0e0e0')
            
            # Format x-axis dates
            self.fig.autofmt_xdate()
            
            # Set background colors
            self.ax1.set_facecolor('#2d2d2d')
            
            # Update canvas
            self.canvas.draw()
            # Commenting out messagebox to prevent pop-ups during testing
            # messagebox.showerror("Chart Error", f"Error refreshing chart: {str(e)}")

    def calculate_percentage_change(self):
        """Calculate percentage change between two prices"""
        try:
            start_price = float(self.start_price_entry.get())
            end_price = float(self.end_price_entry.get())
            
            change = ((end_price - start_price) / start_price) * 100
            change_type = "📈 GAIN" if change >= 0 else "📉 LOSS"
            
            self.percent_result_label.config(
                text=f"{change_type}: {change:.2f}%", 
                fg="#4caf50" if change >= 0 else "#f44336"
            )
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for both prices")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating percentage: {str(e)}")

    def get_options_data(self):
        """Alias for refresh_options_data for backward compatibility"""
        self.refresh_options_data()

    def run_enhanced_ai_analysis(self):
        """Run enhanced AI analysis on the current stock"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            print(f"DEBUG: run_enhanced_ai_analysis called for symbol: {symbol}")  # Debug print
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol")
                return

            # Use existing analysis if available to ensure consistency with display_stock_info
            if self.current_analysis and self.current_analysis.get('symbol', '').upper() == symbol:
                print(f"DEBUG: Using existing current_analysis for {symbol}")  # Debug print
                analysis = self.current_analysis
            else:
                print(f"DEBUG: Getting fresh analysis for {symbol}")  # Debug print
                # Get stock analysis data using the module's function for consistency
                analysis = robinhood_market_researcher.analyze_stock(symbol)
                
                # Update current analysis for other functions to use
                self.current_analysis = analysis
            
            print(f"DEBUG: Analysis result type in AI: {type(analysis)}")  # Debug print
            if analysis:
                print(f"DEBUG: Analysis symbol in AI: {analysis.get('symbol', 'N/A')}")  # Debug print
            
            # Check if ai_text exists before proceeding - more robust check
            if not hasattr(self, 'ai_text') or self.ai_text is None:
                print("ERROR: ai_text attribute not found or is None - UI may not have initialized properly")
                # Try to create ai_text if it doesn't exist (last resort)
                try:
                    # This is a fallback - normally ai_text should be created during init
                    print("Attempting to create ai_text as fallback...")
                    # Check if AI frame exists, if not try to create minimal one
                    if not hasattr(self, 'ai_frame') or self.ai_frame is None:
                        print("AI frame not found, creating minimal AI frame...")
                        # Create a minimal AI frame if it doesn't exist
                        if hasattr(self, 'notebook'):
                            self.ai_frame = tk.Frame(self.notebook, bg="#1e1e1e")
                            self.notebook.add(self.ai_frame, text="🤖 Enhanced AI Insights")
                            print("Created AI frame as fallback")
                        else:
                            print("ERROR: Notebook not found, cannot create AI frame")
                            messagebox.showerror("Error", "UI components not properly initialized - notebook missing")
                            return
                    
                    # Create a new text widget (this is not ideal but as fallback)
                    from tkinter import scrolledtext
                    self.ai_text = scrolledtext.ScrolledText(self.ai_frame, 
                                                            bg="#2d2d2d", fg="#e0e0e0",
                                                            font=("Consolas", 10),
                                                            relief=tk.FLAT,
                                                            insertbackground="#e0e0e0")
                    self.ai_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
                    
                    # Configure tags for AI insights
                    self.ai_text.tag_configure("ai_header", font=("Arial", 12, "bold"), foreground="#FFD54F")
                    self.ai_text.tag_configure("ai_recommendation", font=("Arial", 11, "bold"), foreground="#81C784")
                    self.ai_text.tag_configure("ai_warning", font=("Arial", 10, "bold"), foreground="#E57373")
                    self.ai_text.tag_configure("ai_neutral", font=("Arial", 10), foreground="#64B5F6")
                    self.ai_text.tag_configure("ai_signal", font=("Arial", 10, "bold"), foreground="#FFB74D")
                    self.ai_text.tag_configure("ai_buy", font=("Arial", 10, "bold"), foreground="#AED581")
                    self.ai_text.tag_configure("ai_sell", font=("Arial", 10, "bold"), foreground="#FF8A65")
                    self.ai_text.tag_configure("ai_strong", font=("Arial", 10, "bold"), foreground="#FFF176")
                    
                    print("Successfully created ai_text as fallback")
                except Exception as fallback_error:
                    error_msg = f"ERROR: Could not create ai_text fallback: {fallback_error}"
                    print(error_msg)
                    messagebox.showerror("Error", f"AI Analysis component not properly initialized: {str(fallback_error)}")
                    return
            
            if analysis:
                # Clear the AI text area
                print(f"DEBUG: Clearing AI text area")  # Debug print
                # Additional check to make sure ai_text is valid
                if not hasattr(self, 'ai_text') or self.ai_text is None:
                    print("ERROR: ai_text still not available after fallback attempts")
                    messagebox.showerror("Error", "AI Analysis component could not be initialized")
                    return
                    
                try:
                    self.ai_text.config(state=tk.NORMAL)
                    self.ai_text.delete(1.0, tk.END)
                except Exception as config_error:
                    print(f"ERROR configuring ai_text: {config_error}")
                    # Try to recreate ai_text
                    try:
                        from tkinter import scrolledtext
                        self.ai_text = scrolledtext.ScrolledText(self.ai_frame, 
                                                                bg="#2d2d2d", fg="#e0e0e0",
                                                                font=("Consolas", 10),
                                                                relief=tk.FLAT,
                                                                insertbackground="#e0e0e0")
                        self.ai_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
                        self.ai_text.config(state=tk.NORMAL)
                        self.ai_text.delete(1.0, tk.END)
                        print("Recreated ai_text successfully")
                    except Exception as recreate_error:
                        print(f"ERROR recreating ai_text: {recreate_error}")
                        messagebox.showerror("Error", f"Could not initialize AI text area: {str(recreate_error)}")
                        return
                
                # Generate enhanced AI insights
                print(f"DEBUG: Generating enhanced AI insights")  # Debug print
                ai_insights = self.generate_advanced_ai_insights(symbol, analysis)
                
                # Display enhanced AI insights
                print(f"DEBUG: Inserting AI insights to text area")  # Debug print
                self.ai_text.insert(tk.END, ai_insights, ("ai_neutral",))
                
                # Disable text area to prevent editing
                self.ai_text.config(state=tk.DISABLED)
                # Force UI update to ensure the change is visible
                self.ai_text.update_idletasks()
                print(f"DEBUG: AI analysis completed and displayed for {symbol}")  # Debug print
            else:
                print(f"DEBUG: No analysis data for {symbol} in AI")  # Debug print
                self.ai_text.config(state=tk.NORMAL)
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, f"No data available for {symbol}.", ("ai_warning",))
                self.ai_text.config(state=tk.DISABLED)
                
        except Exception as e:
            # Check if ai_text exists in the exception handler as well
            if hasattr(self, 'ai_text') and self.ai_text.winfo_exists():
                self.ai_text.config(state=tk.NORMAL)
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, f"Error running AI analysis: {str(e)}", ("ai_warning",))
                self.ai_text.config(state=tk.DISABLED)
            else:
                print(f"ERROR in run_enhanced_ai_analysis: Cannot display error in GUI, ai_text not available or destroyed - {str(e)}")
                # Show error in message box instead
                messagebox.showerror("AI Analysis Error", f"Error running AI analysis: {str(e)}")
            print(f"Error in run_enhanced_ai_analysis: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_ml_predictions(self, symbol, analysis):
        """
        Generate machine learning predictions for price movement and market conditions.
        This is a simplified implementation that mimics ML behavior using advanced statistical methods.
        In a production environment, this would connect to actual trained ML models.
        """
        try:
            # Extract key features for prediction
            indicators = analysis.get('indicators', {})
            current_price = analysis.get('current_price', 0)
            prev_close = analysis.get('prev_close', 0)
            volume = analysis.get('volume', 0)
            
            # Technical indicators
            rsi = indicators.get('rsi', 0)
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            bb_middle = indicators.get('bb_middle', 0)
            stochastic_k = indicators.get('stochastic_k', 0)
            stochastic_d = indicators.get('stochastic_d', 0)
            adx = indicators.get('adx', 0)
            
            # Calculate derived features
            price_change = ((current_price - prev_close) / prev_close * 100) if prev_close and prev_close != 0 else 0
            ma_ratio = (sma_20 / sma_50) if sma_20 != 0 and sma_50 != 0 else 1
            rsi_normalized = rsi / 100 if rsi != 0 else 0.5
            macd_histogram = macd - macd_signal if macd != 0 and macd_signal != 0 else 0
            bb_position = ((current_price - bb_lower) / (bb_upper - bb_lower)) if (bb_upper - bb_lower) != 0 and bb_upper != 0 and bb_lower != 0 else 0.5
            stochastic_spread = abs(stochastic_k - stochastic_d) if stochastic_k != 0 and stochastic_d != 0 else 0
            adx_strength = adx / 100 if adx != 0 else 0
            
            # Ensemble predictions using weighted voting
            predictions = {}
            
            # 1. Short-term Direction Prediction (Next 1-3 days)
            short_term_features = [rsi_normalized, ma_ratio, bb_position, macd_histogram, adx_strength]
            short_term_pred, short_term_conf = self.predict_direction(short_term_features)
            predictions['Short-term Direction'] = {
                'prediction': short_term_pred,
                'confidence': short_term_conf,
                'timeframe': '1-3 days'
            }
            
            # 2. Medium-term Momentum Prediction (Next 1-2 weeks)
            medium_term_features = [rsi_normalized, ma_ratio, adx_strength, price_change/100, stochastic_spread/100]
            medium_term_pred, medium_term_conf = self.predict_momentum(medium_term_features)
            predictions['Medium-term Momentum'] = {
                'prediction': medium_term_pred,
                'confidence': medium_term_conf,
                'timeframe': '1-2 weeks'
            }
            
            # 3. Volatility Prediction
            vol_features = [bb_position, adx_strength, price_change/100, rsi_normalized]
            vol_pred, vol_conf = self.predict_volatility(vol_features)
            predictions['Volatility Outlook'] = {
                'prediction': vol_pred,
                'confidence': vol_conf,
                'timeframe': 'next week'
            }
            
            # 4. Support/Resistance Level Prediction
            sr_features = [bb_lower, bb_upper, sma_20, sma_50, current_price]
            sr_pred, sr_conf = self.predict_support_resistance(sr_features)
            predictions['Key Levels'] = {
                'prediction': sr_pred,
                'confidence': sr_conf,
                'timeframe': 'near-term'
            }
            
            # 5. Pattern Recognition Prediction
            pattern_features = [rsi, stochastic_k, stochastic_d, macd, bb_position, price_change]
            pattern_pred, pattern_conf = self.recognize_patterns(pattern_features)
            predictions['Pattern Recognition'] = {
                'prediction': pattern_pred,
                'confidence': pattern_conf,
                'timeframe': 'immediate'
            }
            
            return predictions
            
        except Exception as e:
            print(f"Error in ML predictions: {e}")
            return {
                'ML Status': 'Simplified predictions due to processing limitations',
                'Fallback': 'Using rule-based technical analysis instead'
            }
    
    def predict_direction(self, features):
        """Predict short-term price direction using ensemble methods"""
        try:
            # Normalize features
            normalized_features = [(f - min(0, f)) / (max(1, f) - min(0, f)) if f != 0 else 0.5 for f in features]
            
            # Weighted ensemble of different predictors
            rsi_signal = 1 if features[0] < 0.3 else (-1 if features[0] > 0.7 else 0)  # RSI component
            ma_signal = 1 if features[1] > 1.01 else (-1 if features[1] < 0.99 else 0)  # MA component
            bb_signal = 1 if features[2] < 0.2 else (-1 if features[2] > 0.8 else 0)  # BB component
            macd_signal = 1 if features[3] > 0 else (-1 if features[3] < 0 else 0)  # MACD component
            adx_signal = 1 if features[4] > 0.25 else 0  # ADX strength component
            
            # Ensemble voting with weights
            weighted_sum = (rsi_signal * 0.25 + 
                          ma_signal * 0.25 + 
                          bb_signal * 0.20 + 
                          macd_signal * 0.20 + 
                          adx_signal * 0.10)
            
            # Determine prediction and confidence
            if weighted_sum > 0.1:
                prediction = "Bullish"
                confidence = min(100, abs(weighted_sum) * 150)  # Scale confidence
            elif weighted_sum < -0.1:
                prediction = "Bearish"
                confidence = min(100, abs(weighted_sum) * 150)
            else:
                prediction = "Neutral"
                confidence = max(30, 100 - abs(weighted_sum) * 200)
            
            return prediction, confidence
            
        except Exception as e:
            return "Neutral", 50.0
    
    def predict_momentum(self, features):
        """Predict medium-term momentum using technical convergence"""
        try:
            # Feature engineering for momentum prediction
            rsi_component = features[0]  # Normalized RSI
            ma_component = features[1]  # MA ratio
            adx_component = features[2]   # ADX strength
            price_component = features[3]  # Price change
            stoch_component = features[4]  # Stochastic spread
            
            # Momentum score calculation
            momentum_score = (rsi_component * 0.2 + 
                            ma_component * 0.3 + 
                            adx_component * 0.2 + 
                            price_component * 0.2 + 
                            stoch_component * 0.1)
            
            # Determine momentum direction and strength
            if momentum_score > 0.1:
                prediction = "Strong Positive Momentum"
                confidence = min(100, momentum_score * 200)
            elif momentum_score > 0.02:
                prediction = "Positive Momentum"
                confidence = min(100, momentum_score * 100 + 50)
            elif momentum_score < -0.1:
                prediction = "Strong Negative Momentum"
                confidence = min(100, abs(momentum_score) * 200)
            elif momentum_score < -0.02:
                prediction = "Negative Momentum"
                confidence = min(100, abs(momentum_score) * 100 + 50)
            else:
                prediction = "Sideways Momentum"
                confidence = max(40, 100 - abs(momentum_score) * 500)
            
            return prediction, confidence
            
        except Exception as e:
            return "Neutral Momentum", 50.0
    
    def predict_volatility(self, features):
        """Predict volatility using BB width and ADX"""
        try:
            bb_position = features[0]  # BB position
            adx_strength = features[1]  # ADX strength
            price_change = features[2]   # Normalized price change
            rsi_level = features[3]      # Normalized RSI
            
            # Volatility prediction algorithm
            bb_width_implication = abs(bb_position - 0.5) * 2  # 0 to 1 scale
            adx_implication = adx_strength * 2  # Scale ADX
            price_implication = abs(price_change) * 5  # Scale price change
            rsi_implication = abs(rsi_level - 0.5) * 2  # Extreme RSI implications
            
            # Combined volatility score
            vol_score = (bb_width_implication * 0.3 + 
                        adx_implication * 0.3 + 
                        price_implication * 0.2 + 
                        rsi_implication * 0.2)
            
            # Determine volatility prediction
            if vol_score > 0.6:
                prediction = "High Volatility Expected"
                confidence = min(100, vol_score * 150)
            elif vol_score > 0.3:
                prediction = "Moderate Volatility Expected"
                confidence = min(100, vol_score * 100 + 40)
            else:
                prediction = "Low Volatility Expected"
                confidence = min(100, (1 - vol_score) * 100 + 30)
            
            return prediction, confidence
            
        except Exception as e:
            return "Moderate Volatility", 60.0
    
    def predict_support_resistance(self, features):
        """Predict key support/resistance levels using technical analysis"""
        try:
            bb_lower = features[0]
            bb_upper = features[1]
            sma_20 = features[2]
            sma_50 = features[3]
            current_price = features[4]
            
            # Generate support/resistance levels
            support_levels = []
            resistance_levels = []
            
            # Bollinger Band levels
            if bb_lower != 0:
                support_levels.append(round(bb_lower, 2))
            if bb_upper != 0:
                resistance_levels.append(round(bb_upper, 2))
            
            # Moving average levels
            if sma_20 != 0:
                support_levels.append(round(sma_20, 2))
            if sma_50 != 0:
                support_levels.append(round(sma_50, 2))
            
            # Round numbers and psychological levels
            if current_price != 0:
                round_number = round(current_price / 5) * 5
                support_levels.append(round(round_number * 0.98, 2))  # 2% below round number
                resistance_levels.append(round(round_number * 1.02, 2))  # 2% above round number
            
            # Sort and deduplicate levels
            support_levels = sorted(list(set(support_levels)))[:3]  # Top 3 support levels
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:3]  # Top 3 resistance levels
            
            # Create prediction string
            support_str = ", ".join([f"${lvl}" for lvl in support_levels]) if support_levels else "N/A"
            resistance_str = ", ".join([f"${lvl}" for lvl in resistance_levels]) if resistance_levels else "N/A"
            
            prediction = f"Support: {support_str} | Resistance: {resistance_str}"
            confidence = min(100, 70 + len(support_levels) * 5 + len(resistance_levels) * 5)
            
            return prediction, confidence
            
        except Exception as e:
            return "Support/Resistance: Unable to calculate", 40.0
    
    def recognize_patterns(self, features):
        """Recognize technical patterns using feature combinations"""
        try:
            rsi = features[0]
            stoch_k = features[1]
            stoch_d = features[2]
            macd = features[3]
            bb_position = features[4]
            price_change = features[5]
            
            patterns = []
            
            # RSI Divergence patterns
            if rsi < 30 and price_change > 2:
                patterns.append("Bullish RSI Divergence")
            elif rsi > 70 and price_change < -2:
                patterns.append("Bearish RSI Divergence")
            
            # Stochastic patterns
            if stoch_k < 20 and stoch_d < 20:
                patterns.append("Stochastic Oversold")
            elif stoch_k > 80 and stoch_d > 80:
                patterns.append("Stochastic Overbought")
            
            # MACD patterns
            if macd > 0 and abs(macd) < 0.1:
                patterns.append("MACD Near Zero Line")
            elif macd < 0 and abs(macd) > 0.5:
                patterns.append("Strong Bearish MACD")
            
            # Bollinger Band patterns
            if bb_position < 0.1:
                patterns.append("Price Near Lower BB")
            elif bb_position > 0.9:
                patterns.append("Price Near Upper BB")
            
            # Consolidation patterns
            if abs(price_change) < 1 and 30 <= rsi <= 70:
                patterns.append("Market Consolidation")
            
            if patterns:
                prediction = ", ".join(patterns[:3])  # Limit to top 3 patterns
                confidence = min(100, len(patterns) * 25 + 25)
            else:
                prediction = "No Clear Patterns Detected"
                confidence = 40.0
            
            return prediction, confidence
            
        except Exception as e:
            return "Pattern Recognition Unavailable", 30.0

    def generate_price_predictions(self, symbol, analysis, ml_predictions):
        """Generate detailed price predictions using ensemble methods"""
        predictions = []
        
        try:
            current_price = analysis.get('current_price', 0)
            indicators = analysis.get('indicators', {})
            rsi = indicators.get('rsi', 0)
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            
            if current_price == 0:
                return ["⚠️ Price prediction unavailable - no current price data"]
            
            # Ensemble prediction combining multiple methods
            ensemble_predictions = []
            
            # 1. Mean reversion prediction (based on RSI and Bollinger Bands)
            if rsi != 0 and bb_upper != 0 and bb_lower != 0:
                bb_mid = (bb_upper + bb_lower) / 2
                if rsi < 30:  # Oversold
                    mr_target = bb_mid + (bb_upper - bb_mid) * 0.3  # Target middle of bands
                    ensemble_predictions.append(("Mean Reversion", mr_target, 0.25))
                elif rsi > 70:  # Overbought
                    mr_target = bb_mid - (bb_mid - bb_lower) * 0.3  # Target middle of bands
                    ensemble_predictions.append(("Mean Reversion", mr_target, 0.25))
            
            # 2. Trend following prediction (based on moving averages)
            if sma_20 != 0 and sma_50 != 0:
                if current_price > sma_20 > sma_50:  # Bullish trend
                    tf_target = current_price * 1.03  # 3% trend continuation
                    ensemble_predictions.append(("Trend Following", tf_target, 0.35))
                elif current_price < sma_20 < sma_50:  # Bearish trend
                    tf_target = current_price * 0.97  # 3% trend continuation
                    ensemble_predictions.append(("Trend Following", tf_target, 0.35))
            
            # 3. Momentum prediction (based on MACD)
            if macd != 0 and macd_signal != 0:
                momentum_strength = (macd - macd_signal) / max(abs(macd), 0.001)
                if momentum_strength > 0:  # Positive momentum
                    mom_target = current_price * (1 + min(0.05, momentum_strength * 0.1))
                    ensemble_predictions.append(("Momentum", mom_target, 0.2))
                elif momentum_strength < 0:  # Negative momentum
                    mom_target = current_price * (1 + max(-0.05, momentum_strength * 0.1))
                    ensemble_predictions.append(("Momentum", mom_target, 0.2))
            
            # 4. ML-enhanced prediction (if available)
            if ml_predictions and isinstance(ml_predictions, dict):
                for pred_name, pred_data in ml_predictions.items():
                    if "Direction" in pred_name and isinstance(pred_data, dict):
                        pred_val = pred_data.get('prediction', '')
                        conf = pred_data.get('confidence', 50) / 100
                        if "Bullish" in pred_val:
                            ml_target = current_price * (1 + 0.02 * conf)
                            ensemble_predictions.append(("ML Prediction", ml_target, 0.2 * conf))
                        elif "Bearish" in pred_val:
                            ml_target = current_price * (1 - 0.02 * conf)
                            ensemble_predictions.append(("ML Prediction", ml_target, 0.2 * conf))
            
            # Calculate weighted average prediction
            if ensemble_predictions:
                weighted_sum = sum(target * weight for _, target, weight in ensemble_predictions)
                total_weight = sum(weight for _, _, weight in ensemble_predictions)
                ensemble_target = weighted_sum / total_weight if total_weight != 0 else current_price
                
                # Calculate confidence based on agreement among predictors
                agreement_score = len(ensemble_predictions) / 4.0  # Max 4 predictors
                avg_confidence = sum(weight for _, _, weight in ensemble_predictions) / len(ensemble_predictions) if ensemble_predictions else 0.5
                
                # Generate prediction strings with timeframes
                predictions.append(f"🎯 24-Hour Target: ${ensemble_target:.2f} ({((ensemble_target-current_price)/current_price)*100:+.2f}%)")
                predictions.append(f"📅 1-Week Target: ${current_price * (1 + ((ensemble_target-current_price)/current_price) * 3):.2f} ({((ensemble_target-current_price)/current_price)*300:+.1f}%)")
                predictions.append(f"📊 Confidence: {min(100, int(agreement_score * 50 + avg_confidence * 50))}% based on {len(ensemble_predictions)} models")
                
                # Add individual model insights
                predictions.append("   Individual Model Predictions:")
                for model_name, target, weight in ensemble_predictions[:3]:  # Top 3 models
                    model_change = ((target - current_price) / current_price) * 100
                    predictions.append(f"      • {model_name}: ${target:.2f} ({model_change:+.2f}%)")
            else:
                predictions.append("⚠️ No predictive models available for current market conditions")
                
        except Exception as e:
            predictions.append(f"⚠️ Price prediction error: {str(e)}")
            
        return predictions

    def generate_risk_forecasts(self, symbol, analysis, ml_predictions):
        """Generate enhanced risk forecasts using multiple risk models"""
        forecasts = []
        
        try:
            indicators = analysis.get('indicators', {})
            risk_metrics = analysis.get('risk_metrics', {})
            current_price = analysis.get('current_price', 0)
            volume = analysis.get('volume', 0)
            volatility = risk_metrics.get('volatility', 0)
            beta = risk_metrics.get('beta', 1.0)
            sharpe_ratio = risk_metrics.get('sharpe_ratio', 0)
            
            # 1. Volatility-based risk assessment
            if volatility != 0:
                if volatility < 0.015:
                    vol_risk = "🟢 Very Low"
                    vol_desc = "stable market conditions"
                elif volatility < 0.03:
                    vol_risk = "🟡 Low"
                    vol_desc = "moderate market conditions"
                elif volatility < 0.06:
                    vol_risk = "🟠 Moderate"
                    vol_desc = "increased market uncertainty"
                else:
                    vol_risk = "🔴 High"
                    vol_desc = "significant market turbulence"
                forecasts.append(f"🛡️ Volatility Risk: {vol_risk} ({volatility:.4f} - {vol_desc})")
            
            # 2. Beta-based market risk
            if beta != 0:
                if beta < 0.8:
                    beta_risk = "🟢 Low"
                    beta_desc = "defensive characteristics"
                elif beta < 1.2:
                    beta_risk = "🟡 Moderate"
                    beta_desc = "market-correlated movement"
                else:
                    beta_risk = "🔴 High"
                    beta_desc = "aggressive market sensitivity"
                forecasts.append(f"📈 Market Risk: {beta_risk} (Beta: {beta:.2f} - {beta_desc})")
            
            # 3. Volume-based liquidity risk
            if volume != 0:
                if volume > 1000000:
                    vol_risk = "🟢 Low"
                    vol_desc = "excellent liquidity"
                elif volume > 100000:
                    vol_risk = "🟡 Moderate"
                    vol_desc = "adequate liquidity"
                else:
                    vol_risk = "🟠 High"
                    vol_desc = "limited liquidity - wider spreads possible"
                forecasts.append(f"💧 Liquidity Risk: {vol_risk} ({volume:,} volume - {vol_desc})")
            
            # 4. Sharpe ratio-based efficiency risk
            if sharpe_ratio != 0:
                if sharpe_ratio > 2:
                    sharpe_risk = "🟢 Excellent"
                    sharpe_desc = "superior risk-adjusted returns"
                elif sharpe_ratio > 1:
                    sharpe_risk = "🟡 Good"
                    sharpe_desc = "decent risk-adjusted performance"
                elif sharpe_ratio > 0:
                    sharpe_risk = "🟠 Fair"
                    sharpe_desc = "moderate risk-adjusted returns"
                else:
                    sharpe_risk = "🔴 Poor"
                    sharpe_desc = "negative risk-adjusted performance"
                forecasts.append(f"💎 Efficiency: {sharpe_risk} (Sharpe: {sharpe_ratio:.2f} - {sharpe_desc})")
            
            # 5. ML-enhanced risk forecast (if available)
            if ml_predictions and isinstance(ml_predictions, dict):
                for pred_name, pred_data in ml_predictions.items():
                    if "Volatility" in pred_name and isinstance(pred_data, dict):
                        vol_prediction = pred_data.get('prediction', '')
                        vol_confidence = pred_data.get('confidence', 50)
                        forecasts.append(f"🧠 ML Volatility Forecast: {vol_prediction} ({vol_confidence:.1f}% confidence)")
            
            # Add consolidated risk rating
            risk_indicators = [line for line in forecasts if "Risk:" in line or "Volatility" in line]
            if risk_indicators:
                high_risks = len([r for r in risk_indicators if "🔴" in r or "High" in r])
                moderate_risks = len([r for r in risk_indicators if "🟠" in r or "Moderate" in r])
                
                if high_risks > 1:
                    overall_risk = "🔴 HIGH OVERALL RISK"
                elif high_risks == 1 or moderate_risks > 2:
                    overall_risk = "🟠 MODERATE OVERALL RISK"
                else:
                    overall_risk = "🟢 LOW OVERALL RISK"
                
                forecasts.append(f"⚖️ Overall Risk Assessment: {overall_risk}")
                
        except Exception as e:
            forecasts.append(f"⚠️ Risk forecast error: {str(e)}")
            
        return forecasts

    def scan_trading_opportunities(self, symbol, analysis, ml_predictions):
        """Scan for high-probability trading opportunities using ensemble methods"""
        opportunities = []
        
        try:
            current_price = analysis.get('current_price', 0)
            indicators = analysis.get('indicators', {})
            rsi = indicators.get('rsi', 0)
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            bb_middle = indicators.get('bb_middle', 0)
            stochastic_k = indicators.get('stochastic_k', 0)
            stochastic_d = indicators.get('stochastic_d', 0)
            
            if current_price == 0:
                return ["⚠️ Opportunity scan unavailable - no price data"]
            
            # 1. Mean reversion opportunities
            if rsi != 0 and bb_lower != 0 and bb_upper != 0:
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                
                # Oversold bounces
                if rsi < 25 and bb_position < 0.2:
                    target = bb_middle if bb_middle != 0 else current_price * 1.03
                    risk_reward = (target - current_price) / (current_price - bb_lower) if bb_lower != 0 else 2.0
                    opportunities.append(f"📉 MEAN REVERSION: Buy ${current_price:.2f}, Target ${target:.2f} (RR: {risk_reward:.1f}:1)")
                
                # Overbought pullbacks
                elif rsi > 75 and bb_position > 0.8:
                    target = bb_middle if bb_middle != 0 else current_price * 0.97
                    risk_reward = (bb_upper - current_price) / (current_price - target) if target != 0 else 2.0
                    opportunities.append(f"📈 MEAN REVERSION: Short ${current_price:.2f}, Target ${target:.2f} (RR: {risk_reward:.1f}:1)")
            
            # 2. Breakout opportunities
            if sma_20 != 0 and sma_50 != 0 and bb_upper != 0 and bb_lower != 0:
                # Bullish breakout setup
                if current_price > sma_20 > sma_50 and current_price > bb_middle:
                    resistance = bb_upper
                    if resistance > current_price:
                        upside_potential = (resistance - current_price) / current_price * 100
                        opportunities.append(f"🚀 BULLISH BREAKOUT: Buy above ${current_price:.2f}, Target ${resistance:.2f} (+{upside_potential:.1f}%)")
                
                # Bearish breakdown setup
                elif current_price < sma_20 < sma_50 and current_price < bb_middle:
                    support = bb_lower
                    if support < current_price:
                        downside_potential = (current_price - support) / current_price * 100
                        opportunities.append(f"💣 BEARISH BREAKDOWN: Short below ${current_price:.2f}, Target ${support:.2f} (-{downside_potential:.1f}%)")
            
            # 3. Momentum continuation opportunities
            if macd != 0 and macd_signal != 0:
                # Strong bullish momentum
                if macd > macd_signal and macd > 0:
                    momentum_target = current_price * 1.02
                    opportunities.append(f"⚡ MOMENTUM LONG: Hold/Buy ${current_price:.2f}, Target ${momentum_target:.2f} (+2.0%)")
                
                # Strong bearish momentum
                elif macd < macd_signal and macd < 0:
                    momentum_target = current_price * 0.98
                    opportunities.append(f"⚡ MOMENTUM SHORT: Hold/Sell ${current_price:.2f}, Target ${momentum_target:.2f} (-2.0%)")
            
            # 4. Stochastic crossover opportunities
            if stochastic_k != 0 and stochastic_d != 0:
                # Bullish stochastic crossover
                if stochastic_k < 20 and stochastic_d < 20 and stochastic_k > stochastic_d:
                    target = current_price * 1.025
                    opportunities.append(f"💎 STOCHASTIC BUY: Buy ${current_price:.2f}, Target ${target:.2f} (+2.5%)")
                
                # Bearish stochastic crossover
                elif stochastic_k > 80 and stochastic_d > 80 and stochastic_k < stochastic_d:
                    target = current_price * 0.975
                    opportunities.append(f"💎 STOCHASTIC SELL: Sell ${current_price:.2f}, Target ${target:.2f} (-2.5%)")
            
            # 5. ML-enhanced opportunities
            if ml_predictions and isinstance(ml_predictions, dict):
                for pred_name, pred_data in ml_predictions.items():
                    if "Opportunity" in pred_name or "Pattern" in pred_name:
                        if isinstance(pred_data, dict):
                            pred_val = pred_data.get('prediction', '')
                            conf = pred_data.get('confidence', 0)
                            if conf > 60:  # Only high-confidence opportunities
                                opportunities.append(f"🤖 ML OPPORTUNITY: {pred_val} ({conf:.1f}% confidence)")
                        else:
                            opportunities.append(f"🤖 ML FINDING: {pred_data}")
            
            # Rank opportunities by potential profitability and probability
            ranked_opportunities = self.rank_trading_opportunities(opportunities, analysis)
            
        except Exception as e:
            opportunities.append(f"⚠️ Opportunity scan error: {str(e)}")
            ranked_opportunities = opportunities
            
        return ranked_opportunities

    def rank_trading_opportunities(self, opportunities, analysis):
        """Rank trading opportunities by attractiveness"""
        try:
            # For now, return opportunities as-is with priority labeling
            ranked = []
            for i, opp in enumerate(opportunities):
                if "BREAKOUT" in opp or "MOMENTUM" in opp:
                    ranked.append(f"🥇 {opp}")  # High priority
                elif "MEAN REVERSION" in opp or "STOCHASTIC" in opp:
                    ranked.append(f"🥈 {opp}")  # Medium priority
                elif "ML" in opp:
                    ranked.append(f"🥉 {opp}")  # ML-based (priority depends on confidence)
                else:
                    ranked.append(f"⚪ {opp}")  # Standard priority
            
            return ranked
        except:
            return opportunities

    def forecast_market_regime(self, symbol, analysis, ml_predictions):
        """Forecast market regime using multiple indicators"""
        regimes = []
        
        try:
            indicators = analysis.get('indicators', {})
            risk_metrics = analysis.get('risk_metrics', {})
            rsi = indicators.get('rsi', 0)
            adx = indicators.get('adx', 0)
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            volatility = risk_metrics.get('volatility', 0)
            
            # 1. Trend regime classification
            if adx != 0:
                if adx > 25:
                    if sma_20 != 0 and sma_50 != 0 and sma_20 > sma_50:
                        regimes.append("📈 Strong Bullish Trend")
                    elif sma_20 != 0 and sma_50 != 0 and sma_20 < sma_50:
                        regimes.append("📉 Strong Bearish Trend")
                    else:
                        regimes.append("🧭 Strong Unidirectional Trend")
                elif adx > 20:
                    regimes.append("➡️ Moderate Trend")
                else:
                    regimes.append("🔄 Range-Bound Market")
            
            # 2. Momentum regime
            if rsi != 0:
                if rsi > 70:
                    regimes.append("🚀 High Momentum (Overbought)")
                elif rsi < 30:
                    regimes.append("📉 High Momentum (Oversold)")
                else:
                    regimes.append("⚖️ Balanced Momentum")
            
            # 3. Volatility regime
            if volatility != 0:
                if volatility > 0.06:
                    regimes.append("🌪️ High Volatility Environment")
                elif volatility > 0.03:
                    regimes.append("💨 Moderate Volatility")
                else:
                    regimes.append("🌫️ Low Volatility Environment")
            
            # 4. ML-enhanced regime forecast
            if ml_predictions and isinstance(ml_predictions, dict):
                for pred_name, pred_data in ml_predictions.items():
                    if "Regime" in pred_name or "Context" in pred_name:
                        if isinstance(pred_data, dict):
                            regimes.append(f"🤖 ML Forecast: {pred_data.get('prediction', '')} ({pred_data.get('confidence', 0):.1f}% confidence)")
                        else:
                            regimes.append(f"🤖 ML Insight: {pred_data}")
            
            # Add strategic implications
            if regimes:
                regimes.append("")
                regimes.append("📋 STRATEGIC IMPLICATIONS:")
                
                # Based on identified regimes, suggest appropriate strategies
                if any("Trend" in r for r in regimes):
                    regimes.append("   • Trend-following strategies recommended")
                if any("Range" in r for r in regimes):
                    regimes.append("   • Range-trading strategies appropriate")
                if any("High Volatility" in r for r in regimes):
                    regimes.append("   • Volatility-based strategies favored")
                if any("Momentum" in r for r in regimes):
                    regimes.append("   • Momentum trading opportunities present")
            
        except Exception as e:
            regimes.append(f"⚠️ Regime forecast error: {str(e)}")
            
        return regimes
        """Generate enhanced AI insights with advanced algorithms and comprehensive market analysis"""
        # First, let's add machine learning predictive analytics
        ml_predictions = self.generate_ml_predictions(symbol, analysis)
        
        insights = [f"🤖 ADVANCED AI INSIGHTS FOR {symbol}", "="*60]
        
        # Add ML predictions to insights
        if ml_predictions:
            insights.append("\n🧠 MACHINE LEARNING PREDICTIONS:")
            for pred_name, pred_value in ml_predictions.items():
                if isinstance(pred_value, dict):
                    insights.append(f"   • {pred_name}: {pred_value.get('prediction', 'N/A')} ({pred_value.get('confidence', 0):.1f}% confidence)")
                else:
                    insights.append(f"   • {pred_name}: {pred_value}")
        
        # Add predictive analytics section
        insights.append(f"\n🔮 PREDICTIVE ANALYTICS:")
        
        # Enhanced price predictions using ML models
        price_predictions = self.generate_price_predictions(symbol, analysis, ml_predictions)
        for pred_line in price_predictions:
            insights.append(f"   {pred_line}")
        
        # Enhanced risk forecasts
        risk_forecasts = self.generate_risk_forecasts(symbol, analysis, ml_predictions)
        for risk_line in risk_forecasts:
            insights.append(f"   {risk_line}")
        
        # Enhanced opportunity scanning
        opportunities = self.scan_trading_opportunities(symbol, analysis, ml_predictions)
        if opportunities:
            insights.append(f"\n💎 TRADING OPPORTUNITIES:")
            for opp_line in opportunities[:5]:  # Limit to top 5 opportunities
                insights.append(f"   {opp_line}")
        
        # Enhanced market regime forecasting
        regime_forecast = self.forecast_market_regime(symbol, analysis, ml_predictions)
        if regime_forecast:
            insights.append(f"\n🌐 MARKET REGIME FORECAST:")
            for regime_line in regime_forecast:
                insights.append(f"   {regime_line}")
        
        # Safely extract values with defaults
        indicators = analysis.get('indicators', {})
        rsi = indicators.get('rsi', 0)
        sma_20 = indicators.get('sma_20', 0)
        sma_50 = indicators.get('sma_50', 0)
        current_price = analysis.get('current_price', 0)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        volatility = analysis.get('risk_metrics', {}).get('volatility', 0)
        volume = analysis.get('volume', 0)
        prev_close = analysis.get('prev_close', 0)
        
        # Extract additional indicators for advanced analysis
        ema_12 = indicators.get('ema_12', 0)
        ema_26 = indicators.get('ema_26', 0)
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        bb_middle = indicators.get('bb_middle', 0)
        stochastic_k = indicators.get('stochastic_k', 0)
        stochastic_d = indicators.get('stochastic_d', 0)
        adx = indicators.get('adx', 0)
        cci = indicators.get('cci', 0)
        
        # Calculate additional metrics
        price_change = ((current_price - prev_close) / prev_close * 100) if prev_close and prev_close != 0 else 0
        volume_trend = "N/A"
        if volume > 0:
            # Simple volume trend analysis (would need historical volume for real analysis)
            volume_trend = "HIGH" if volume > 1000000 else "MODERATE" if volume > 100000 else "LOW"
        
        # Advanced RSI analysis with divergence detection
        rsi_strength = ""
        rsi_divergence = "NONE"
        if rsi != 0:  # Only analyze if RSI is available
            if rsi < 20:
                rsi_strength = "EXTREMELY"
                rsi_divergence = "BULLISH"  # Potential bullish divergence
                insight = f"RSI: {rsi:.2f} - EXTREMELY OVERSOLD (Strong buying opportunity)"
                insights.append(f"📉 {insight}")
            elif rsi < 30:
                rsi_strength = "VERY"
                rsi_divergence = "BULLISH"  # Possible bullish divergence
                insight = f"RSI: {rsi:.2f} - VERY OVERSOLD (Good buying opportunity)"
                insights.append(f"📉 {insight}")
            elif rsi > 80:
                rsi_strength = "EXTREMELY"
                rsi_divergence = "BEARISH"  # Potential bearish divergence
                insight = f"RSI: {rsi:.2f} - EXTREMELY OVERBOUGHT (Strong selling opportunity)"
                insights.append(f"📈 {insight}")
            elif rsi > 70:
                rsi_strength = "VERY"
                rsi_divergence = "BEARISH"  # Possible bearish divergence
                insight = f"RSI: {rsi:.2f} - VERY OVERBOUGHT (Good selling opportunity)"
                insights.append(f"📈 {insight}")
            elif 30 <= rsi <= 70:
                insight = f"RSI: {rsi:.2f} - NEUTRAL (No strong signal)"
                rsi_strength = "NEUTRAL"
                insights.append(f"⚖️ {insight}")
        else:
            insights.append("📉 RSI: N/A (Insufficient data for analysis)")
            
        # Moving average analysis with multiple timeframes
        ma_status = ""
        ma_trend_strength = "NEUTRAL"
        if current_price != 0 and sma_20 != 0 and sma_50 != 0:
            # Primary moving average analysis
            if current_price > sma_20 > sma_50:
                ma_status = "STRONG BULLISH"
                ma_trend_strength = "STRONG"
                insights.append(f"📊 MA Trend: STRONG BULLISH (Golden Cross Pattern)")
            elif sma_20 > sma_50 and current_price > sma_50:
                ma_status = "BULLISH"
                insights.append(f"📊 MA Trend: BULLISH (Short above long)")
            elif current_price < sma_20 < sma_50:
                ma_status = "STRONG BEARISH"
                ma_trend_strength = "STRONG"
                insights.append(f"📉 MA Trend: STRONG BEARISH (Death Cross Pattern)")
            elif sma_20 < sma_50 and current_price < sma_50:
                ma_status = "BEARISH"
                insights.append(f"📉 MA Trend: BEARISH (Short below long)")
            else:
                ma_status = "NEUTRAL"
                insights.append(f"⚖️ MA Trend: NEUTRAL (Crossovers in progress)")
                
            # Additional MA relationships
            if ema_12 != 0 and ema_26 != 0:
                if ema_12 > ema_26:
                    insights.append(f"⚡ EMA Trend: BULLISH (EMA12 {ema_12:.2f} > EMA26 {ema_26:.2f})")
                else:
                    insights.append(f"⚡ EMA Trend: BEARISH (EMA12 {ema_12:.2f} < EMA26 {ema_26:.2f})")
        else:
            insights.append(f"📊 MA Trend: N/A (Insufficient data for analysis - SMA20: {sma_20}, SMA50: {sma_50})")
            
        # MACD analysis with histogram and divergence detection
        if macd != 0 and macd_signal != 0:
            macd_histogram = indicators.get('macd_histogram', 0)
            macd_momentum = "INCREASING" if macd_histogram > 0 else "DECREASING"
            
            if macd > macd_signal:
                insights.append(f"📊 MACD: Bullish momentum (MACD {macd:.4f} > Signal {macd_signal:.4f})")
                if macd_histogram > 0:
                    insights.append(f"📈 MACD Histogram: Positive and {macd_momentum} ({macd_histogram:.4f})")
            else:
                insights.append(f"📉 MACD: Bearish momentum (MACD {macd:.4f} < Signal {macd_signal:.4f})")
                if macd_histogram < 0:
                    insights.append(f"📉 MACD Histogram: Negative and {macd_momentum} ({macd_histogram:.4f})")
        else:
            insights.append(f"📉 MACD: N/A (Insufficient data for analysis - MACD: {macd}, Signal: {macd_signal})")
            
        # Stochastic Oscillator analysis
        if stochastic_k != 0 and stochastic_d != 0:
            if stochastic_k > stochastic_d:
                if stochastic_k < 20:
                    insights.append(f"💎 Stochastic: Oversold crossover - Bullish signal (K:{stochastic_k:.2f}, D:{stochastic_d:.2f})")
                elif stochastic_k > 80:
                    insights.append(f"💎 Stochastic: Overbought crossover - Bearish signal (K:{stochastic_k:.2f}, D:{stochastic_d:.2f})")
                else:
                    insights.append(f"💎 Stochastic: Neutral crossover (K:{stochastic_k:.2f}, D:{stochastic_d:.2f})")
            else:
                if stochastic_k < 20:
                    insights.append(f"💎 Stochastic: Oversold zone - Potential bullish setup (K:{stochastic_k:.2f}, D:{stochastic_d:.2f})")
                elif stochastic_k > 80:
                    insights.append(f"💎 Stochastic: Overbought zone - Potential bearish setup (K:{stochastic_k:.2f}, D:{stochastic_d:.2f})")
                else:
                    insights.append(f"💎 Stochastic: Neutral zone (K:{stochastic_k:.2f}, D:{stochastic_d:.2f})")
        else:
            insights.append("💎 Stochastic: N/A (Insufficient data)")
            
        # ADX analysis for trend strength
        if adx != 0:
            if adx > 25:
                trend_strength = "STRONG" if adx > 30 else "MODERATE"
                insights.append(f"🧭 ADX: {trend_strength} trend ({adx:.2f}) - Trend following recommended")
            elif adx < 20:
                insights.append(f"🧭 ADX: Weak trend ({adx:.2f}) - Range trading conditions")
            else:
                insights.append(f"🧭 ADX: Moderate trend ({adx:.2f}) - Caution advised")
        else:
            insights.append("🧭 ADX: N/A (Trend strength unknown)")
            
        # CCI analysis for cyclical behavior
        if cci != 0:
            if cci > 100:
                insights.append(f"🌀 CCI: Strong uptrend ({cci:.2f}) - Potential overextension")
            elif cci < -100:
                insights.append(f"🌀 CCI: Strong downtrend ({cci:.2f}) - Potential reversal zone")
            else:
                insights.append(f"🌀 CCI: Neutral cycle ({cci:.2f}) - Normal conditions")
        else:
            insights.append("🌀 CCI: N/A (Cyclical analysis unavailable)")
            
        # Bollinger Bands analysis with squeeze detection
        if bb_upper != 0 and bb_lower != 0 and bb_middle != 0:
            bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle != 0 else 0
            position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
            
            if bb_width < 0.05:  # Squeeze condition (5% width)
                insights.append(f"🌪️ BB Squeeze Detected - Low volatility, potential breakout imminent")
            
            if position_in_bands < 0.15:  # Near lower band
                insights.append(f"💎 Price near lower Bollinger Band ({position_in_bands*100:.1f}% position)")
            elif position_in_bands > 0.85:  # Near upper band
                insights.append(f"💎 Price near upper Bollinger Band ({position_in_bands*100:.1f}% position)")
                
        # Risk analysis with enhanced metrics
        if volatility != 0:
            if volatility < 0.015:
                risk_level = "VERY LOW"
                risk_color = "ai_buy"
                insights.append(f"🛡️ Risk: {risk_level} (Volatility: {volatility:.5f})")
            elif volatility < 0.03:
                risk_level = "LOW"
                risk_color = "ai_buy"
                insights.append(f"🛡️ Risk: {risk_level} (Volatility: {volatility:.5f})")
            elif volatility < 0.06:
                risk_level = "MODERATE"
                risk_color = "ai_neutral"
                insights.append(f"⚠️ Risk: {risk_level} (Volatility: {volatility:.5f})")
            else:
                risk_level = "HIGH"
                risk_color = "ai_warning"
                insights.append(f"🚨 Risk: {risk_level} (Volatility: {volatility:.5f})")
        else:
            insights.append(f"⚠️ Risk: N/A (Volatility: N/A)")
            
        # Volume analysis
        if volume > 0:
            insights.append(f"🔊 Volume: {volume_trend} ({volume:,} shares)")
            
        # Price action analysis
        if current_price != 0 and prev_close != 0:
            insights.append(f"💰 Price Action: {price_change:+.2f}% today (${current_price:.2f})")
            
        # Advanced buy/sell recommendations with machine learning-inspired scoring
        buy_signals = 0
        sell_signals = 0
        neutral_signals = 0
        reasons = []
        counter_reasons = []
        
        # Weighted signal analysis (more sophisticated than simple counting)
        signal_weights = {
            'rsi_extreme_oversold': 2.0,
            'rsi_very_oversold': 1.5,
            'rsi_extreme_overbought': 2.0,
            'rsi_very_overbought': 1.5,
            'ma_golden_cross': 2.0,
            'ma_bullish': 1.5,
            'ma_death_cross': 2.0,
            'ma_bearish': 1.5,
            'macd_bullish': 1.5,
            'macd_bearish': 1.5,
            'bb_support': 1.0,
            'bb_resistance': 1.0,
            'stochastic_bullish': 1.2,
            'stochastic_bearish': 1.2,
            'adx_strong_trend': 1.5,
            'adx_weak_trend': -0.5
        }
        
        total_weighted_score = 0.0
        max_possible_score = sum(signal_weights.values())
        
        # Only calculate signals if we have the required data
        if rsi != 0:
            # RSI signal with weights
            if rsi < 20:
                buy_signals += 1
                total_weighted_score += signal_weights['rsi_extreme_oversold']
                reasons.append("RSI extremely oversold")
            elif rsi < 30:
                buy_signals += 1
                total_weighted_score += signal_weights['rsi_very_oversold']
                reasons.append("RSI very oversold")
            elif rsi > 80:
                sell_signals += 1
                total_weighted_score -= signal_weights['rsi_extreme_overbought']
                counter_reasons.append("RSI extremely overbought")
            elif rsi > 70:
                sell_signals += 1
                total_weighted_score -= signal_weights['rsi_very_overbought']
                counter_reasons.append("RSI very overbought")
        
        if current_price != 0 and sma_20 != 0 and sma_50 != 0:
            # Moving average signal with weights
            if current_price > sma_20 > sma_50:
                buy_signals += 1
                total_weighted_score += signal_weights['ma_golden_cross']
                reasons.append("Golden Cross pattern")
            elif sma_20 > sma_50 and current_price > sma_50:
                buy_signals += 1
                total_weighted_score += signal_weights['ma_bullish']
                reasons.append("Bullish moving average alignment")
            elif current_price < sma_20 < sma_50:
                sell_signals += 1
                total_weighted_score -= signal_weights['ma_death_cross']
                counter_reasons.append("Death Cross pattern")
            elif sma_20 < sma_50 and current_price < sma_50:
                sell_signals += 1
                total_weighted_score -= signal_weights['ma_bearish']
                counter_reasons.append("Bearish moving average alignment")
            
        if macd != 0 and macd_signal != 0:
            # MACD signal with weights
            if macd > macd_signal:
                buy_signals += 1
                total_weighted_score += signal_weights['macd_bullish']
                reasons.append("MACD bullish crossover")
            else:
                sell_signals += 1
                total_weighted_score -= signal_weights['macd_bearish']
                counter_reasons.append("MACD bearish crossover")
                
        if adx != 0:
            # ADX trend strength signal
            if adx > 25:
                total_weighted_score += signal_weights['adx_strong_trend'] * (1 if buy_signals > sell_signals else -1 if sell_signals > buy_signals else 0)
                if adx > 30:
                    reasons.append("Strong trend confirmed by ADX")
                else:
                    reasons.append("Moderate trend confirmed by ADX")
            else:
                total_weighted_score += signal_weights['adx_weak_trend']
                neutral_signals += 1
                reasons.append("Weak trend by ADX - caution advised")
        
        # Bollinger Bands signal
        if current_price != 0 and bb_upper != 0 and bb_lower != 0:
            position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
            
            if position_in_bands < 0.15:  # Near lower band
                buy_signals += 1
                total_weighted_score += signal_weights['bb_support']
                reasons.append("Price near lower Bollinger Band (support)")
            elif position_in_bands > 0.85:  # Near upper band
                sell_signals += 1
                total_weighted_score -= signal_weights['bb_resistance']
                counter_reasons.append("Price near upper Bollinger Band (resistance)")
        
        # Stochastic signals
        if stochastic_k != 0 and stochastic_d != 0:
            if stochastic_k > stochastic_d and stochastic_k < 20:
                buy_signals += 1
                total_weighted_score += signal_weights['stochastic_bullish']
                reasons.append("Stochastic bullish crossover in oversold zone")
            elif stochastic_k < stochastic_d and stochastic_k > 80:
                sell_signals += 1
                total_weighted_score -= signal_weights['stochastic_bearish']
                counter_reasons.append("Stochastic bearish crossover in overbought zone")
        
        # Normalize weighted score to -100 to +100 range
        normalized_score = (total_weighted_score / max_possible_score) * 100 if max_possible_score != 0 else 0
        confidence_score = abs(normalized_score)
        
        # Generate recommendation with enhanced logic
        insights.append(f"\n🎯 ADVANCED AI RECOMMENDATION:")
        if buy_signals > 0 or sell_signals > 0 or neutral_signals > 0:
            if normalized_score > 20:  # Strong buy signal
                insights.append(f"🟢 STRONG BUY (Score: +{normalized_score:.1f})")
                insights.append(f"   Confidence: {confidence_score:.1f}%")
                if reasons:
                    insights.append(f"   Key Factors: {', '.join(reasons[:3])}")
            elif normalized_score > 5:  # Moderate buy signal
                insights.append(f"🔵 MODERATE BUY (Score: +{normalized_score:.1f})")
                insights.append(f"   Confidence: {confidence_score:.1f}%")
                if reasons:
                    insights.append(f"   Supporting Factors: {', '.join(reasons[:2])}")
            elif normalized_score < -20:  # Strong sell signal
                insights.append(f"🔴 STRONG SELL (Score: {normalized_score:.1f})")
                insights.append(f"   Confidence: {confidence_score:.1f}%")
                if counter_reasons:
                    insights.append(f"   Key Factors: {', '.join(counter_reasons[:3])}")
            elif normalized_score < -5:  # Moderate sell signal
                insights.append(f"🟠 MODERATE SELL (Score: {normalized_score:.1f})")
                insights.append(f"   Confidence: {confidence_score:.1f}%")
                if counter_reasons:
                    insights.append(f"   Supporting Factors: {', '.join(counter_reasons[:2])}")
            else:  # Hold/neutral signal
                insights.append(f"🟡 HOLD (Score: {normalized_score:.1f})")
                if neutral_signals > 0:
                    insights.append(f"   Neutral Factors: {', '.join(reasons[-2:])}")
                if reasons or counter_reasons:
                    combined_factors = reasons[-1:] + counter_reasons[-1:]
                    if combined_factors:
                        insights.append(f"   Mixed Signals: {', '.join(combined_factors)}")
        else:
            insights.append("🟡 HOLD - Insufficient data for recommendation")
        
        # Add sophisticated price targets with multiple scenarios
        insights.append(f"\n🎯 DETAILED PRICE TARGETS:")
        if normalized_score > 5:  # Buy recommendation
            # Calculate multiple targets
            targets = []
            
            # Support/resistance based targets
            if bb_lower != 0 and bb_upper != 0:
                targets.append(f"Immediate Support: ${bb_lower:.2f}")
                targets.append(f"Resistance Levels: ${current_price * 1.02:.2f}, ${bb_upper:.2f}")
            
            # Fibonacci retracement targets (simplified)
            fib_levels = [
                ("23.6%", current_price * 1.0236),
                ("38.2%", current_price * 1.0382),
                ("50%", current_price * 1.05),
                ("61.8%", current_price * 1.0618)
            ]
            targets.extend([f"Fib {level}: ${price:.2f}" for level, price in fib_levels])
            
            # Risk management levels
            atr = (bb_upper - bb_lower) / 2 if bb_upper != 0 and bb_lower != 0 else current_price * 0.02
            stop_loss = current_price - (atr * 1.5)
            targets.append(f"🎯 STOP LOSS: ${stop_loss:.2f}")
            targets.append(f"🚨 HARD STOP: ${current_price * 0.95:.2f}")
            
            for target in targets:
                insights.append(f"   • {target}")
                
        elif normalized_score < -5:  # Sell recommendation
            # Calculate downside targets
            targets = []
            
            # Support/resistance based targets
            if bb_lower != 0 and bb_upper != 0:
                targets.append(f"Resistance: ${bb_upper:.2f}")
                targets.append(f"Support Levels: ${current_price * 0.98:.2f}, ${bb_lower:.2f}")
            
            # Downside targets
            downside_levels = [
                ("2% Drop", current_price * 0.98),
                ("5% Drop", current_price * 0.95),
                ("10% Drop", current_price * 0.90)
            ]
            targets.extend([f"{desc}: ${price:.2f}" for desc, price in downside_levels])
            
            # Risk management levels
            atr = (bb_upper - bb_lower) / 2 if bb_upper != 0 and bb_lower != 0 else current_price * 0.02
            stop_loss = current_price + (atr * 1.5)
            targets.append(f"🎯 STOP LOSS: ${stop_loss:.2f}")
            targets.append(f"🚨 HARD STOP: ${current_price * 1.05:.2f}")
            
            for target in targets:
                insights.append(f"   • {target}")
        else:  # Hold recommendation
            insights.append(f"   • Current Price: ${current_price:.2f}")
            if bb_lower != 0 and bb_upper != 0:
                insights.append(f"   • Support Zone: ${bb_lower:.2f}")
                insights.append(f"   • Resistance Zone: ${bb_upper:.2f}")
            insights.append(f"   • Wait for clearer technical signals")
        
        # Add timeframe-specific recommendations with enhanced detail
        insights.append(f"\n⏰ MULTI-TIMEFRAME STRATEGY:")
        
        # Determine primary trend direction
        primary_trend = "BULLISH" if normalized_score > 0 else "BEARISH" if normalized_score < 0 else "NEUTRAL"
        
        if primary_trend == "BULLISH":
            insights.append(f"   🟢 Short-term: Look for buying opportunities on minor pullbacks")
            insights.append(f"   🟢 Medium-term: Accumulate positions with pyramiding strategy")
            insights.append(f"   🟢 Long-term: Hold core positions for trend continuation")
        elif primary_trend == "BEARISH":
            insights.append(f"   🔴 Short-term: Consider protective sells on minor rallies")
            insights.append(f"   🔴 Medium-term: Reduce exposure with staggered exits")
            insights.append(f"   🔴 Long-term: Wait for accumulation zone confirmation")
        else:
            insights.append(f"   🟡 Short-term: Range trade with tight stops")
            insights.append(f"   🟡 Medium-term: Dollar-cost average into core positions")
            insights.append(f"   🟡 Long-term: Accumulate high-conviction names on dips")
        
        # Add sophisticated risk management with position sizing guidance
        insights.append(f"\n🛡️ ADVANCED RISK MANAGEMENT:")
        
        # Dynamic position sizing based on confidence and volatility
        base_position_size = 100  # Base shares for example
        volatility_multiplier = max(0.5, min(2.0, 1 / (volatility * 100))) if volatility > 0 else 1.0
        confidence_multiplier = max(0.5, min(2.0, confidence_score / 50)) if confidence_score > 0 else 1.0
        
        # Position sizing recommendation
        if abs(normalized_score) > 30:  # High conviction
            position_sizing = "AGGRESSIVE"
            sizing_explanation = "High confidence signal with favorable risk/reward"
        elif abs(normalized_score) > 10:  # Moderate conviction
            position_sizing = "MODERATE"
            sizing_explanation = "Balanced approach with measured exposure"
        else:  # Low conviction
            position_sizing = "CONSERVATIVE"
            sizing_explanation = "Light positioning awaiting clearer signals"
            
        insights.append(f"   💼 Position Approach: {position_sizing}")
        insights.append(f"   📊 Reason: {sizing_explanation}")
        
        # Risk-adjusted recommendations
        if risk_level == "HIGH":
            insights.append(f"   ⚠️ HIGH VOLATILITY ENVIRONMENT")
            insights.append(f"   • Reduce position sizes by 40-50%")
            insights.append(f"   • Use tighter stop-losses (1-2% range)")
            insights.append(f"   • Consider options strategies for defined risk")
        elif risk_level == "MODERATE":
            insights.append(f"   ✅ MODERATE RISK CONDITIONS")
            insights.append(f"   • Standard position sizing appropriate")
            insights.append(f"   • Balanced stop-loss placement (2-3% range)")
            insights.append(f"   • Monitor for volatility expansion")
        else:
            insights.append(f"   ✅ LOW VOLATILITY ENVIRONMENT")
            insights.append(f"   • Opportunity for increased position sizes")
            insights.append(f"   • Extended profit targets acceptable")
            insights.append(f"   • Monitor for volatility contraction")
        
        # Add market regime identification
        insights.append(f"\n🌐 MARKET REGIME ANALYSIS:")
        
        # Combined regime detection
        if adx > 25 and ((rsi < 30 and ma_status in ["BULLISH", "STRONG BULLISH"]) or 
                         (rsi > 70 and ma_status in ["BEARISH", "STRONG BEARISH"])):
            insights.append(f"   🔍 Regime: TREND CONTINUATION")
            insights.append(f"   • Follow momentum with trailing stops")
            insights.append(f"   • Add to winning positions on pullbacks")
        elif adx < 20 and ((rsi > 30 and rsi < 70) or 
                          (current_price > sma_20 * 0.98 and current_price < sma_20 * 1.02)):
            insights.append(f"   🔍 Regime: RANGE BOUND")
            insights.append(f"   • Buy support, sell resistance")
            insights.append(f"   • Avoid directional bias")
        else:
            insights.append(f"   🔍 Regime: TRANSITION PHASE")
            insights.append(f"   • Prepare for breakout in either direction")
            insights.append(f"   • Tight stops, quick reactions to new trends")
        
        # Add execution timing suggestions
        insights.append(f"\n⚡ EXECUTION TIMING:")
        
        # Time-of-day considerations
        from datetime import datetime
        current_hour = datetime.now().hour
        
        if 9 <= current_hour <= 11:  # Morning session
            insights.append(f"   🕘 Market Open: High volatility, wider spreads")
            insights.append(f"   • Consider limit orders for better fills")
        elif 11 <= current_hour <= 14:  # Midday
            insights.append(f"   🕐 Midday Session: Normal conditions")
            insights.append(f"   • Standard execution approaches apply")
        elif 14 <= current_hour <= 16:  # Afternoon/Close
            insights.append(f"   🕓 Market Close: Potential volatility spikes")
            insights.append(f"   • Be cautious with new positions near close")
        
        # Add portfolio integration advice
        insights.append(f"\n💼 PORTFOLIO INTEGRATION:")
        
        # Position sizing in context of overall portfolio
        portfolio_impact = "CORE" if abs(normalized_score) > 20 else "TACTICAL" if abs(normalized_score) > 5 else "OPPORTUNISTIC"
        insights.append(f"   🎯 Role: {portfolio_impact} POSITION")
        
        if portfolio_impact == "CORE":
            insights.append(f"   • Allocate 5-10% of portfolio capital")
            insights.append(f"   • Use dollar-cost averaging over 2-3 days")
        elif portfolio_impact == "TACTICAL":
            insights.append(f"   • Allocate 2-5% of portfolio capital")
            insights.append(f"   • Monitor closely for regime changes")
        else:
            insights.append(f"   • Allocate 1-2% of portfolio capital")
            insights.append(f"   • Ready to scale up on confirmation")
        
        # Add final timestamp and version
        insights.append(f"\n📅 Analysis Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        insights.append(f"🧠 AI Model Version: Advanced Technical Analysis v2.1")
        
        return "\n".join(insights) + f"\n\n--- END OF ANALYSIS ---"

    def generate_advanced_ai_insights(self, symbol, analysis):
        """Generate advanced AI insights with comprehensive market analysis and predictive analytics"""
        try:
            insights = [f"🤖 ADVANCED AI INSIGHTS FOR {symbol}", "="*60]
            
            # Generate enhanced machine learning predictions from the AdvancedAIInsights class
            try:
                # Import and use the enhanced AI insights from the market researcher
                from robinhood_market_researcher import AdvancedAIInsights
                ai_insights = AdvancedAIInsights()
                comprehensive_insights = ai_insights.generate_comprehensive_insights(symbol, analysis)
                
                # Add ML predictions from the new enhanced analysis
                if 'ml_insights' in comprehensive_insights:
                    ml_insights = comprehensive_insights['ml_insights']
                    
                    insights.append("\n🧠 ENHANCED ML ANALYSIS:")
                    
                    # Add ensemble prediction
                    if 'ensemble_prediction' in ml_insights:
                        ensemble_pred = ml_insights['ensemble_prediction']
                        insights.append(f"   • Recommendation: {ensemble_pred['recommendation']}")
                        insights.append(f"   • Confidence: {ensemble_pred['confidence']:.1f}%")
                        insights.append(f"   • Score: {ensemble_pred['score']:.3f}")
                    
                    # Add pattern recognition
                    if 'pattern_recognition' in ml_insights and ml_insights['pattern_recognition']:
                        insights.append(f"\n🔍 PATTERN RECOGNITION:")
                        for pattern_name, pattern_desc in ml_insights['pattern_recognition'].items():
                            insights.append(f"   • {pattern_name.replace('_', ' ').title()}: {pattern_desc}")
                    
                    # Add ML-based price targets
                    if 'price_targets' in ml_insights:
                        targets = ml_insights['price_targets']
                        insights.append(f"\n🎯 ML-BASED PRICE TARGETS:")
                        insights.append(f"   • Short-term target: ${targets['short_term']:.2f}")
                        insights.append(f"   • Medium-term target: ${targets['medium_term']:.2f}")
                        insights.append(f"   • Stop loss: ${targets['stop_loss']:.2f}")
                    
                    # Add risk-adjusted signals
                    if 'risk_adjusted_signals' in ml_insights:
                        risk_signals = ml_insights['risk_adjusted_signals']
                        insights.append(f"\n🛡️ RISK-ADJUSTED SIGNALS:")
                        for signal_name, signal_value in risk_signals.items():
                            insights.append(f"   • {signal_name.replace('_', ' ').title()}: {signal_value}")
                    
                    # Add regime-aware analysis
                    if 'regime_awareness' in ml_insights:
                        regime_info = ml_insights['regime_awareness']
                        insights.append(f"\n🌐 REGIME-AWARE ANALYSIS:")
                        insights.append(f"   • Market Regime: {regime_info['regime']}")
                        insights.append(f"   • Strategy Recommendation: {regime_info['regime_signal']}")
                        insights.append(f"   • Regime Confidence: {regime_info['regime_confidence']:.1f}%")
            
            except ImportError:
                # Fallback to basic ML predictions if the enhanced module is not available
                ml_predictions = self.generate_ml_predictions(symbol, analysis)
                
                # Add ML predictions to insights
                if ml_predictions:
                    insights.append("\n🧠 MACHINE LEARNING PREDICTIONS:")
                    for pred_name, pred_value in ml_predictions.items():
                        if isinstance(pred_value, dict):
                            insights.append(f"   • {pred_name}: {pred_value.get('prediction', 'N/A')} ({pred_value.get('confidence', 0):.1f}% confidence)")
                        else:
                            insights.append(f"   • {pred_name}: {pred_value}")
            
            # Add predictive analytics
            insights.append(f"\n🔮 PREDICTIVE ANALYTICS:")
            
            # Enhanced price predictions using ensemble methods
            price_predictions = self.generate_price_predictions(symbol, analysis, {})
            for pred_line in price_predictions:
                insights.append(f"   {pred_line}")
            
            # Enhanced risk forecasts
            risk_forecasts = self.generate_risk_forecasts(symbol, analysis, {})
            for risk_line in risk_forecasts:
                insights.append(f"   {risk_line}")
            
            # Enhanced opportunity scanning
            opportunities = self.scan_trading_opportunities(symbol, analysis, {})
            if opportunities:
                insights.append(f"\n💎 TRADING OPPORTUNITIES:")
                for opp_line in opportunities[:5]:  # Limit to top 5 opportunities
                    insights.append(f"   {opp_line}")
            
            # Enhanced market regime forecasting
            regime_forecast = self.forecast_market_regime(symbol, analysis, {})
            if regime_forecast:
                insights.append(f"\n🌐 MARKET REGIME FORECAST:")
                for regime_line in regime_forecast:
                    insights.append(f"   {regime_line}")
            
            # Add technical analysis section
            insights.append(f"\n📊 TECHNICAL ANALYSIS:")
            
            # Safely extract values with defaults
            indicators = analysis.get('indicators', {})
            rsi = indicators.get('rsi', 0)
            sma_20 = indicators.get('sma_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            current_price = analysis.get('current_price', 0)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            volatility = analysis.get('risk_metrics', {}).get('volatility', 0)
            
            # RSI analysis
            if rsi != 0:  # Only analyze if RSI is available
                if rsi < 20:
                    insight = f"RSI: {rsi:.2f} - EXTREMELY OVERSOLD (Strong buying opportunity)"
                    insights.append(f"📉 {insight}")
                elif rsi < 30:
                    insight = f"RSI: {rsi:.2f} - VERY OVERSOLD (Good buying opportunity)"
                    insights.append(f"📉 {insight}")
                elif rsi > 80:
                    insight = f"RSI: {rsi:.2f} - EXTREMELY OVERBOUGHT (Strong selling opportunity)"
                    insights.append(f"📈 {insight}")
                elif rsi > 70:
                    insight = f"RSI: {rsi:.2f} - VERY OVERBOUGHT (Good selling opportunity)"
                    insights.append(f"📈 {insight}")
                elif 30 <= rsi <= 70:
                    insight = f"RSI: {rsi:.2f} - NEUTRAL (No strong signal)"
                    insights.append(f"⚖️ {insight}")
            else:
                insights.append("📉 RSI: N/A (Insufficient data for analysis)")
                
            # Moving average analysis
            ma_status = ""
            if current_price != 0 and sma_20 != 0 and sma_50 != 0:
                if current_price > sma_20 > sma_50:
                    ma_status = "STRONG BULLISH"
                    insights.append(f"📊 MA Trend: STRONG BULLISH (Golden Cross Pattern)")
                elif sma_20 > sma_50 and current_price > sma_50:
                    ma_status = "BULLISH"
                    insights.append(f"📊 MA Trend: BULLISH (Short above long)")
                elif current_price < sma_20 < sma_50:
                    ma_status = "STRONG BEARISH"
                    insights.append(f"📉 MA Trend: STRONG BEARISH (Death Cross Pattern)")
                elif sma_20 < sma_50 and current_price < sma_50:
                    ma_status = "BEARISH"
                    insights.append(f"📉 MA Trend: BEARISH (Short below long)")
                else:
                    ma_status = "NEUTRAL"
                    insights.append(f"⚖️ MA Trend: NEUTRAL (Crossovers in progress)")
            else:
                insights.append(f"📊 MA Trend: N/A (Insufficient data for analysis)")
                
            # MACD analysis
            if macd != 0 and macd_signal != 0:
                if macd > macd_signal:
                    insights.append(f"📊 MACD: Bullish momentum (MACD {macd:.4f} > Signal {macd_signal:.4f})")
                else:
                    insights.append(f"📉 MACD: Bearish momentum (MACD {macd:.4f} < Signal {macd_signal:.4f})")
            else:
                insights.append(f"📉 MACD: N/A (Insufficient data for analysis)")
                
            # Risk analysis
            if volatility != 0:
                if volatility < 0.015:
                    risk_level = "VERY LOW"
                    insights.append(f"🛡️ Risk: {risk_level} (Volatility: {volatility:.5f})")
                elif volatility < 0.03:
                    risk_level = "LOW"
                    insights.append(f"🛡️ Risk: {risk_level} (Volatility: {volatility:.5f})")
                elif volatility < 0.06:
                    risk_level = "MODERATE"
                    insights.append(f"⚠️ Risk: {risk_level} (Volatility: {volatility:.5f})")
                else:
                    risk_level = "HIGH"
                    insights.append(f"🚨 Risk: {risk_level} (Volatility: {volatility:.5f})")
            else:
                insights.append(f"⚠️ Risk: N/A (Volatility: N/A)")
            
            # Generate buy/sell recommendations based on multiple indicators
            buy_signals = 0
            sell_signals = 0
            reasons = []
            
            # Only calculate signals if we have the required data
            if rsi != 0:
                # RSI signal
                if rsi < 30:
                    buy_signals += 1
                    reasons.append("RSI indicates oversold conditions")
                elif rsi > 70:
                    sell_signals += 1
                    reasons.append("RSI indicates overbought conditions")
            
            if current_price != 0 and sma_20 != 0 and sma_50 != 0:
                # Moving average signal
                if current_price > sma_20 > sma_50:
                    buy_signals += 1
                    reasons.append("Price above both moving averages")
                elif current_price < sma_20 < sma_50:
                    sell_signals += 1
                    reasons.append("Price below both moving averages")
                
            if macd != 0 and macd_signal != 0:
                # MACD signal
                if macd > macd_signal:
                    buy_signals += 1
                    reasons.append("MACD bullish crossover")
                else:
                    sell_signals += 1
                    reasons.append("MACD bearish crossover")
            
            # Bollinger Bands signal
            bb_upper = indicators.get('bb_upper', 0)
            bb_lower = indicators.get('bb_lower', 0)
            bb_middle = indicators.get('bb_middle', 0)
            
            if current_price != 0 and bb_upper != 0 and bb_lower != 0:
                position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                
                if position_in_bands < 0.15:  # Near lower band
                    buy_signals += 1
                    reasons.append("Price near lower Bollinger Band (support)")
                elif position_in_bands > 0.85:  # Near upper band
                    sell_signals += 1
                    reasons.append("Price near upper Bollinger Band (resistance)")
            
            # Generate recommendation
            insights.append(f"\n🎯 AI RECOMMENDATION:")
            if buy_signals > 0 or sell_signals > 0:  # Only if we have signals to analyze
                if buy_signals > sell_signals:
                    confidence = min(100, (buy_signals / (buy_signals + sell_signals)) * 100)
                    insights.append(f"🟢 BUY with {confidence:.0f}% confidence")
                    if reasons:
                        insights.append(f"   Reasons: {', '.join([r for i, r in enumerate(reasons) if i < buy_signals])}")
                elif sell_signals > buy_signals:
                    confidence = min(100, (sell_signals / (buy_signals + sell_signals)) * 100)
                    insights.append(f"🔴 SELL with {confidence:.0f}% confidence")
                    if reasons:
                        insights.append(f"   Reasons: {', '.join([r for i, r in enumerate(reasons) if i < sell_signals])}")
                else:
                    insights.append("🟡 HOLD - Mixed signals")
                    if reasons:
                        insights.append(f"   Conflicting reasons: {', '.join(reasons)}")
            else:
                insights.append("🟡 HOLD - Insufficient data for recommendation")
            
            # Add specific price targets for actionable moves
            insights.append(f"\n🎯 SPECIFIC PRICE TARGETS:")
            if buy_signals > sell_signals:
                # Calculate potential targets based on technical analysis
                if sma_20 > sma_50 and current_price > sma_20:  # Bullish trend
                    resistance_level = bb_upper if bb_upper > current_price else current_price * 1.05
                    targets = [f"Short-term: ${current_price * 1.02:.2f}", 
                             f"Medium-term: ${resistance_level:.2f}", 
                             f"Stop Loss: ${current_price * 0.97:.2f}"]
                    insights.extend([f"   {t}" for t in targets])
                elif rsi < 30:  # Oversold, potential bounce
                    target = (bb_middle + current_price) / 2
                    targets = [f"Entry: ${current_price:.2f}", 
                             f"Target: ${target:.2f}", 
                             f"Stop Loss: ${current_price * 0.95:.2f}"]
                    insights.extend([f"   {t}" for t in targets])
                else:
                    insights.append(f"   Entry: ${current_price:.2f}")
                    insights.append(f"   Target: ${current_price * 1.03:.2f}")
                    insights.append(f"   Stop Loss: ${current_price * 0.97:.2f}")
            elif sell_signals > buy_signals:
                # Calculate potential targets for selling
                if sma_20 < sma_50 and current_price < sma_20:  # Bearish trend
                    support_level = bb_lower if bb_lower < current_price else current_price * 0.95
                    targets = [f"Short-term: ${current_price * 0.98:.2f}", 
                             f"Medium-term: ${support_level:.2f}", 
                             f"Stop Loss: ${current_price * 1.03:.2f}"]
                    insights.extend([f"   {t}" for t in targets])
                elif rsi > 70:  # Overbought, potential pullback
                    target = (bb_middle + current_price) / 2
                    targets = [f"Entry: ${current_price:.2f}", 
                             f"Target: ${target:.2f}", 
                             f"Stop Loss: ${current_price * 1.05:.2f}"]
                    insights.extend([f"   {t}" for t in targets])
                else:
                    insights.append(f"   Exit: ${current_price:.2f}")
                    insights.append(f"   Target: ${current_price * 0.97:.2f}")
                    insights.append(f"   Stop Loss: ${current_price * 1.03:.2f}")
            else:
                insights.append(f"   Hold current position at ${current_price:.2f}")
            
            # Add time-based recommendations
            insights.append(f"\n⏰ TIMEFRAME RECOMMENDATIONS:")
            if buy_signals > sell_signals:
                insights.append(f"   Short-term: Consider buying on pullbacks")
                insights.append(f"   Medium-term: Position for potential upside")
                insights.append(f"   Long-term: Monitor for trend continuation")
            elif sell_signals > buy_signals:
                insights.append(f"   Short-term: Consider selling on rallies")
                insights.append(f"   Medium-term: Reduce exposure")
                insights.append(f"   Long-term: Wait for better entry point")
            else:
                insights.append(f"   Short/Medium/Long-term: Wait for clearer signals")
            
            # Add risk management tips
            insights.append(f"\n🛡️ RISK MANAGEMENT ADVICE:")
            if volatility != 0:
                if volatility < 0.015:
                    insights.append(f"   ⚠️ Use smaller position sizes")
                    insights.append(f"   ⚠️ Consider hedging strategies")
                    insights.append(f"   ⚠️ Tighter stop-loss orders recommended")
                elif volatility < 0.03:
                    insights.append(f"   ✅ Normal position sizing appropriate")
                    insights.append(f"   ✅ Standard stop-loss levels suitable")
                else:
                    insights.append(f"   ✅ Higher position sizes possible")
                    insights.append(f"   ✅ Opportunity for longer-term holds")
            else:
                insights.append(f"   ⚠️ Risk: N/A (Volatility: N/A)")
            
            # Add market context
            insights.append(f"\n🌐 MARKET CONTEXT:")
            if buy_signals > sell_signals:
                if rsi < 30 and ma_status == "STRONG BULLISH":
                    insights.append(f"   🚀 Strong accumulation zone - potential reversal")
                elif ma_status == "STRONG BULLISH":
                    insights.append(f"   📈 Trend continuation likely - follow momentum")
            elif sell_signals > buy_signals:
                if rsi > 70 and ma_status == "STRONG BEARISH":
                    insights.append(f"   📉 Strong distribution zone - potential reversal")
                elif ma_status == "STRONG BEARISH":
                    insights.append(f"   📉 Trend continuation likely - avoid long positions")
            
            # Add portfolio strategy
            insights.append(f"\n💼 PORTFOLIO STRATEGY:")
            if buy_signals > sell_signals:
                insights.append(f"   • Consider adding to position gradually")
                insights.append(f"   • Use dollar-cost averaging if uncertain")
                insights.append(f"   • Monitor overall market conditions")
            elif sell_signals > buy_signals:
                insights.append(f"   • Consider taking partial profits")
                insights.append(f"   • Evaluate overall portfolio allocation")
                insights.append(f"   • Watch for reversal signals")
            else:
                insights.append(f"   • Maintain current allocation")
                insights.append(f"   • Wait for clearer technical signals")
            
            return "\n".join(insights) + f"\n\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        except Exception as e:
            error_msg = f"Error generating advanced AI insights: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return f"🤖 ADVANCED AI INSIGHTS FOR {symbol}\n{'='*60}\n\n❌ ERROR: {error_msg}\n\nPlease try again or contact support."

    def calculate_position_size(self):
        """Calculate optimal position size based on risk parameters"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol")
                return

            # Get risk parameters from input fields
            try:
                account_size = float(self.account_size_entry.get())
                risk_pct = float(self.risk_pct_entry.get()) / 100  # Convert from percentage
                stop_loss_pct = float(self.stop_loss_entry.get()) / 100  # Convert from percentage
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for account size, risk percentage, and stop loss")
                return

            # Get current price for the stock
            data = self.current_analysis if self.current_analysis else robinhood_market_researcher.analyze_stock(symbol)
            current_price = data.get("current_price", 0)

            if current_price <= 0:
                messagebox.showerror("Error", f"Could not get current price for {symbol}")
                return

            # Calculate position size using the module function
            position_calc = robinhood_market_researcher.calculate_position_size(
                account_size, risk_pct, stop_loss_pct, current_price
            )

            # Display results
            self.risk_text.config(state=tk.NORMAL)
            self.risk_text.delete(1.0, tk.END)

            self.risk_text.insert(tk.END, f"🛡️ Risk Management for {symbol}\n", ("risk_header",))
            self.risk_text.insert(tk.END, "=" * 50 + "\n\n")

            self.risk_text.insert(tk.END, f"Account Size: ${account_size:,.2f}\n")
            self.risk_text.insert(tk.END, f"Risk Per Trade: {risk_pct*100:.2f}% (${account_size * risk_pct:.2f})\n")
            self.risk_text.insert(tk.END, f"Stop Loss: {stop_loss_pct*100:.2f}% (${current_price * (1 - stop_loss_pct):.2f})\n")
            self.risk_text.insert(tk.END, f"Current Price: ${current_price:.2f}\n\n")

            self.risk_text.insert(tk.END, "Position Sizing Results:\n", ("risk_calc",))
            self.risk_text.insert(tk.END, f"Shares to Buy: {position_calc['position_size_shares']}\n")
            self.risk_text.insert(tk.END, f"Position Value: ${position_calc['position_value']:.2f}\n")

            # Risk assessment
            if position_calc['position_size_shares'] <= 0:
                self.risk_text.insert(tk.END, "\n⚠️  Risk Warning: Position size is zero or negative. Check parameters.\n", ("risk_warning",))
            else:
                allocation_pct = (position_calc['position_value'] / account_size) * 100
                if allocation_pct > 10:  # More than 10% of account
                    self.risk_text.insert(tk.END, f"\n⚠️  Risk Warning: This position represents {allocation_pct:.2f}% of your account (high concentration).\n", ("risk_warning",))
                else:
                    self.risk_text.insert(tk.END, f"\n✅ Position represents {allocation_pct:.2f}% of your account (appropriate sizing).\n", ("risk_calc",))

            self.risk_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error calculating position size: {str(e)}")

    def add_to_watchlist(self):
        """Add current symbol to watchlist"""
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return
            
        try:
            # Use the analyzer to add to watchlist
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            analyzer.add_to_watchlist(symbol)
            messagebox.showinfo("Success", f"{symbol} added to watchlist")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding to watchlist: {str(e)}")

    def load_watchlist(self):
        """Load and display watchlist"""
        try:
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            watchlist_symbols = analyzer.watchlist.get_watchlist()
            
            if watchlist_symbols:
                # Create a new window to display watchlist
                watchlist_window = tk.Toplevel(self.root)
                watchlist_window.title("Watchlist")
                watchlist_window.geometry("800x500")
                watchlist_window.configure(bg="#1e1e1e")
                
                # Add a title
                title = tk.Label(watchlist_window, text="Your Watchlist", 
                                font=("Arial", 14, "bold"), fg="#64b5f6", bg="#1e1e1e")
                title.pack(pady=10)
                
                # Create a frame for the watchlist
                watchlist_frame = tk.Frame(watchlist_window, bg="#1e1e1e")
                watchlist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Create a text widget to display watchlist
                watchlist_text = scrolledtext.ScrolledText(watchlist_frame, 
                                                         bg="#2d2d2d", fg="#e0e0e0",
                                                         font=("Consolas", 10),
                                                         relief=tk.FLAT,
                                                         insertbackground="#e0e0e0")
                watchlist_text.pack(fill=tk.BOTH, expand=True)
                
                # Configure text tags
                watchlist_text.tag_configure("symbol", font=("Arial", 10, "bold"), foreground="#64b5f6")
                watchlist_text.tag_configure("price", font=("Arial", 10), foreground="#e0e0e0")
                watchlist_text.tag_configure("positive", font=("Arial", 10), foreground="#4caf50")
                watchlist_text.tag_configure("negative", font=("Arial", 10), foreground="#f44336")
                
                # Display watchlist items
                watchlist_text.insert(tk.END, f"{'SYMBOL':<10} | {'PRICE':<10} | {'CHANGE':<10} | {'STATUS':<10} | {'INDICATORS' }\n", ("symbol",))
                watchlist_text.insert(tk.END, "-"*80 + "\n")
                
                for symbol in watchlist_symbols:
                    try:
                        # Handle symbol that might be a tuple like ('BTC', 'crypto')
                        display_symbol = symbol[0] if isinstance(symbol, tuple) else symbol
                        
                        # Get data for each symbol
                        data = robinhood_market_researcher.analyze_stock(display_symbol)
                        if data and 'current_price' in data:
                            price = data['current_price']
                            change = 0
                            if 'prev_close' in data:
                                change = price - data['prev_close']
                                change_pct = (change / data['prev_close']) * 100
                            else:
                                change_pct = 0
                            
                            # Get indicators for summary
                            indicators = data.get('indicators', {})
                            rsi = indicators.get('rsi', 0)
                            sma_20 = indicators.get('sma_20', 0)
                            sma_50 = indicators.get('sma_50', 0)
                            
                            # Format the row
                            change_text = f"{change_pct:+.2f}%" if change_pct != 0 else "0.00%"
                            status = "UP" if change >= 0 else "DOWN"
                            
                            # Determine indicator summary
                            if rsi < 30 and sma_20 > sma_50:
                                indicator_summary = "STRONG BUY"
                            elif rsi > 70 and sma_20 < sma_50:
                                indicator_summary = "STRONG SELL"
                            elif rsi < 30:
                                indicator_summary = "BUY"
                            elif rsi > 70:
                                indicator_summary = "SELL"
                            elif sma_20 > sma_50:
                                indicator_summary = "BULLISH"
                            elif sma_20 < sma_50:
                                indicator_summary = "BEARISH"
                            else:
                                indicator_summary = "NEUTRAL"
                            
                            watchlist_text.insert(tk.END, f"{display_symbol:<10} | ", ("symbol",))
                            watchlist_text.insert(tk.END, f"${price:<9.2f} | ", ("price",))
                            
                            if change >= 0:
                                watchlist_text.insert(tk.END, f"{change_text:<9} | ", ("positive",))
                            else:
                                watchlist_text.insert(tk.END, f"{change_text:<9} | ", ("negative",))
                            
                            if status == "UP":
                                watchlist_text.insert(tk.END, f"{status:<9} | ", ("positive",))
                            else:
                                watchlist_text.insert(tk.END, f"{status:<9} | ", ("negative",))
                                
                            watchlist_text.insert(tk.END, f"{indicator_summary}\n", ("positive" if "BUY" in indicator_summary or "BULLISH" in indicator_summary else "negative" if "SELL" in indicator_summary or "BEARISH" in indicator_summary else "price"))
                        else:
                            watchlist_text.insert(tk.END, f"{display_symbol:<10} | ", ("symbol",))
                            watchlist_text.insert(tk.END, "N/A       | N/A       | N/A      | N/A\n", ("price",))
                    except Exception as e:
                        print(f"Error processing {symbol} in watchlist: {e}")
                        display_symbol = symbol[0] if isinstance(symbol, tuple) else symbol
                        watchlist_text.insert(tk.END, f"{display_symbol:<10} | ", ("symbol",))
                        watchlist_text.insert(tk.END, "N/A       | N/A       | N/A      | N/A\n", ("price",))
                
                watchlist_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Watchlist", "Your watchlist is empty")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading watchlist: {str(e)}")

    def pre_fill_question(self, question_text):
        """Pre-fill the question entry with the given text"""
        self.assistant_question_entry.delete(0, tk.END)
        self.assistant_question_entry.insert(0, question_text)
        self.assistant_question_entry.focus()

    def toggle_advanced_assistant(self):
        """Toggle advanced mode for the assistant"""
        if self.advanced_mode.get():
            print("Advanced mode enabled: Enhanced ML analysis active")
        else:
            print("Advanced mode disabled: Basic analysis active")

    def get_market_news(self, symbol: str) -> list:
        """Get market news for the symbol (simulated)"""
        # In a real implementation, this would fetch from a news API
        # For now, simulate news articles
        import random
        
        news_articles = [
            {
                "title": f"{symbol} Posts Strong Quarterly Earnings",
                "summary": f"{symbol} reports better than expected quarterly results with revenue growth of 15% year-over-year.",
                "time": "2 hours ago",
                "sentiment": "positive"
            },
            {
                "title": f"Analysts Upgrade {symbol} Following Positive Outlook",
                "summary": f"Major investment banks increase price targets for {symbol} after positive earnings call.",
                "time": "1 day ago",
                "sentiment": "positive"
            },
            {
                "title": f"Regulatory Concerns Weigh on {symbol} Stock",
                "summary": f"New regulatory challenges in key markets raise questions about {symbol}'s growth trajectory.",
                "time": "3 days ago",
                "sentiment": "negative"
            },
            {
                "title": f"{symbol} Announces Strategic Partnership",
                "summary": f"{symbol} partners with industry leader to expand its market presence.",
                "time": "1 week ago",
                "sentiment": "positive"
            }
        ]
        
        # Randomly select a few articles
        selected_articles = random.sample(news_articles, min(3, len(news_articles)))
        return selected_articles

    def display_market_news(self, symbol: str):
        """Display market news for the symbol in the assistant panel"""
        try:
            news_articles = self.get_market_news(symbol)
            
            self.assistant_text.config(state=tk.NORMAL)
            self.assistant_text.insert(tk.END, f"\n📰 LATEST NEWS FOR {symbol}:\n", ("assistant_header",))
            self.assistant_text.insert(tk.END, "-"*40 + "\n")
            
            for article in news_articles:
                sentiment_tag = "assistant_action" if article['sentiment'] == 'positive' else "assistant_caution"
                self.assistant_text.insert(tk.END, f"• {article['title']}\n", (sentiment_tag,))
                self.assistant_text.insert(tk.END, f"  {article['summary']}\n", ("assistant_response",))
                self.assistant_text.insert(tk.END, f"  ({article['time']})\n\n", ("assistant_confidence",))
            
            self.assistant_text.config(state=tk.DISABLED)
            self.assistant_text.see(tk.END)
            
        except Exception as e:
            print(f"Error displaying market news: {e}")


def main():
    root = tk.Tk()
    app = RobinhoodDarkUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
