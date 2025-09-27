"""
Market Researcher Module
Contains the MarketAnalyzer class and associated components for the trading assistant
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import sqlite3


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