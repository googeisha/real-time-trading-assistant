"""
Enhanced Robinhood-Style Trading Assistant UI
A clean, modern interface for monitoring your watchlist with Robinhood-inspired design and charts
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

class RobinhoodStyleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Robinhood-Style Trading Assistant")
        self.root.geometry("1400x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize analyzer
        self.analyzer = MarketAnalyzer()
        
        # Configure styles to match Robinhood
        self.configure_styles()
        
        # Create the interface
        self.create_widgets()
        
        # Load initial watchlist
        self.load_watchlist()
        
        # Start periodic updates
        self.update_dashboard()
        
    def configure_styles(self):
        """Configure styles to match Robinhood's clean design"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure("Robinhood.TFrame", background="#ffffff")
        style.configure("Robinhood.TLabel", background="#ffffff", foreground="#212121", font=("Arial", 10))
        style.configure("Header.TLabel", background="#ffffff", foreground="#212121", font=("Arial", 16, "bold"))
        style.configure("Title.TLabel", background="#ffffff", foreground="#00c800", font=("Arial", 12, "bold"))
        style.configure("Subtitle.TLabel", background="#ffffff", foreground="#757575", font=("Arial", 9))
        style.configure("Card.TFrame", background="#ffffff", relief="flat", borderwidth=1)
        style.configure("Box.TFrame", background="#ffffff", relief="solid", borderwidth=1)
        style.configure("Section.TFrame", background="#f9f9f9", relief="solid", borderwidth=1)
        style.configure("Green.TLabel", background="#ffffff", foreground="#00c800", font=("Arial", 10, "bold"))
        style.configure("Red.TLabel", background="#ffffff", foreground="#f44336", font=("Arial", 10, "bold"))
        
    def create_widgets(self):
        """Create the main interface widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style="Robinhood.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame, style="Robinhood.TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="📈 Enhanced Robinhood-Style Trading Assistant", 
            style="Header.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self.header_frame, style="Robinhood.TFrame")
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
        self.dashboard_frame = ttk.Frame(self.main_frame, style="Robinhood.TFrame")
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel container
        self.left_panel = ttk.Frame(self.dashboard_frame, style="Robinhood.TFrame")
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
            selectbackground="#00c800",
            selectforeground="white",
            height=8
        )
        self.stock_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Button frame for watchlist controls
        self.watchlist_btn_frame = ttk.Frame(self.watchlist_section, style="Robinhood.TFrame")
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
        
        # Stock details text area
        self.details_text = tk.Text(
            self.details_section,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED,
            height=12
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar for details
        details_scrollbar = ttk.Scrollbar(self.details_section, command=self.details_text.yview)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=5)
        self.details_text.config(yscrollcommand=details_scrollbar.set)
        
        # Right panel - Charts and Analysis
        self.right_panel = ttk.Frame(self.dashboard_frame, style="Robinhood.TFrame")
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
        
        # Create matplotlib figure for chart
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Stock Price Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price ($)")
        
        # Create canvas for the chart
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_section)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Analysis section
        self.analysis_section = ttk.Frame(self.right_panel, style="Section.TFrame")
        self.analysis_section.pack(fill=tk.BOTH, expand=True)
        
        # Analysis title
        ttk.Label(
            self.analysis_section,
            text="💡 MARKET ANALYSIS",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=10, pady=(5, 5))
        
        # Analysis text area
        self.analysis_text = tk.Text(
            self.analysis_section,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED
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
            
            self.details_text.insert(tk.END, f"Selected Stock: {symbol}\n")
            self.details_text.insert(tk.END, f"Current Price: ${latest_close:.2f}\n\n")
            
            # Technical Indicators
            self.details_text.insert(tk.END, "📊 TECHNICAL INDICATORS\n")
            self.details_text.insert(tk.END, "="*30 + "\n")
            
            indicators = analysis['indicators']
            self.details_text.insert(tk.END, f"RSI: {indicators['rsi']:.2f}\n")
            self.details_text.insert(tk.END, f"SMA 20: {indicators['sma_20']:.2f}\n")
            self.details_text.insert(tk.END, f"SMA 50: {indicators['sma_50']:.2f}\n")
            self.details_text.insert(tk.END, f"MACD: {indicators['macd']:.2f}\n")
            self.details_text.insert(tk.END, f"BB Upper: {indicators['bb_upper']:.2f}\n")
            self.details_text.insert(tk.END, f"BB Middle: {indicators['bb_middle']:.2f}\n")
            self.details_text.insert(tk.END, f"BB Lower: {indicators['bb_lower']:.2f}\n\n")
            
            # Signals
            self.details_text.insert(tk.END, "💡 TRADING SIGNALS\n")
            self.details_text.insert(tk.END, "="*30 + "\n")
            for signal in analysis['signals']:
                self.details_text.insert(tk.END, f"• {signal}\n")
            
            # Patterns
            if analysis['patterns']:
                self.details_text.insert(tk.END, "\n🔍 CHART PATTERNS\n")
                self.details_text.insert(tk.END, "="*30 + "\n")
                for pattern in analysis['patterns']:
                    self.details_text.insert(tk.END, f"• {pattern}\n")
            
            # Risk Metrics
            self.details_text.insert(tk.END, "\n⚠️ RISK METRICS\n")
            self.details_text.insert(tk.END, "="*30 + "\n")
            risk = analysis['risk_metrics']
            self.details_text.insert(tk.END, f"Volatility: {risk['volatility']:.4f}\n")
            
            self.details_text.config(state=tk.DISABLED)
        else:
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, "No data available for this stock.")
            self.details_text.config(state=tk.DISABLED)
    
    def update_chart(self, symbol):
        """Update the chart for the selected stock"""
        # Get fresh data for the stock
        watchlist_data = self.analyzer.watchlist.get_watchlist_data()
        
        if symbol in watchlist_data:
            data = watchlist_data[symbol]
            
            # Limit data to last 50 points for better visualization
            if len(data) > 50:
                data = data.tail(50)
            
            # Clear the previous chart
            self.ax.clear()
            
            # Plot the price data
            self.ax.plot(data.index, data['Close'], label='Close Price', color='#00c800', linewidth=2)
            self.ax.plot(data.index, data['Open'], label='Open Price', color='#0088cc', alpha=0.7, linestyle='--')
            
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
                    self.ax.plot(data.index, sma_20, label='SMA 20', color='orange', alpha=0.7)
                if len(sma_50.dropna()) > 0 and len(data) >= 50:
                    self.ax.plot(data.index, sma_50, label='SMA 50', color='red', alpha=0.7)
            except:
                pass  # If analysis fails, continue without moving averages
            
            self.ax.set_title(f"{symbol} - Price Chart")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Price ($)")
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Improve x-axis formatting
            self.fig.autofmt_xdate()
            
            # Redraw the canvas
            self.canvas.draw()
        else:
            # Clear the chart if no data is available
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No data available', horizontalalignment='center', 
                        verticalalignment='center', transform=self.ax.transAxes)
            self.ax.set_title(f"{symbol} - Price Chart")
            self.canvas.draw()
    
    def update_dashboard(self):
        """Update the dashboard with fresh analysis"""
        # Get analysis
        summary = self.analyzer.get_analysis_summary()
        
        # Update analysis text\n        self.analysis_text.config(state=tk.NORMAL)\n        self.analysis_text.delete(1.0, tk.END)\n        self.analysis_text.insert(tk.END, f\"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\")\n        self.analysis_text.insert(tk.END, \"=\"*50 + \"\\n\\n\")\n        self.analysis_text.insert(tk.END, summary)\n        self.analysis_text.config(state=tk.DISABLED)
        
        # Reload watchlist in case it changed
        self.load_watchlist()
        
        # Update chart for selected stock if one is selected
        selection = self.stock_listbox.curselection()
        if selection:
            symbol = self.stock_listbox.get(selection[0])
            self.update_chart(symbol)
            self.update_stock_details(symbol)
        
        # Schedule next update (every 30 seconds)
        self.root.after(30000, self.update_dashboard)

def main():
    root = tk.Tk()
    app = RobinhoodStyleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()