"""
Dark-Themed Robinhood-Style Trading Assistant UI
A sleek black and blue themed interface for monitoring your watchlist with enhanced charts
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import pandas as pd
from datetime import datetime
import json
import sqlite3
from robinhood_market_researcher import MarketAnalyzer

# Import matplotlib for charts
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

class DarkRobinhoodStyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dark Robinhood-Style Trading Assistant")
        self.root.geometry("1400x800")
        self.root.configure(bg="#121212")  # Dark background
        
        # Initialize analyzer
        self.analyzer = MarketAnalyzer()
        
        # Configure styles to match dark theme
        self.configure_styles()
        
        # Create the interface
        self.create_widgets()
        
        # Load initial watchlist
        self.load_watchlist()
        
        # Start periodic updates
        self.update_dashboard()
        
    def configure_styles(self):
        """Configure styles to match dark theme with blue accents"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles for dark theme
        style.configure("Dark.TFrame", background="#1e1e1e")
        style.configure("Blue.TFrame", background="#0a0a23")  # Dark blue
        style.configure("Card.TFrame", background="#252526", relief="flat", borderwidth=1)
        style.configure("Section.TFrame", background="#2d2d30", relief="solid", borderwidth=1)
        
        style.configure("Dark.TLabel", background="#1e1e1e", foreground="#e0e0e0", font=("Arial", 10))
        style.configure("Header.TLabel", background="#1e1e1e", foreground="#64b5f6", font=("Arial", 16, "bold"))  # Light blue
        style.configure("Title.TLabel", background="#2d2d30", foreground="#64b5f6", font=("Arial", 12, "bold"))  # Light blue title
        style.configure("Subtitle.TLabel", background="#1e1e1e", foreground="#9e9e9e", font=("Arial", 9))
        style.configure("Green.TLabel", background="#2d2d30", foreground="#4caf50", font=("Arial", 10, "bold"))
        style.configure("Red.TLabel", background="#2d2d30", foreground="#f44336", font=("Arial", 10, "bold"))
        
        # Configure ttk widgets to match dark theme
        style.configure("TButton", background="#0d47a1", foreground="#ffffff", font=("Arial", 10, "bold"))
        style.map("TButton", background=[('active', '#1565c0')])
        
        style.configure("TListbox", background="#2d2d2d", foreground="#e0e0e0", selectbackground="#1976d2", selectforeground="white")
        
        # Configure the root background
        style.configure("TFrame", background="#121212")
        
    def create_widgets(self):
        """Create the main interface widgets with dark theme"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style="Dark.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="🌙 Dark Robinhood-Style Trading Assistant", 
            style="Header.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self.header_frame, style="Dark.TFrame")
        self.controls_frame.pack(side=tk.RIGHT)
        
        self.refresh_btn = ttk.Button(
            self.controls_frame,
            text="🔄 Refresh",
            command=self.update_dashboard
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add stock button
        self.add_stock_btn = ttk.Button(
            self.controls_frame,
            text="➕ Add Stock",
            command=self.add_stock_to_watchlist
        )
        self.add_stock_btn.pack(side=tk.LEFT)
        
        # Dashboard container
        self.dashboard_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel container
        self.left_panel = ttk.Frame(self.dashboard_frame, style="Dark.TFrame")
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Watchlist section
        self.watchlist_section = ttk.Frame(self.left_panel, style="Section.TFrame")
        self.watchlist_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Watchlist title
        ttk.Label(
            self.watchlist_section,
            text="📊 YOUR WATCHLIST",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # Stock list
        self.stock_listbox = tk.Listbox(
            self.watchlist_section,
            font=("Arial", 11),
            borderwidth=0,
            highlightthickness=0,
            selectbackground="#1976d2",  # Blue selection
            selectforeground="white",
            height=8,
            bg="#2d2d2d",  # Dark background
            fg="#e0e0e0",  # Light text
            relief="flat",
            highlightbackground="#2d2d2d"
        )
        self.stock_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Button frame for watchlist controls
        self.watchlist_btn_frame = ttk.Frame(self.watchlist_section, style="Dark.TFrame")
        self.watchlist_btn_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.remove_btn = ttk.Button(
            self.watchlist_btn_frame,
            text="❌ Remove Selected",
            command=self.remove_stock_from_watchlist
        )
        self.remove_btn.pack(side=tk.RIGHT)
        
        # Stock details section
        self.details_section = ttk.Frame(self.left_panel, style="Section.TFrame")
        self.details_section.pack(fill=tk.BOTH, expand=True)
        
        # Details title
        ttk.Label(
            self.details_section,
            text="📈 STOCK DETAILS",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # Stock details text area with dark theme
        self.details_text = tk.Text(
            self.details_section,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED,
            height=12,
            padx=5,
            pady=5,
            bg="#2d2d2d",  # Dark background
            fg="#e0e0e0",  # Light text
            selectbackground="#1976d2",  # Blue selection
            insertbackground="#e0e0e0"  # Light cursor
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar for details
        details_scrollbar = ttk.Scrollbar(self.details_section, command=self.details_text.yview)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=5)
        self.details_text.config(yscrollcommand=details_scrollbar.set)
        
        # Right panel - Charts and Analysis
        self.right_panel = ttk.Frame(self.dashboard_frame, style="Dark.TFrame")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Chart section
        self.chart_section = ttk.Frame(self.right_panel, style="Section.TFrame")
        self.chart_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chart title
        ttk.Label(
            self.chart_section,
            text="📊 PRICE CHART",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # Create matplotlib figure for chart with dark theme
        self.fig = Figure(figsize=(6, 3.5), dpi=100, facecolor='#1e1e1e', edgecolor='none')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')
        self.ax.set_title("Stock Price Chart", color='white')
        self.ax.set_xlabel("Time", color='white')
        self.ax.set_ylabel("Price ($)", color='white')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, color='#444444', alpha=0.5)
        
        # Create canvas for the chart
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_section)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create a second figure for volume and RSI with dark theme
        self.fig2 = Figure(figsize=(6, 2.5), dpi=100, facecolor='#1e1e1e', edgecolor='none')
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_facecolor('#1e1e1e')
        self.ax2.set_title("Volume & RSI", color='white')
        self.ax2.set_xlabel("Time", color='white')
        self.ax2.set_ylabel("Volume", color='white')
        self.ax2.tick_params(colors='white')
        self.ax2.grid(True, color='#444444', alpha=0.5)
        
        # Create canvas for the second chart
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.chart_section)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 5))
        
        # Analysis section
        self.analysis_section = ttk.Frame(self.right_panel, style="Section.TFrame")
        self.analysis_section.pack(fill=tk.BOTH, expand=True)
        
        # Analysis title
        ttk.Label(
            self.analysis_section,
            text="💡 MARKET ANALYSIS",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # Analysis text area with dark theme
        self.analysis_text = tk.Text(
            self.analysis_section,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED,
            padx=5,
            pady=5,
            bg="#2d2d2d",  # Dark background
            fg="#e0e0e0",  # Light text
            selectbackground="#1976d2",  # Blue selection
            insertbackground="#e0e0e0"  # Light cursor
        )
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar for analysis
        analysis_scrollbar = ttk.Scrollbar(self.analysis_section, command=self.analysis_text.yview)
        analysis_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=5)
        self.analysis_text.config(yscrollcommand=analysis_scrollbar.set)
        
        # Bind selection event to update details and chart
        self.stock_listbox.bind('<<ListboxSelect>>', self.on_stock_select)
    
    def load_watchlist(self):
        """Load watchlist from database"""
        self.stock_listbox.delete(0, tk.END)
        watchlist = self.analyzer.watchlist.get_watchlist()
        for stock in watchlist:
            self.stock_listbox.insert(tk.END, stock)
    
    def add_stock_to_watchlist(self):
        """Add a new stock to the watchlist"""
        symbol = simpledialog.askstring("Add Stock", "Enter stock symbol:")
        if symbol:
            symbol = symbol.strip().upper()
            if symbol and len(symbol) <= 5:
                self.analyzer.add_to_watchlist(symbol)
                self.load_watchlist()
                messagebox.showinfo("Success", f"Added {symbol} to your watchlist!")
            else:
                messagebox.showerror("Error", "Please enter a valid stock symbol (1-5 characters)")
    
    def remove_stock_from_watchlist(self):
        """Remove selected stock from watchlist"""
        selection = self.stock_listbox.curselection()
        if selection:
            symbol = self.stock_listbox.get(selection[0])
            result = messagebox.askyesno("Confirm", f"Remove {symbol} from watchlist?")
            if result:
                import sqlite3
                conn = sqlite3.connect("watchlist.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
                conn.commit()
                conn.close()
                self.load_watchlist()
        else:
            messagebox.showinfo("Info", "Please select a stock to remove")
    
    def on_stock_select(self, event):
        """Handle stock selection to update details and chart"""
        selection = self.stock_listbox.curselection()
        if selection:
            symbol = self.stock_listbox.get(selection[0])
            self.update_stock_details(symbol)
            self.update_chart(symbol)
    
    def update_stock_details(self, symbol):
        """Update the stock details panel for the selected stock"""
        # Get fresh data for the stock
        watchlist_data = self.analyzer.watchlist.get_watchlist_data()
        
        if symbol in watchlist_data:
            data = watchlist_data[symbol]
            latest_close = data['Close'].iloc[-1] if len(data) > 0 else 0
            
            # Get analysis
            analysis = self.analyzer.analyze_stock(symbol, data)
            
            # Update details text
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            
            # Add colored indicators based on price movement
            prev_close = data['Close'].iloc[-2] if len(data) > 1 else latest_close
            price_change = latest_close - prev_close
            price_change_percent = (price_change / prev_close) * 100 if prev_close != 0 else 0
            
            self.details_text.insert(tk.END, f"Selected Stock: {symbol}\n")
            
            # Color-code the price based on movement
            if price_change >= 0:
                self.details_text.insert(tk.END, f"Current Price: ", ("normal",))
                self.details_text.insert(tk.END, f"${latest_close:.2f}", ("green",))
                self.details_text.insert(tk.END, f" (+{price_change_percent:.2f}%)\n", ("green",))
            else:
                self.details_text.insert(tk.END, f"Current Price: ", ("normal",))
                self.details_text.insert(tk.END, f"${latest_close:.2f}", ("red",))
                self.details_text.insert(tk.END, f" ({price_change_percent:.2f}%)\n", ("red",))
            
            self.details_text.insert(tk.END, "\n")
            
            # Technical Indicators with color coding
            self.details_text.insert(tk.END, "📊 TECHNICAL INDICATORS\n", ("section",))
            self.details_text.insert(tk.END, "="*30 + "\n")
            
            indicators = analysis['indicators']
            
            # RSI with color coding
            rsi = indicators['rsi']
            if rsi > 70:
                self.details_text.insert(tk.END, f"RSI: ", ("normal",))
                self.details_text.insert(tk.END, f"{rsi:.2f}", ("red",))  # Overbought
                self.details_text.insert(tk.END, " (OVERBOUGHT)\n")
            elif rsi < 30:
                self.details_text.insert(tk.END, f"RSI: ", ("normal",))
                self.details_text.insert(tk.END, f"{rsi:.2f}", ("green",))  # Oversold
                self.details_text.insert(tk.END, " (OVERSOLD)\n")
            else:
                self.details_text.insert(tk.END, f"RSI: {rsi:.2f}\n")
            
            # Moving averages comparison
            sma_20 = indicators['sma_20']
            sma_50 = indicators['sma_50']
            if sma_20 > sma_50:
                self.details_text.insert(tk.END, f"SMA 20: ", ("normal",))
                self.details_text.insert(tk.END, f"{sma_20:.2f}", ("green",))  # Bullish
                self.details_text.insert(tk.END, f" | SMA 50: {sma_50:.2f}\n")
            else:
                self.details_text.insert(tk.END, f"SMA 20: ", ("normal",))
                self.details_text.insert(tk.END, f"{sma_20:.2f}", ("red",))  # Bearish
                self.details_text.insert(tk.END, f" | SMA 50: {sma_50:.2f}\n")
            
            # MACD
            self.details_text.insert(tk.END, f"MACD: {indicators['macd']:.2f}\n")
            # Bollinger Bands
            self.details_text.insert(tk.END, f"BB Upper: {indicators['bb_upper']:.2f}\n")
            self.details_text.insert(tk.END, f"BB Middle: {indicators['bb_middle']:.2f}\n")
            self.details_text.insert(tk.END, f"BB Lower: {indicators['bb_lower']:.2f}\n\n")
            
            # Signals with color coding
            self.details_text.insert(tk.END, "💡 TRADING SIGNALS\n", ("section",))
            self.details_text.insert(tk.END, "="*30 + "\n")
            for signal in analysis['signals']:
                if "OVERBOUGHT" in signal or "BEARISH" in signal or "SIGNAL" in signal:
                    self.details_text.insert(tk.END, f"• {signal}\n", ("red",))
                elif "OVERSOLD" in signal or "BULLISH" in signal or "BUY" in signal:
                    self.details_text.insert(tk.END, f"• {signal}\n", ("green",))
                else:
                    self.details_text.insert(tk.END, f"• {signal}\n")
            
            # Patterns
            if analysis['patterns']:
                self.details_text.insert(tk.END, "\n🔍 CHART PATTERNS\n", ("section",))
                self.details_text.insert(tk.END, "="*30 + "\n")
                for pattern in analysis['patterns']:
                    self.details_text.insert(tk.END, f"• {pattern}\n")
            
            # Risk Metrics
            self.details_text.insert(tk.END, "\n⚠️ RISK METRICS\n", ("section",))
            self.details_text.insert(tk.END, "="*30 + "\n")
            risk = analysis['risk_metrics']
            self.details_text.insert(tk.END, f"Volatility: {risk['volatility']:.4f}\n")
            
            # Configure tags for color coding
            self.details_text.tag_configure("green", foreground="#4caf50", font=("Arial", 10, "bold"))
            self.details_text.tag_configure("red", foreground="#f44336", font=("Arial", 10, "bold"))
            self.details_text.tag_configure("normal", font=("Arial", 10), foreground="#e0e0e0")
            self.details_text.tag_configure("section", font=("Arial", 10, "bold"), foreground="#64b5f6")  # Light blue
            
            self.details_text.config(state=tk.DISABLED)
        else:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, "No data available for this stock.")
            self.details_text.config(state=tk.DISABLED)
    
    def update_chart(self, symbol):
        """Update the chart for the selected stock with dark theme"""
        # Get fresh data for the stock
        watchlist_data = self.analyzer.watchlist.get_watchlist_data()
        
        if symbol in watchlist_data:
            data = watchlist_data[symbol]
            
            # Limit data to last 50 points for better visualization
            if len(data) > 50:
                data = data.tail(50)
            
            # Clear the main chart
            self.ax.clear()
            self.ax.set_facecolor('#1e1e1e')
            self.ax.grid(True, color='#444444', alpha=0.5)
            
            # Plot the price data
            self.ax.plot(data.index, data['Close'], label='Close Price', color='#4caf50', linewidth=2)  # Green
            self.ax.plot(data.index, data['Open'], label='Open Price', color='#2196f3', alpha=0.7, linestyle='--')  # Blue
            
            # Add moving averages if available
            try:
                analysis = self.analyzer.analyze_stock(symbol, watchlist_data[symbol])
                indicators = analysis['indicators']
                
                # Calculate SMAs for the current data range
                close_prices = data['Close']
                sma_20 = close_prices.rolling(window=20).mean()
                sma_50 = close_prices.rolling(window=50).mean()
                
                # Only plot if we have enough data points
                if len(sma_20.dropna()) > 0:
                    self.ax.plot(data.index, sma_20, label='SMA 20', color='#ff9800', alpha=0.8)  # Orange
                if len(sma_50.dropna()) > 0 and len(data) >= 50:
                    self.ax.plot(data.index, sma_50, label='SMA 50', color='#f44336', alpha=0.8)  # Red
                    
                # Add Bollinger Bands
                bb_upper, bb_middle, bb_lower = self.analyzer.indicators.calculate_bollinger_bands(close_prices)
                self.ax.fill_between(data.index, bb_upper, bb_lower, alpha=0.1, color='#9e9e9e')
                self.ax.plot(data.index, bb_middle, label='BB Middle', color='#9e9e9e', alpha=0.7)
            except:
                pass  # If analysis fails, continue without additional indicators
            
            self.ax.set_title(f"{symbol} - Price Chart", color='white')
            self.ax.set_xlabel("Time", color='white')
            self.ax.set_ylabel("Price ($)", color='white')
            self.ax.tick_params(colors='white')
            self.ax.legend()
            
            # Improve x-axis formatting
            self.fig.autofmt_xdate()
            
            # Redraw the main canvas
            self.canvas.draw()
            
            # Clear and update the second chart (Volume and RSI)
            self.ax2.clear()
            self.ax2.set_facecolor('#1e1e1e')
            self.ax2.grid(True, color='#444444', alpha=0.5)
            
            # Calculate RSI for the volume chart
            rsi = self.analyzer.indicators.calculate_rsi(data['Close'])
            
            # Create subplots for volume and RSI
            ax_rsi = self.ax2.twinx()  # Create a second y-axis
            ax_rsi.set_facecolor('#1e1e1e')
            
            # Plot volume bars
            bars = self.ax2.bar(data.index, data['Volume'], alpha=0.3, color='#2196f3', label='Volume')  # Blue
            
            # Plot RSI
            rsi_data = rsi[-len(data):]  # Align with the current data range
            line_rsi = ax_rsi.plot(data.index, rsi_data, color='#e91e63', label='RSI', linewidth=2)  # Pink
            
            # Add RSI threshold lines
            ax_rsi.axhline(y=70, color='#f44336', linestyle='--', alpha=0.5, label='Overbought')  # Red
            ax_rsi.axhline(y=30, color='#4caf50', linestyle='--', alpha=0.5, label='Oversold')  # Green
            
            # Set labels with color matching
            self.ax2.set_xlabel("Time", color='white')
            self.ax2.set_ylabel("Volume", color='#2196f3')  # Blue
            ax_rsi.set_ylabel("RSI", color='#e91e63')  # Pink
            
            # Set y-limits for RSI
            ax_rsi.set_ylim(0, 100)
            
            # Set tick colors
            self.ax2.tick_params(colors='white')
            ax_rsi.tick_params(colors='white')
            
            # Set title
            self.ax2.set_title(f"{symbol} - Volume & RSI", color='white')
            
            # Draw the second canvas
            self.canvas2.draw()
            
        else:
            # Clear the chart if no data is available
            self.ax.clear()
            self.ax.set_facecolor('#1e1e1e')
            self.ax.text(0.5, 0.5, 'No data available', horizontalalignment='center', 
                        verticalalignment='center', transform=self.ax.transAxes, color='white')
            self.ax.set_title(f"{symbol} - Price Chart", color='white')
            self.ax.tick_params(colors='white')
            self.canvas.draw()
            
            # Clear the second chart if no data is available
            self.ax2.clear()
            self.ax2.set_facecolor('#1e1e1e')
            self.ax2.text(0.5, 0.5, 'No data available', horizontalalignment='center', 
                         verticalalignment='center', transform=self.ax2.transAxes, color='white')
            self.ax2.set_title(f"{symbol} - Volume & RSI", color='white')
            self.ax2.tick_params(colors='white')
            self.canvas2.draw()
    
    def update_dashboard(self):
        """Update the dashboard with fresh analysis"""
        # Get analysis for selected stock if one is selected
        selection = self.stock_listbox.curselection()
        if selection:
            symbol = self.stock_listbox.get(selection[0])
            watchlist_data = self.analyzer.watchlist.get_watchlist_data()
            
            if symbol in watchlist_data:
                data = watchlist_data[symbol]
                analysis = self.analyzer.analyze_stock(symbol, data)
                insights = self.analyzer.generate_ai_insights(symbol, analysis)
                
                # Update analysis text with AI insights
                self.analysis_text.config(state=tk.NORMAL)
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, f"🤖 AI Insights for {symbol}\n\n")
                self.analysis_text.insert(tk.END, insights)
                
                # Configure tags for better visual indicators in analysis
                self.analysis_text.tag_configure("bullish", foreground="#4caf50", font=("Arial", 10, "bold"))
                self.analysis_text.tag_configure("bearish", foreground="#f44336", font=("Arial", 10, "bold"))
                
                # Apply tags based on keywords
                content = self.analysis_text.get(1.0, tk.END)
                for i, line in enumerate(content.split('\n')):
                    if 'BULLISH' in line or 'BUY' in line or 'oversold' in line.lower() or '🟢' in line:
                        start_pos = f"{i+1}.0"
                        end_pos = f"{i+1}.end"
                        self.analysis_text.tag_add("bullish", start_pos, end_pos)
                    elif 'BEARISH' in line or 'SELL' in line or 'overbought' in line.lower() or '🔴' in line:
                        start_pos = f"{i+1}.0"
                        end_pos = f"{i+1}.end"
                        self.analysis_text.tag_add("bearish", start_pos, end_pos)
                
                self.analysis_text.config(state=tk.DISABLED)
            else:
                # If no data for selected stock, show general summary
                summary = self.analyzer.get_analysis_summary()
                self.analysis_text.config(state=tk.NORMAL)
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.analysis_text.insert(tk.END, "="*50 + "\n\n")
                self.analysis_text.insert(tk.END, summary)
                self.analysis_text.config(state=tk.DISABLED)
        else:
            # Show general summary
            summary = self.analyzer.get_analysis_summary()
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.analysis_text.insert(tk.END, "="*50 + "\n\n")
            self.analysis_text.insert(tk.END, summary)
            self.analysis_text.config(state=tk.DISABLED)
        
        # Reload watchlist in case it changed
        self.load_watchlist()
        
        # Update chart for selected stock if one is selected
        if selection:
            symbol = self.stock_listbox.get(selection[0])
            self.update_chart(symbol)
            self.update_stock_details(symbol)
        
        # Schedule next update (every 30 seconds)
        self.root.after(30000, self.update_dashboard)

def main():
    root = tk.Tk()
    app = DarkRobinhoodStyleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()