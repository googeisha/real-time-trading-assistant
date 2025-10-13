"""
Robinhood Market Researcher - Dark UI
A comprehensive tool for analyzing stocks using technical indicators
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import robinhood_market_researcher  # Import our analysis functions


class RobinhoodBasicUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Robinhood Market Researcher - Dark Mode")
        self.root.geometry("1200x800")
        
        # Set dark theme
        self.root.configure(bg="#1e1e1e")
        
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
        
        analyze_btn = tk.Button(input_frame, text="🔍 Analyze", command=self.analyze_stock,
                               bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                               relief=tk.FLAT, padx=15)
        analyze_btn.pack(side=tk.LEFT, padx=(0, 5))
        
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
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
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
        
        # Chart tab
        self.chart_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.chart_frame, text="📈 Chart")
        
        # Add matplotlib figure for charts
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6), 
                                                      gridspec_kw={'height_ratios': [3, 1]})
        self.fig.patch.set_facecolor('#1e1e1e')
        
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
        
        tk.Label(options_control_frame, text="Expiration Date:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.expiration_entry = tk.Entry(options_control_frame, font=("Arial", 10), 
                                        bg="#2d2d2d", fg="#e0e0e0", width=12)
        self.expiration_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.expiration_entry.insert(0, "YYYY-MM-DD")
        
        get_options_btn = tk.Button(options_control_frame, text="Fetch Options", 
                                   command=self.get_options_data,
                                   bg="#9C27B0", fg="white", font=("Arial", 10),
                                   relief=tk.FLAT, padx=10)
        get_options_btn.pack(side=tk.LEFT)
        
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
        
        # AI Insights tab
        self.ai_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.ai_frame, text="🤖 AI Insights")
        
        # AI Insights content
        ai_content_frame = tk.Frame(self.ai_frame, bg="#1e1e1e")
        ai_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # AI Controls
        ai_control_frame = tk.Frame(ai_content_frame, bg="#1e1e1e")
        ai_control_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ai_control_frame, text="AI Analysis:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        analyze_ai_btn = tk.Button(ai_control_frame, text="Run AI Analysis", 
                                  command=self.run_ai_analysis,
                                  bg="#FF9800", fg="white", font=("Arial", 10),
                                  relief=tk.FLAT, padx=10)
        analyze_ai_btn.pack(side=tk.LEFT, padx=(5, 0))
        
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
        
        # Risk Management tab
        self.risk_frame = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.risk_frame, text="🛡️ Risk Management")
        
        # Risk Management content
        risk_content_frame = tk.Frame(self.risk_frame, bg="#1e1e1e")
        risk_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Risk Controls
        risk_control_frame = tk.Frame(risk_content_frame, bg="#1e1e1e")
        risk_control_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(risk_control_frame, text="Account Size ($):", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.account_size_entry = tk.Entry(risk_control_frame, font=("Arial", 10), 
                                          bg="#2d2d2d", fg="#e0e0e0", width=10)
        self.account_size_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.account_size_entry.insert(0, "100000")
        
        tk.Label(risk_control_frame, text="Risk % per Trade:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.risk_pct_entry = tk.Entry(risk_control_frame, font=("Arial", 10), 
                                      bg="#2d2d2d", fg="#e0e0e0", width=8)
        self.risk_pct_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.risk_pct_entry.insert(0, "2")
        
        tk.Label(risk_control_frame, text="Stop Loss %:", 
                font=("Arial", 10), fg="#e0e0e0", bg="#1e1e1e").pack(side=tk.LEFT)
        
        self.stop_loss_entry = tk.Entry(risk_control_frame, font=("Arial", 10), 
                                       bg="#2d2d2d", fg="#e0e0e0", width=8)
        self.stop_loss_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.stop_loss_entry.insert(0, "8")
        
        calc_position_btn = tk.Button(risk_control_frame, text="Calculate Position", 
                                     command=self.calculate_position_size,
                                     bg="#4CAF50", fg="white", font=("Arial", 10),
                                     relief=tk.FLAT, padx=10)
        calc_position_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Risk display area
        self.risk_text = scrolledtext.ScrolledText(risk_content_frame, 
                                                  bg="#2d2d2d", fg="#e0e0e0",
                                                  font=("Consolas", 10),
                                                  relief=tk.FLAT,
                                                  insertbackground="#e0e0e0")
        self.risk_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure tags for risk management
        self.risk_text.tag_configure("risk_header", font=("Arial", 12, "bold"), foreground="#FFD54F")
        self.risk_text.tag_configure("risk_calc", font=("Arial", 10), foreground="#81C784")
        self.risk_text.tag_configure("risk_warning", font=("Arial", 10, "bold"), foreground="#E57373")
        
        # Initialize with sample data
        self.display_stock_info("SPY")
        # Load initial chart
        self.root.after(1000, self.refresh_chart)  # Delay to ensure UI is ready

    def analyze_stock(self):
        """Analyze the entered stock symbol"""
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return
        
        try:
            self.display_stock_info(symbol)
            # Refresh the chart automatically after analysis
            self.root.after(500, self.refresh_chart)  # Small delay to ensure data is displayed first
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze {symbol}: {str(e)}")
    
    def display_stock_info(self, symbol):
        """Display detailed stock information"""
        try:
            # Use the analysis function from our module
            analysis = robinhood_market_researcher.analyze_stock(symbol)
            
            if analysis:
                # Clear the text area
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                
                # Display basic stock info
                self.details_text.insert(tk.END, f"📈 {symbol.upper()} - ", ("section",))
                self.details_text.insert(tk.END, f"{analysis.get('company_name', 'Company Name Unknown')}\n\n", ("normal",))
                
                # Current price with color coding
                latest_close = analysis['current_price']
                if 'prev_close' in analysis:
                    price_change = latest_close - analysis['prev_close']
                    price_change_percent = (price_change / analysis['prev_close']) * 100
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
                
                indicators = analysis['indicators']
                
                # RSI with color coding
                rsi = indicators['rsi']
                rsi_status = "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL"
                rsi_color = "green" if rsi < 30 else "red" if rsi > 70 else "normal"
                self.details_text.insert(tk.END, f"RSI (14): {rsi:.2f} ({rsi_status})\n", (rsi_color,))
                
                # Moving averages
                sma_20 = indicators['sma_20']
                sma_50 = indicators['sma_50']
                ema_12 = indicators.get('ema_12', 0)
                ema_26 = indicators.get('ema_26', 0)
                
                if sma_20 > sma_50:
                    self.details_text.insert(tk.END, f"SMA 20: ", ("normal",))
                    self.details_text.insert(tk.END, f"{sma_20:.2f}", ("green",))  # Bullish
                    self.details_text.insert(tk.END, f" | SMA 50: {sma_50:.2f}  [UP]\n")
                else:
                    self.details_text.insert(tk.END, f"SMA 20: ", ("normal",))
                    self.details_text.insert(tk.END, f"{sma_20:.2f}", ("red",))  # Bearish
                    self.details_text.insert(tk.END, f" | SMA 50: {sma_50:.2f}  [DOWN]\n")
                
                # EMA trend
                if ema_12 > ema_26:
                    self.details_text.insert(tk.END, f"EMA 12: ", ("normal",))
                    self.details_text.insert(tk.END, f"{ema_12:.2f}", ("green",))
                    self.details_text.insert(tk.END, f" | EMA 26: {ema_26:.2f}  [BULLISH]\n")
                else:
                    self.details_text.insert(tk.END, f"EMA 12: ", ("normal",))
                    self.details_text.insert(tk.END, f"{ema_12:.2f}", ("red",))
                    self.details_text.insert(tk.END, f" | EMA 26: {ema_26:.2f}  [BEARISH]\n")
                
                # MACD
                macd = indicators['macd']
                macd_signal = indicators['macd_signal']
                macd_histogram = indicators.get('macd_histogram', 0)
                if macd > macd_signal:
                    self.details_text.insert(tk.END, f"MACD: {macd:.2f} | Signal: {macd_signal:.2f} | Histogram: {macd_histogram:.2f}  [BULLISH]\n")
                else:
                    self.details_text.insert(tk.END, f"MACD: {macd:.2f} | Signal: {macd_signal:.2f} | Histogram: {macd_histogram:.2f}  [BEARISH]\n")
                
                # Bollinger Bands
                current_price = analysis['current_price']
                bb_upper = indicators['bb_upper']
                bb_lower = indicators['bb_lower']
                bb_middle = indicators['bb_middle']
                position_in_bands = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                bb_status = ""
                if current_price > bb_upper:
                    bb_status = "ABOVE UPPER BAND [ROTATE]"
                elif current_price < bb_lower:
                    bb_status = "BELOW LOWER BAND [UP]"
                elif position_in_bands > 0.8:
                    bb_status = "NEAR UPPER BAND [ROTATE]"
                elif position_in_bands < 0.2:
                    bb_status = "NEAR LOWER BAND [DOWN]"
                else:
                    bb_status = "MIDDLE BANDS"
                
                self.details_text.insert(tk.END, f"BB Upper: {bb_upper:.2f} | Middle: {bb_middle:.2f} | Lower: {bb_lower:.2f}\n")
                self.details_text.insert(tk.END, f"BB Position: {position_in_bands:.2%} ({bb_status})\n\n")
                
                # Signals with better formatting
                self.details_text.insert(tk.END, "💡 TRADING SIGNALS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                for signal in analysis['signals']:
                    if "OVERBOUGHT" in signal or "BEARISH" in signal or "SIGNAL" in signal:
                        self.details_text.insert(tk.END, f"• {signal}  [ALERT]\n", ("red",))
                    elif "OVERSOLD" in signal or "BULLISH" in signal or "BUY" in signal:
                        self.details_text.insert(tk.END, f"• {signal}  [TARGET]\n", ("green",))
                    else:
                        self.details_text.insert(tk.END, f"• {signal}\n")
                
                # Patterns
                if analysis['patterns']:
                    self.details_text.insert(tk.END, "\n🔍 CHART PATTERNS\n", ("section",))
                    self.details_text.insert(tk.END, "─" * 40 + "\n")
                    for pattern in analysis['patterns']:
                        self.details_text.insert(tk.END, f"• {pattern}\n")
                else:
                    self.details_text.insert(tk.END, "\n🔍 CHART PATTERNS\n", ("section",))
                    self.details_text.insert(tk.END, "─" * 40 + "\n")
                    self.details_text.insert(tk.END, "No specific patterns detected\n")
                
                # Risk Metrics
                self.details_text.insert(tk.END, "\n⚠️ RISK METRICS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                risk = analysis['risk_metrics']
                volatility_desc = "LOW" if risk['volatility'] < 0.02 else "MODERATE" if risk['volatility'] < 0.05 else "HIGH"
                avg_return = risk.get('avg_return', 0)
                sharpe_ratio = risk.get('sharpe_ratio', 0)
                
                self.details_text.insert(tk.END, f"Volatility: {risk['volatility']:.4f} ({volatility_desc})\n")
                self.details_text.insert(tk.END, f"Average Return: {avg_return:.4f} ({avg_return*100:.2f}%)\n")
                self.details_text.insert(tk.END, f"Sharpe Ratio: {sharpe_ratio:.4f}\n")
                
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
                
                # Overall trend summary
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
                    self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: {bull_signals} BULLISH | {bear_signals} BEARISH  [UP]\n", ("green",))
                    self.details_text.insert(tk.END, "Recommendation: POTENTIALLY BULLISH\n", ("green_bold",))
                elif bear_signals > bull_signals:
                    self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: {bull_signals} BULLISH | {bear_signals} BEARISH  [DOWN]\n", ("red",))
                    self.details_text.insert(tk.END, "Recommendation: POTENTIALLY BEARISH\n", ("red_bold",))
                else:
                    self.details_text.insert(tk.END, f"\nSIGNAL STRENGTH: {bull_signals} BULLISH | {bear_signals} BEARISH  [BALANCE]\n", ("normal",))
                    self.details_text.insert(tk.END, "Recommendation: NEUTRAL TREND\n", ("normal_bold",))
                
                # Additional insights
                self.details_text.insert(tk.END, "\n💬 ANALYST INSIGHTS\n", ("section",))
                self.details_text.insert(tk.END, "─" * 40 + "\n")
                
                # Generate insights based on current data
                insights = []
                if rsi < 30:
                    insights.append("RSI indicates potential buying opportunity (oversold)")
                elif rsi > 70:
                    insights.append("RSI indicates potential selling opportunity (overbought)")
                
                if sma_20 > sma_50:
                    insights.append("Bullish moving average crossover (Golden Cross possible)")
                elif sma_20 < sma_50:
                    insights.append("Bearish moving average crossover (Death Cross possible)")
                
                if current_price > bb_middle:
                    insights.append("Price trading above middle Bollinger Band (positive bias)")
                else:
                    insights.append("Price trading below middle Bollinger Band (negative bias)")
                
                for insight in insights:
                    self.details_text.insert(tk.END, f"• {insight}\n")
                
                if not insights:
                    self.details_text.insert(tk.END, "• No strong technical signals identified\n")
                
                self.details_text.config(state=tk.DISABLED)
            else:
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.insert(tk.END, "No data available for this stock.")
                self.details_text.config(state=tk.DISABLED)
        except Exception as e:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Error fetching data: {str(e)}")
            self.details_text.config(state=tk.DISABLED)
            print(f"Error in display_stock_info: {e}")
    
    def refresh_chart(self):
        """Refresh the stock chart with current data"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                return
            
            # Use the analyzer to get comprehensive historical data
            analyzer = robinhood_market_researcher.MarketAnalyzer()
            data = analyzer.watchlist._get_stock_data(symbol)  # Use the internal method to get data
            
            # If that doesn't work, try the API directly
            if data is None or data.empty:
                api = robinhood_market_researcher.MarketDataAPI()
                data = api.get_stock_data(symbol)
            
            if data is not None and not data.empty and len(data) > 1:
                # Clear previous plots
                self.ax1.clear()
                self.ax2.clear()
                
                # Ensure data is properly sorted by date
                data = data.sort_index()
                
                # Plot price data
                self.ax1.plot(data.index, data['Close'], label='Close Price', color='#64b5f6', linewidth=1.5)
                if 'High' in data.columns and 'Low' in data.columns:
                    self.ax1.plot(data.index, data['High'], label='High', color='#81c784', alpha=0.6, linewidth=0.8)
                    self.ax1.plot(data.index, data['Low'], label='Low', color='#e57373', alpha=0.6, linewidth=0.8)
                
                # Add moving averages
                if 'Close' in data.columns and len(data) >= 20:
                    sma20 = data['Close'].rolling(window=20).mean()
                    self.ax1.plot(data.index, sma20, label='SMA 20', color='#ffb74d', linewidth=1)
                if 'Close' in data.columns and len(data) >= 50:
                    sma50 = data['Close'].rolling(window=50).mean()
                    self.ax1.plot(data.index, sma50, label='SMA 50', color='#ba68c8', linewidth=1)
                
                self.ax1.set_title(f'{symbol} Price Chart', color='#e0e0e0', fontsize=12)
                self.ax1.set_ylabel('Price ($)', color='#e0e0e0')
                self.ax1.legend(loc='upper left', facecolor='#2d2d2d', labelcolor='#e0e0e0')
                self.ax1.grid(True, color='#444444', linestyle='--', alpha=0.6)
                self.ax1.tick_params(colors='#e0e0e0')
                
                # Plot volume if available
                if 'Volume' in data.columns:
                    self.ax2.bar(data.index, data['Volume'], color='#90a4ae', alpha=0.7)
                    self.ax2.set_ylabel('Volume', color='#e0e0e0')
                
                self.ax2.set_xlabel('Date', color='#e0e0e0')
                self.ax2.tick_params(colors='#e0e0e0', labelsize=8)
                
                # Format x-axis dates
                self.fig.autofmt_xdate()
                
                # Set background colors
                self.ax1.set_facecolor('#2d2d2d')
                self.ax2.set_facecolor('#2d2d2d')
                
                # Update canvas
                self.canvas.draw()
                print(f"Chart refreshed successfully for {symbol} with {len(data)} data points")
            else:
                # Create a simple chart as fallback
                import matplotlib.dates as mdates
                self.ax1.clear()
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
                print(f"Chart fallback displayed for {symbol}")
                
        except Exception as e:
            print(f"Error in refresh_chart: {e}")
            # Create a simple fallback chart
            self.ax1.clear()
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
            messagebox.showerror("Chart Error", f"Error refreshing chart: {str(e)}")
    
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
        """Get and display options chain data"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol")
                return
            
            expiration = self.expiration_entry.get().strip()
            if expiration == "YYYY-MM-DD":
                expiration = None  # Use default
            
            # Get options data
            options_data = robinhood_market_researcher.get_options_data(symbol, expiration)
            
            if options_data:
                self.options_text.config(state=tk.NORMAL)
                self.options_text.delete(1.0, tk.END)
                
                # Display options data
                self.options_text.insert(tk.END, f"期权 Chain for {symbol}\n", ("header",))
                self.options_text.insert(tk.END, f"Expiration: {options_data['expiration_date']}\n", ("header",))
                self.options_text.insert(tk.END, f"Current Price: ${options_data['current_price']:.2f}\n\n", ("header",))
                
                # Display calls
                self.options_text.insert(tk.END, "CALLS:\n", ("header",))
                self.options_text.insert(tk.END, f"{'Strike':<8} {'Bid':<8} {'Ask':<8} {'Last':<8} {'Vol':<8} {'OI':<10} {'IV':<8} {'Delta':<8}\n", ("header",))
                self.options_text.insert(tk.END, "-"*70 + "\n")
                
                for call in options_data['calls']:
                    self.options_text.insert(tk.END, f"{call['strike']:<8.2f} ")
                    self.options_text.insert(tk.END, f"{call['bid']:<8.2f} ", ("call",))
                    self.options_text.insert(tk.END, f"{call['ask']:<8.2f} ", ("call",))
                    self.options_text.insert(tk.END, f"{call['last']:<8.2f} ", ("call",))
                    self.options_text.insert(tk.END, f"{call['volume']:<8} ", ("call",))
                    self.options_text.insert(tk.END, f"{call['open_interest']:<10} ", ("call",))
                    self.options_text.insert(tk.END, f"{call['iv']*100:<7.2f}% ", ("call",))
                    self.options_text.insert(tk.END, f"{call['delta']:<8.3f} ", ("call",))
                    self.options_text.insert(tk.END, "\n")
                
                # Display puts
                self.options_text.insert(tk.END, "\n\nPUTS:\n", ("header",))
                self.options_text.insert(tk.END, f"{'Strike':<8} {'Bid':<8} {'Ask':<8} {'Last':<8} {'Vol':<8} {'OI':<10} {'IV':<8} {'Delta':<8}\n", ("header",))
                self.options_text.insert(tk.END, "-"*70 + "\n")
                
                for put in options_data['puts']:
                    self.options_text.insert(tk.END, f"{put['strike']:<8.2f} ")
                    self.options_text.insert(tk.END, f"{put['bid']:<8.2f} ", ("put",))
                    self.options_text.insert(tk.END, f"{put['ask']:<8.2f} ", ("put",))
                    self.options_text.insert(tk.END, f"{put['last']:<8.2f} ", ("put",))
                    self.options_text.insert(tk.END, f"{put['volume']:<8} ", ("put",))
                    self.options_text.insert(tk.END, f"{put['open_interest']:<10} ", ("put",))
                    self.options_text.insert(tk.END, f"{put['iv']*100:<7.2f}% ", ("put",))
                    self.options_text.insert(tk.END, f"{put['delta']:<8.3f} ", ("put",))
                    self.options_text.insert(tk.END, "\n")
                
                self.options_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", f"No options data available for {symbol}")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting options data: {str(e)}")
    
    def get_options_strategies(self):
        """Get suggested options strategies"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol")
                return
            
            strategies = robinhood_market_researcher.get_options_strategies(symbol)
            
            if strategies:
                # For now, just display in the main details tab
                self.details_text.config(state=tk.NORMAL)
                self.details_text.insert(tk.END, f"\n\n🎯 OPTIONS STRATEGIES for {symbol}\n", ("section",))
                self.details_text.insert(tk.END, "─" * 50 + "\n")
                
                for strat in strategies:
                    self.details_text.insert(tk.END, f"Strategy: {strat['strategy']}\n", ("green_bold",))
                    self.details_text.insert(tk.END, f"Description: {strat['description']}\n", ("normal",))
                    self.details_text.insert(tk.END, f"Risk: {strat['risk']}\n", ("normal",))
                    self.details_text.insert(tk.END, f"Target: {strat['target']}\n\n", ("normal",))
                
                self.details_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Info", f"No strategies available for {symbol}")
        except Exception as e:
            messagebox.showerror("Error", f"Error getting options strategies: {str(e)}")

    def run_ai_analysis(self):
        """Run AI analysis on the current stock"""
        try:
            symbol = self.symbol_entry.get().strip().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a stock symbol")
                return

            # Get stock analysis data
            analysis = robinhood_market_researcher.analyze_stock(symbol)
            
            if analysis:
                # Clear the AI text area
                self.ai_text.config(state=tk.NORMAL)
                self.ai_text.delete(1.0, tk.END)
                
                # Generate AI insights
                analyzer = robinhood_market_researcher.MarketAnalyzer()
                ai_insights = analyzer.generate_ai_insights(symbol, analysis)
                
                # Display AI insights
                self.ai_text.insert(tk.END, ai_insights, ("ai_neutral",))
                
                # Disable text area to prevent editing
                self.ai_text.config(state=tk.DISABLED)
            else:
                self.ai_text.config(state=tk.NORMAL)
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, f"No data available for {symbol}.", ("ai_warning",))
                self.ai_text.config(state=tk.DISABLED)
                
        except Exception as e:
            self.ai_text.config(state=tk.NORMAL)
            self.ai_text.delete(1.0, tk.END)
            self.ai_text.insert(tk.END, f"Error running AI analysis: {str(e)}", ("ai_warning",))
            self.ai_text.config(state=tk.DISABLED)
            print(f"Error in run_ai_analysis: {e}")

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
            data = robinhood_market_researcher.analyze_stock(symbol)
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
                watchlist_window.geometry("600x400")
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
                watchlist_text.insert(tk.END, "SYMBOL    |  PRICE  |  CHANGE  |  STATUS\n", ("symbol",))
                watchlist_text.insert(tk.END, "-"*50 + "\n")
                
                for symbol in watchlist_symbols:
                    try:
                        # Get data for each symbol
                        data = robinhood_market_researcher.analyze_stock(symbol)
                        if data and 'current_price' in data:
                            price = data['current_price']
                            change = 0
                            if 'prev_close' in data:
                                change = price - data['prev_close']
                                change_pct = (change / data['prev_close']) * 100
                            else:
                                change_pct = 0
                            
                            # Format the row
                            change_text = f"{change_pct:+.2f}%" if change_pct != 0 else "0.00%"
                            status = "UP" if change >= 0 else "DOWN"
                            
                            watchlist_text.insert(tk.END, f"{symbol:<10} | ", ("symbol",))
                            watchlist_text.insert(tk.END, f"${price:.2f}", ("price",))
                            watchlist_text.insert(tk.END, " | ")
                            
                            if change >= 0:
                                watchlist_text.insert(tk.END, f"{change_text:>8}", ("positive",))
                            else:
                                watchlist_text.insert(tk.END, f"{change_text:>8}", ("negative",))
                            
                            watchlist_text.insert(tk.END, " | ")
                            if status == "UP":
                                watchlist_text.insert(tk.END, f"{status:>6} 📈\n", ("positive",))
                            else:
                                watchlist_text.insert(tk.END, f"{status:>6} 📉\n", ("negative",))
                        else:
                            watchlist_text.insert(tk.END, f"{symbol:<10} | ", ("symbol",))
                            watchlist_text.insert(tk.END, "N/A      | N/A      | N/A\n", ("price",))
                    except Exception:
                        watchlist_text.insert(tk.END, f"{symbol:<10} | ", ("symbol",))
                        watchlist_text.insert(tk.END, "N/A      | N/A      | N/A\n", ("price",))
                
                watchlist_text.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Watchlist", "Your watchlist is empty")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading watchlist: {str(e)}")

def main():
    root = tk.Tk()
    app = RobinhoodBasicUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()