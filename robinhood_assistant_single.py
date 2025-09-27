"""
Advanced Robinhood-Style Trading Assistant
Single-file consolidated application with UI and AI insights
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import time
import threading
import sqlite3
import json

class MarketDataAPI:
    """Handles market data retrieval from various APIs"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def get_stock_data(self, symbol: str, interval: str = "60min", outputsize: str = "compact") -> pd.DataFrame:
        """
        Fetch stock data for a given symbol
        Note: Using Alpha Vantage API for demonstration
        """
        if not self.api_key:
            return self._get_fallback_data(symbol)
            
        try:
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': symbol,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if "Time Series (60min)" in data:
                df = pd.DataFrame(data["Time Series (60min)"]).T
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                df = df.astype(float)
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                return df
            else:
                return self._get_fallback_data(symbol)
                
        except Exception as e:
            return self._get_fallback_data(symbol)
    
    def _get_fallback_data(self, symbol: str) -> pd.DataFrame:
        """Generate fallback data for testing when API is not available"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='60min')
        np.random.seed(hash(symbol) % 2**32)  # Different seed per symbol
        
        # Generate synthetic stock data based on symbol
        base_price = 50 + (hash(symbol) % 100)
        prices = [base_price]
        
        for i in range(1, 100):
            change = np.random.normal(0, 1.5)  # Random walk with small changes
            prices.append(max(1, prices[-1] + change))  # Ensure positive prices
            
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(10000, 50000, 100)
        }, index=dates)
        
        return df

class TechnicalIndicators:
    """Calculate various technical indicators"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """MACD - Moving Average Convergence Divergence"""
        exp1 = data.ewm(span=fast).mean()
        exp2 = data.ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

class PatternRecognition:
    """Identify chart patterns in price data"""
    
    @staticmethod
    def detect_support_resistance(df: pd.Series, window: int = 20, threshold: float = 0.02) -> list:
        """Detect support and resistance levels"""
        levels = []
        prices = df.values
        dates = df.index
        
        for i in range(window, len(prices) - window):
            # Check if current point is local min/max
            local_max = np.max(prices[i-window:i+window])
            local_min = np.min(prices[i-window:i+window])
            
            if abs(prices[i] - local_max) / local_max < threshold:
                levels.append((dates[i], prices[i], "resistance"))
            elif abs(prices[i] - local_min) / local_min < threshold:
                levels.append((dates[i], prices[i], "support"))
                
        return levels

class WatchlistManager:
    """Manage user's watchlist of stocks"""
    
    def __init__(self):
        self.watchlist = set()
        self.db_connection = sqlite3.connect("watchlist.db")
        self.init_db()
        
    def init_db(self):
        """Initialize the database for storing watchlist and alerts"""
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                symbol TEXT,
                alert_type TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        """)
        self.db_connection.commit()
    
    def add_to_watchlist(self, symbol: str):
        """Add a symbol to the watchlist"""
        symbol = symbol.upper()
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("INSERT INTO watchlist (symbol) VALUES (?)", (symbol,))
            self.db_connection.commit()
            self.watchlist.add(symbol)
        except sqlite3.IntegrityError:
            self.watchlist.add(symbol)
    
    def remove_from_watchlist(self, symbol: str):
        """Remove a symbol from the watchlist"""
        symbol = symbol.upper()
        cursor = self.db_connection.cursor()
        cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
        self.db_connection.commit()
        self.watchlist.discard(symbol)
    
    def get_watchlist(self):
        """Get the current watchlist"""
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT symbol FROM watchlist")
        results = cursor.fetchall()
        self.watchlist = {row[0] for row in results}
        return list(self.watchlist)
    
    def get_watchlist_data(self) -> dict:
        """Get market data for all symbols in watchlist"""
        data = {}
        for symbol in self.get_watchlist():
            try:
                # Using fallback for demonstration - in production, use real API
                data[symbol] = self._get_stock_data(symbol)
            except Exception as e:
                print(f"Error getting data for {symbol}: {e}")
        return data
    
    def _get_stock_data(self, symbol: str) -> pd.DataFrame:
        """Internal method to get stock data (using fallback for now)"""
        # Using fallback data for demonstration
        dates = pd.date_range(end=datetime.now(), periods=100, freq='60min')
        np.random.seed(hash(symbol) % 2**32)  # Different seed per symbol
        
        # Generate synthetic stock data based on symbol
        base_price = 50 + (hash(symbol) % 100)
        prices = [base_price]
        
        for i in range(1, 100):
            change = np.random.normal(0, 1.5)  # Random walk with small changes
            prices.append(max(1, prices[-1] + change))  # Ensure positive prices
            
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(10000, 50000, 100)
        }, index=dates)
        
        return df

class MarketAnalyzer:
    """Main analysis engine for the trading assistant"""
    
    def __init__(self):
        self.data_api = MarketDataAPI()  # In production, provide actual API key
        self.indicators = TechnicalIndicators()
        self.patterns = PatternRecognition()
        self.watchlist = WatchlistManager()
        self.alerts = []
    
    def add_to_watchlist(self, symbol: str):
        """Add a symbol to the watchlist"""
        self.watchlist.add_to_watchlist(symbol)
    
    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> dict:
        """Perform comprehensive analysis on a single stock"""
        analysis = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'current_price': data['Close'].iloc[-1],
            'indicators': {},
            'patterns': [],
            'signals': [],
            'risk_metrics': {}
        }
        
        # Calculate technical indicators
        close_prices = data['Close']
        high_prices = data['High']
        low_prices = data['Low']
        
        # Moving Averages
        analysis['indicators']['sma_20'] = self.indicators.calculate_sma(close_prices, 20).iloc[-1]
        analysis['indicators']['sma_50'] = self.indicators.calculate_sma(close_prices, 50).iloc[-1]
        analysis['indicators']['ema_12'] = self.indicators.calculate_ema(close_prices, 12).iloc[-1]
        analysis['indicators']['ema_26'] = self.indicators.calculate_ema(close_prices, 26).iloc[-1]
        
        # RSI
        rsi = self.indicators.calculate_rsi(close_prices)
        analysis['indicators']['rsi'] = rsi.iloc[-1]
        
        # MACD
        macd, signal, histogram = self.indicators.calculate_macd(close_prices)
        analysis['indicators']['macd'] = macd.iloc[-1]
        analysis['indicators']['macd_signal'] = signal.iloc[-1]
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.indicators.calculate_bollinger_bands(close_prices)
        current_price = close_prices.iloc[-1]
        analysis['indicators']['bb_upper'] = bb_upper.iloc[-1]
        analysis['indicators']['bb_middle'] = bb_middle.iloc[-1]
        analysis['indicators']['bb_lower'] = bb_lower.iloc[-1]
        
        # Generate signals based on indicators
        signals = []
        
        # RSI signals
        if analysis['indicators']['rsi'] > 70:
            signals.append("RSI: OVERBOUGHT - Potential SELL signal")
        elif analysis['indicators']['rsi'] < 30:
            signals.append("RSI: OVERSOLD - Potential BUY signal")
        
        # Moving average signals
        if analysis['indicators']['sma_20'] > analysis['indicators']['sma_50']:
            signals.append("SMA20 > SMA50 - Bullish trend")
        else:
            signals.append("SMA20 < SMA50 - Bearish trend")
        
        # MACD signals
        if macd.iloc[-1] > signal.iloc[-1]:
            signals.append("MACD Bullish - Bullish momentum")
        else:
            signals.append("MACD Bearish - Bearish momentum")
        
        # Bollinger Bands signals
        if current_price > bb_upper.iloc[-1]:
            signals.append("Price above upper Bollinger Band - Potential reversal")
        elif current_price < bb_lower.iloc[-1]:
            signals.append("Price below lower Bollinger Band - Potential reversal")
        
        analysis['signals'] = signals
        
        # Detect patterns
        support_resistance = self.patterns.detect_support_resistance(close_prices)
        if support_resistance:
            analysis['patterns'].extend([f"{sr[2].upper()} at {sr[1]:.2f} on {sr[0].strftime('%Y-%m-%d %H:%M')}" 
                                        for sr in support_resistance[-3:]])  # Last 3 levels
        
        # Risk metrics
        analysis['risk_metrics']['volatility'] = close_prices.pct_change().std()
        
        return analysis
    
    def analyze_watchlist(self) -> list:
        """Analyze all stocks in the watchlist"""
        results = []
        watchlist_data = self.watchlist.get_watchlist_data()
        
        for symbol, data in watchlist_data.items():
            try:
                analysis = self.analyze_stock(symbol, data)
                results.append(analysis)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        return results

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
        self.watchlist_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
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
        self.insights_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
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
            insights.append(f"🔴 RSI indicates {symbol} is OVERBOUGHT. Potential SELL signal.")
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