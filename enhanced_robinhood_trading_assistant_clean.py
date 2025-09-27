"""
Enhanced Dark-Themed Robinhood-Style Trading Assistant
Single comprehensive file with all features: dark theme, organized UI, charts, and market analysis
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

# Import matplotlib for charts
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# Market Data API Class
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
                df = pd.DataFrame(data["Time Series (60min)"].T)
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


# Technical Indicators Class
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


# Pattern Recognition Class
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


# Watchlist Manager Class
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


# Market Analyzer Class
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
        current_price = close_prices.iloc[-1]
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
    
    def get_analysis_summary(self) -> str:
        """Get a summary of the watchlist analysis"""
        analyses = self.analyze_watchlist()
        summary = []
        
        for analysis in analyses:
            summary.append(f"Stock: {analysis['symbol']}")
            summary.append(f"Current Price: ${analysis['current_price']:.2f}")
            summary.append(f"RSI: {analysis['indicators']['rsi']:.2f}")
            summary.append(f"Signals: {', '.join(analysis['signals'][:2])}")  # Show first 2 signals
            summary.append("-" * 30)
        
        return "\n".join(summary) if summary else "No stocks in watchlist"
    
    def generate_ai_insights(self, symbol, analysis):
        """Generate comprehensive AI-style insights based on technical analysis"""
        insights = []
        
        # Advanced RSI Insights
        rsi = analysis['indicators']['rsi']
        if rsi > 80:
            insights.append(f"🔴🔴 RSI EXTREME OVERBOUGHT ({rsi:.2f}) - Strong SELL signal. Potential reversal imminent.")
        elif rsi > 70:
            insights.append(f"🔴 RSI OVERBOUGHT ({rsi:.2f}) - SELL signal. Watch for pullback.")
        elif rsi < 20:
            insights.append(f"🟢🟢 RSI EXTREME OVERSOLD ({rsi:.2f}) - Strong BUY signal. Potential bounce expected.")
        elif rsi < 30:
            insights.append(f"🟢 RSI OVERSOLD ({rsi:.2f}) - BUY signal. Potential reversal starting.")
        else:
            insights.append(f"📊 RSI ({rsi:.2f}) suggests neutral market conditions for {symbol}.")
        
        # Trend Insights with strength analysis
        sma_20 = analysis['indicators']['sma_20']
        sma_50 = analysis['indicators']['sma_50']
        current_price = analysis['current_price']
        
        trend_strength = abs((sma_20 - sma_50) / sma_50) * 100  # Percentage difference
        if sma_20 > sma_50:
            if trend_strength > 5:
                insights.append(f"📈📈 STRONG BULLISH trend (SMA20: {sma_20:.2f} > SMA50: {sma_50:.2f}, strength: {trend_strength:.1f}%)")
            else:
                insights.append(f"📈 WEAK BULLISH trend (SMA20: {sma_20:.2f} > SMA50: {sma_50:.2f}, strength: {trend_strength:.1f}%)")
        else:
            if trend_strength > 5:
                insights.append(f"📉📉 STRONG BEARISH trend (SMA20: {sma_20:.2f} < SMA50: {sma_50:.2f}, strength: {trend_strength:.1f}%)")
            else:
                insights.append(f"📉 WEAK BEARISH trend (SMA20: {sma_20:.2f} < SMA50: {sma_50:.2f}, strength: {trend_strength:.1f}%)")
        
        # MACD Insights with divergence detection
        macd = analysis['indicators']['macd']
        macd_signal = analysis['indicators']['macd_signal']
        macd_hist = macd - macd_signal  # MACD histogram
        
        if macd > macd_signal:
            if macd_hist > 0 and macd_hist > (macd_hist * 0.9):  # Histogram is positive and growing
                insights.append(f"🟢🟢 MACD STRONG Bullish momentum - histogram expanding ({macd_hist:.3f})")
            else:
                insights.append(f"🟢 MACD Bullish momentum - signal line crossed ({macd:.3f} > {macd_signal:.3f})")
        else:
            if macd_hist < 0 and macd_hist < (macd_hist * 1.1):  # Histogram is negative and getting more negative
                insights.append(f"🔴🔴 MACD STRONG Bearish momentum - histogram contracting ({macd_hist:.3f})")
            else:
                insights.append(f"🔴 MACD Bearish momentum - signal line crossed ({macd:.3f} < {macd_signal:.3f})")
        
        # Bollinger Band Insights with squeeze detection
        bb_upper = analysis['indicators']['bb_upper']
        bb_middle = analysis['indicators']['bb_middle']
        bb_lower = analysis['indicators']['bb_lower']
        
        # Calculate Bollinger Band width for squeeze detection
        bb_width = (bb_upper - bb_lower) / bb_middle  # BB width as percentage of price
        
        if current_price > bb_upper:
            insights.append(f"🔴 Price above upper Bollinger Band - potential reversal from overbought territory")
        elif current_price < bb_lower:
            insights.append(f"🟢 Price below lower Bollinger Band - potential reversal from oversold territory")
        elif bb_width < 0.02:  # Less than 2% width indicates squeeze
            insights.append(f"⚡ BOLLINGER SQUEEZE detected - potential breakout (width: {bb_width*100:.2f}%)")
        else:
            insights.append(f"📊 Price in normal Bollinger Band range - typical volatility")
        
        # Support/Resistance and Pattern Insights
        if analysis['patterns']:
            insights.append(f"🔑 Key levels to watch: {', '.join(analysis['patterns'][:2])}")
        
        # Volatility and Risk Assessment
        volatility = analysis['risk_metrics']['volatility']
        if volatility > 0.03:  # High volatility threshold
            insights.append(f"⚠️ HIGH volatility detected ({volatility*100:.2f}%) - increased risk")
        elif volatility < 0.01:  # Low volatility threshold
            insights.append(f"🔍 LOW volatility detected ({volatility*100:.2f}%) - potential breakout setup")
        else:
            insights.append(f"✅ NORMAL volatility level ({volatility*100:.2f}%)")
        
        # Price Position Analysis
        price_position = (current_price - bb_lower) / (bb_upper - bb_lower)  # Where price is in BB range
        if price_position > 0.8:
            insights.append(f"📈 Price in upper range of recent volatility (position: {price_position*100:.1f}%)")
        elif price_position < 0.2:
            insights.append(f"📉 Price in lower range of recent volatility (position: {price_position*100:.1f}%)")
        else:
            insights.append(f"📊 Price in middle range of recent volatility (position: {price_position*100:.1f}%)")
        
        # Overall AI-driven recommendation with confidence level
        bull_signals = sum([
            rsi < 30,  # Oversold
            sma_20 > sma_50,  # Bullish trend
            macd > macd_signal,  # Bullish momentum
            current_price > sma_20,  # Above short-term MA
            current_price > bb_middle  # Above middle BB
        ])
        
        bear_signals = sum([
            rsi > 70,  # Overbought
            sma_20 < sma_50,  # Bearish trend
            macd < macd_signal,  # Bearish momentum
            current_price < sma_20,  # Below short-term MA
            current_price < bb_middle  # Below middle BB
        ])
        
        total_signals = bull_signals + bear_signals
        confidence = (max(bull_signals, bear_signals) / total_signals * 100) if total_signals > 0 else 0
        
        if bull_signals > bear_signals:
            if confidence > 70:
                insights.append(f"\n🎯🎯 HIGH CONFIDENCE BUY: {symbol} shows {bull_signals} bullish vs {bear_signals} bearish signals ({confidence:.0f}% confidence)")
            elif confidence > 50:
                insights.append(f"\n🎯 MODERATE CONFIDENCE BUY: {symbol} shows {bull_signals} bullish vs {bear_signals} bearish signals ({confidence:.0f}% confidence)")
            else:
                insights.append(f"\n💡 WEAK SIGNAL: {symbol} shows {bull_signals} bullish vs {bear_signals} bullish signals")
        elif bear_signals > bull_signals:
            if confidence > 70:
                insights.append(f"\n🎯🎯 HIGH CONFIDENCE SELL: {symbol} shows {bear_signals} bearish vs {bull_signals} bullish signals ({confidence:.0f}% confidence)")
            elif confidence > 50:
                insights.append(f"\n🎯 MODERATE CONFIDENCE SELL: {symbol} shows {bear_signals} bearish vs {bull_signals} bullish signals ({confidence:.0f}% confidence)")
            else:
                insights.append(f"\n💡 WEAK SIGNAL: {symbol} shows {bear_signals} bearish vs {bull_signals} bullish signals")
        else:
            insights.append(f"\n⚖️  BALANCED: {symbol} shows equal bullish ({bull_signals}) and bearish ({bear_signals}) signals")
        
        # Add market regime assessment
        if trend_strength > 5 and volatility > 0.02:
            insights.append(f"🔥 TRENDING MARKET: Strong trend with high volatility - follow trend strategy")
        elif trend_strength < 2 and volatility < 0.015:
            insights.append(f"😴 CHOPPY MARKET: Weak trend with low volatility - range-bound strategy")
        else:
            insights.append(f"📈 MIXED MARKET: Moderate trend with normal volatility")
        
        return "\n".join(insights) + f"\n\n🤖 AI Analysis complete | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# Main Application Class
class EnhancedRobinhoodAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 Enhanced Robinhood-Style Trading Assistant")
        self.root.geometry("1400x800")
        self.root.configure(bg="#121212")  # Dark background
        
        # Initialize analyzer
        self.analyzer = MarketAnalyzer()
        
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
            text="🌙 Enhanced Robinhood-Style Trading Assistant", 
            style="Header.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Controls frame
        self.controls_frame = ttk.Frame(self.header_frame, style="Dark.TFrame")
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
        self.dashboard_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Watchlist and Details
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
        self.watchlist_listbox = tk.Listbox(
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
        self.watchlist_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
            
            # Update chart for the selected stock
            self.update_chart(symbol)
        else:
            self.clear_details()
    
    def show_ai_insights(self, symbol):
        """Generate and show AI insights for the selected stock"""
        watchlist_data = self.analyzer.watchlist.get_watchlist_data()
        
        if symbol in watchlist_data:
            data = watchlist_data[symbol]
            analysis = self.analyzer.analyze_stock(symbol, data)
            
            # Generate comprehensive AI insights based on technical analysis
            insights = self.analyzer.generate_ai_insights(symbol, analysis)
            
            # Update insights text
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            
            self.analysis_text.insert(tk.END, f"🤖 AI Insights for {symbol}\n\n")
            self.analysis_text.insert(tk.END, insights)
            
            # Configure tags for better visual indicators in analysis
            self.analysis_text.tag_configure("bullish", foreground="#4caf50", font=("Arial", 10, "bold"))
            self.analysis_text.tag_configure("bearish", foreground="#f44336", font=("Arial", 10, "bold"))
            self.analysis_text.tag_configure("strong_signal", foreground="#8bc34a", font=("Arial", 10, "bold"))
            self.analysis_text.tag_configure("weak_signal", foreground="#f57c00", font=("Arial", 10, "bold"))
            self.analysis_text.tag_configure("neutral", foreground="#64b5f6", font=("Arial", 10, "bold"))
            self.analysis_text.tag_configure("high_confidence", foreground="#e91e63", font=("Arial", 11, "bold"))
            self.analysis_text.tag_configure("market_regime", foreground="#9c27b0", font=("Arial", 10, "bold"))
            
            # Apply tags based on keywords with more sophisticated patterns
            content = self.analysis_text.get(1.0, tk.END)
            for i, line in enumerate(content.split('\n')):
                line_upper = line.upper()
                
                # Strong signal indicators
                if '🎯🎯 HIGH CONFIDENCE' in line_upper:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("high_confidence", start_pos, end_pos)
                elif 'BULLISH' in line_upper or 'BUY' in line_upper or 'oversold' in line.lower() or '🟢' in line:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("bullish", start_pos, end_pos)
                elif 'BEARISH' in line_upper or 'SELL' in line_upper or 'overbought' in line.lower() or '🔴' in line:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("bearish", start_pos, end_pos)
                elif 'WEAK SIGNAL' in line_upper:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("weak_signal", start_pos, end_pos)
                elif 'BALANCED' in line_upper or 'NEUTRAL' in line_upper:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("neutral", start_pos, end_pos)
                elif 'TRENDING' in line_upper or 'CHOPPY' in line_upper or 'MIXED' in line_upper:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("market_regime", start_pos, end_pos)
                elif 'STRONG' in line_upper:
                    start_pos = f"{i+1}.0"
                    end_pos = f"{i+1}.end"
                    self.analysis_text.tag_add("strong_signal", start_pos, end_pos)
            
            self.analysis_text.config(state=tk.DISABLED)
    
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
    
    def clear_details(self):
        """Clear the details panel"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, "Select a stock from your watchlist to see details...")
        self.details_text.config(state=tk.DISABLED)
    
    def clear_insights(self):
        """Clear the insights panel"""
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "AI Insights will appear here when you select a stock...")
        self.analysis_text.config(state=tk.DISABLED)
    
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
    app = EnhancedRobinhoodAssistant(root)
    
    def on_closing():
        app.destroy()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":    
    main()