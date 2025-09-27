"""
Consolidated Robinhood-Style Trading Assistant with AI Integration
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import pandas as pd
from datetime import datetime
import json
import sqlite3
import threading
import time
from robinhood_market_researcher import MarketAnalyzer

class AdvancedRobinhoodAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Advanced Robinhood-Style Trading Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize analyzer
        self.analyzer = MarketAnalyzer()
        
        # AI insights cache
        self.ai_insights = {}
        
        # Configure styles
        self.configure_styles()
        
        # Create the interface
        self.create_widgets()
        
        # Load initial watchlist
        self.load_watchlist()
        
        # Start periodic updates in a separate thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
    
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
        style.configure("Green.TLabel", background="#ffffff", foreground="#00c800", font=("Arial", 10, "bold"))
        style.configure("Red.TLabel", background="#ffffff", foreground="#f44336", font=("Arial", 10, "bold"))
    
    def create_widgets(self):
        """Create the main interface widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root, style="Robinhood.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame, style="Robinhood.TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="🤖 Advanced Robinhood-Style Trading Assistant", 
            style="Header.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self.header_frame, style="Robinhood.TFrame")
        self.controls_frame.pack(side=tk.RIGHT)
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            self.controls_frame,
            text="🔄 Refresh",
            command=self.manual_refresh
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add stock button
        self.add_stock_btn = ttk.Button(
            self.controls_frame,
            text="➕ Add Stock",
            command=self.add_stock_to_watchlist
        )
        self.add_stock_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dashboard
        self.dashboard_frame = ttk.Frame(self.main_frame, style="Robinhood.TFrame")
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Watchlist
        self.watchlist_frame = ttk.Frame(self.dashboard_frame, style="Card.TFrame")
        self.watchlist_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), width=250)
        
        # Watchlist title
        ttk.Label(
            self.watchlist_frame,
            text="📈 Your Watchlist",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        # Stock list
        self.watchlist_listbox = tk.Listbox(
            self.watchlist_frame,
            font=("Arial", 11),
            borderwidth=0,
            highlightthickness=0,
            selectbackground="#00c800",
            selectforeground="white",
            height=25
        )
        self.watchlist_listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Remove stock button
        self.remove_btn = ttk.Button(
            self.watchlist_frame,
            text="❌ Remove Selected",
            command=self.remove_stock_from_watchlist
        )
        self.remove_btn.pack(pady=(0, 15))
        
        # Middle panel - Stock Details
        self.details_frame = ttk.Frame(self.dashboard_frame, style="Card.TFrame")
        self.details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Stock details title
        self.details_title = ttk.Label(
            self.details_frame,
            text="Stock Details",
            style="Title.TLabel"
        )
        self.details_title.pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        # Stock details text area
        self.details_text = tk.Text(
            self.details_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbar for details
        details_scrollbar = ttk.Scrollbar(self.details_frame, command=self.details_text.yview)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=10)
        self.details_text.config(yscrollcommand=details_scrollbar.set)
        
        # Right panel - AI Insights and Analysis
        self.insights_frame = ttk.Frame(self.dashboard_frame, style="Card.TFrame")
        self.insights_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, width=350)
        
        # AI Insights title
        ttk.Label(
            self.insights_frame,
            text="💡 AI Insights & Analysis",
            style="Title.TLabel"
        ).pack(anchor=tk.W, padx=15, pady=(15, 5))
        
        # AI insights text area
        self.insights_text = tk.Text(
            self.insights_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            state=tk.DISABLED
        )
        self.insights_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Scrollbar for insights
        insights_scrollbar = ttk.Scrollbar(self.insights_frame, command=self.insights_text.yview)
        insights_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 15), pady=10)
        self.insights_text.config(yscrollcommand=insights_scrollbar.set)
        
        # Bind selection event to show details
        self.watchlist_listbox.bind('<<ListboxSelect>>', self.on_stock_select)
    
    def load_watchlist(self):
        """Load watchlist from database"""
        self.watchlist_listbox.delete(0, tk.END)
        watchlist = self.analyzer.watchlist.get_watchlist()
        for stock in watchlist:
            self.watchlist_listbox.insert(tk.END, stock)
    
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
        selection = self.watchlist_listbox.curselection()
        if selection:
            symbol = self.watchlist_listbox.get(selection[0])
            result = messagebox.askyesno("Confirm", f"Remove {symbol} from watchlist?")
            if result:
                import sqlite3
                conn = sqlite3.connect("watchlist.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
                conn.commit()
                conn.close()
                self.load_watchlist()
                # Clear details and insights when stock is removed
                self.clear_details()
                self.clear_insights()
        else:
            messagebox.showinfo("Info", "Please select a stock to remove")
    
    def on_stock_select(self, event):
        """Handle stock selection to show details and insights"""
        selection = self.watchlist_listbox.curselection()
        if selection:
            symbol = self.watchlist_listbox.get(selection[0])
            self.show_stock_details(symbol)
            self.show_ai_insights(symbol)
    
    def show_stock_details(self, symbol):
        """Show detailed information about a selected stock"""
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
            self.clear_details()
    
    def show_ai_insights(self, symbol):
        """Generate and show AI insights for the selected stock"""
        watchlist_data = self.analyzer.watchlist.get_watchlist_data()
        
        if symbol in watchlist_data:
            data = watchlist_data[symbol]
            analysis = self.analyzer.analyze_stock(symbol, data)
            
            # Simulate AI insights based on technical analysis
            insights = self.generate_ai_insights(symbol, analysis)
            
            # Update insights text
            self.insights_text.config(state=tk.NORMAL)
            self.insights_text.delete(1.0, tk.END)
            
            self.insights_text.insert(tk.END, f"🤖 AI Insights for {symbol}\n\n")
            self.insights_text.insert(tk.END, insights)
            
            self.insights_text.config(state=tk.DISABLED)
    
    def generate_ai_insights(self, symbol, analysis):
        """Generate AI-style insights based on technical analysis"""
        insights = []
        
        # RSI Insights
        rsi = analysis['indicators']['rsi']
        if rsi > 70:
            insights.append(f"🔴 RSI indicates {symbol} is OVERSOLD. Potential SELL signal.")
        elif rsi < 30:
            insights.append(f"🟢 RSI indicates {symbol} is OVERSOLD. Potential BUY signal.")
        else:
            insights.append(f"📊 RSI ({rsi:.2f}) suggests neutral market conditions for {symbol}.")
        
        # Trend Insights
        sma_20 = analysis['indicators']['sma_20']
        sma_50 = analysis['indicators']['sma_50']
        
        if sma_20 > sma_50:
            insights.append(f"📈 {symbol} is in a BULLISH trend (SMA20 > SMA50).")
        else:
            insights.append(f"📉 {symbol} is in a BEARISH trend (SMA20 < SMA50).")
        
        # MACD Insights
        macd = analysis['indicators']['macd']
        macd_signal = analysis['indicators']['macd_signal']
        
        if macd > macd_signal:
            insights.append(f"🟢 MACD indicates BULLISH momentum for {symbol}.")
        else:
            insights.append(f"🔴 MACD indicates BEARISH momentum for {symbol}.")
        
        # Bollinger Band Insights
        current_price = analysis['current_price']
        bb_upper = analysis['indicators']['bb_upper']
        bb_lower = analysis['indicators']['bb_lower']
        
        if current_price > bb_upper:
            insights.append(f"🔴 Price is above upper Bollinger Band - potential reversal.")
        elif current_price < bb_lower:
            insights.append(f"🟢 Price is below lower Bollinger Band - potential reversal.")
        else:
            insights.append(f"📊 Price is within Bollinger Bands - normal volatility.")
        
        # Support/Resistance Insights
        if analysis['patterns']:
            insights.append(f"🔑 Key levels to watch: {', '.join(analysis['patterns'][:2])}")
        
        # Overall recommendation
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
            insights.append(f"\n🎯 RECOMMENDATION: {symbol} shows more bullish signals ({bull_signals} vs {bear_signals} bearish)")
        elif bear_signals > bull_signals:
            insights.append(f"\n🎯 RECOMMENDATION: {symbol} shows more bearish signals ({bear_signals} vs {bull_signals} bullish)")
        else:
            insights.append(f"\n🎯 RECOMMENDATION: {symbol} shows balanced market conditions")
        
        return "\n".join(insights) + "\n\nLast updated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def clear_details(self):
        """Clear the details panel"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Select a stock from your watchlist to see details...")
        self.details_text.config(state=tk.DISABLED)
    
    def clear_insights(self):
        """Clear the insights panel"""
        self.insights_text.config(state=tk.NORMAL)
        self.insights_text.delete(1.0, tk.END)
        self.insights_text.insert(tk.END, "AI Insights will appear here when you select a stock...")
        self.insights_text.config(state=tk.DISABLED)
    
    def manual_refresh(self):
        """Manually refresh the data"""
        self.load_watchlist()
        selection = self.watchlist_listbox.curselection()
        if selection:
            symbol = self.watchlist_listbox.get(selection[0])
            self.show_stock_details(symbol)
            self.show_ai_insights(symbol)
    
    def update_loop(self):
        """Continuous update loop running in a separate thread"""
        while self.running:
            try:
                # Update details and insights if a stock is selected
                self.root.after(0, self.update_selected_stock)
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                print(f"Update error: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
    
    def update_selected_stock(self):
        """Update the currently selected stock"""
        selection = self.watchlist_listbox.curselection()
        if selection:
            symbol = self.watchlist_listbox.get(selection[0])
            self.show_stock_details(symbol)
            self.show_ai_insights(symbol)
    
    def destroy(self):
        """Clean up when closing"""
        self.running = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AdvancedRobinhoodAssistant(root)
    
    def on_closing():
        app.destroy()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()