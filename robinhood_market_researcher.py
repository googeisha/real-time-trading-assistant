"""
Market Researcher Module
Contains the MarketAnalyzer class and associated components for the trading assistant
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime
import sqlite3
import threading
import random

# Try to import yfinance, use fallback if not available
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available. Using fallback data only.")


class MarketDataAPI:
    """Handles market data retrieval from various APIs"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.crypto_base_url = "https://www.alphavantage.co/query"
        # Add support for real-time data simulation
        self.real_time_data = {}
        self.last_update_time = {}
        
    def get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch stock data for a given symbol using yfinance if available
        """
        if not YFINANCE_AVAILABLE:
            print("yfinance not available, using fallback data")
            return self._get_fallback_data(symbol)
        
        try:
            # Use yfinance to get real market data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"No data found for {symbol}, using fallback data")
                return self._get_fallback_data(symbol)
            
            # Ensure the required columns exist
            if not all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                print(f"Missing required columns for {symbol}, using fallback data")
                return self._get_fallback_data(symbol)
            
            # Convert to the format expected by the rest of the application
            df = pd.DataFrame({
                'Open': data['Open'],
                'High': data['High'],
                'Low': data['Low'],
                'Close': data['Close'],
                'Volume': data['Volume']
            })
            
            df.index = data.index  # Preserve the datetime index
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol} with yfinance: {e}")
            # Try fallback method
            return self._get_fallback_data(symbol)
    
    def get_real_time_quote(self, symbol: str, asset_type: str = 'stock') -> dict:
        """
        Get real-time quote for a symbol (simulated for demo purposes)
        In a real implementation, this would connect to a real-time data feed
        """
        # Simulate real-time data by adding small random variations to the last known price
        import random
        from datetime import datetime, timedelta
        
        # Get current time
        now = datetime.now()
        
        # Check if we have cached data for this symbol
        cache_key = f"{symbol}_{asset_type}"
        if cache_key in self.real_time_data:
            # Check if last update was recent (within 30 seconds)
            last_update = self.last_update_time.get(cache_key, now - timedelta(seconds=60))
            if (now - last_update).seconds < 30:
                # Return cached data with small variation
                cached_data = self.real_time_data[cache_key].copy()
                # Add small random variation to simulate real-time changes
                variation = random.uniform(-0.005, 0.005)  # +/- 0.5% variation
                cached_data['price'] = cached_data['price'] * (1 + variation)
                cached_data['timestamp'] = now
                return cached_data
        
        # If no recent cached data, get fresh data
        if asset_type == 'crypto':
            data = self.get_crypto_data(symbol)
        else:
            data = self.get_stock_data(symbol)
        
        if data is not None and not data.empty:
            # Get the latest close price
            latest_price = data['Close'].iloc[-1]
            
            # Create simulated real-time quote with bid/ask
            bid_price = latest_price * (1 - random.uniform(0.001, 0.003))  # Slightly lower than last price
            ask_price = latest_price * (1 + random.uniform(0.001, 0.003))  # Slightly higher than last price
            last_price = latest_price
            
            quote_data = {
                'symbol': symbol,
                'price': last_price,
                'bid': bid_price,
                'ask': ask_price,
                'volume': data['Volume'].iloc[-1] if 'Volume' in data.columns else 0,
                'change': last_price - data['Close'].iloc[-2] if len(data) > 1 else 0,
                'change_percent': ((last_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100) if len(data) > 1 and data['Close'].iloc[-2] != 0 else 0,
                'timestamp': now,
                'asset_type': asset_type
            }
            
            # Cache the data
            self.real_time_data[cache_key] = quote_data.copy()
            self.last_update_time[cache_key] = now
            
            return quote_data
        else:
            # Return error data if no data available
            return {
                'symbol': symbol,
                'error': 'No data available',
                'timestamp': now
            }

    def subscribe_to_real_time_updates(self, symbol: str, asset_type: str = 'stock', callback_func=None) -> bool:
        """
        Subscribe to real-time updates for a symbol
        In a real implementation, this would connect to a WebSocket or similar real-time feed
        """
        # For demo purposes, we'll simulate subscription with periodic updates
        # In a real implementation, this would establish a persistent connection
        
        def simulated_real_time_feed():
            """Simulate real-time data feed"""
            import time
            import threading
            
            def update_loop():
                while True:
                    try:
                        # Get real-time quote
                        quote = self.get_real_time_quote(symbol, asset_type)
                        
                        # Call callback function if provided
                        if callback_func:
                            callback_func(quote)
                        
                        # Wait before next update (simulated 5-second interval)
                        time.sleep(5)
                    except Exception as e:
                        print(f"Error in real-time feed for {symbol}: {e}")
                        break
            
            # Start the update loop in a separate thread
            update_thread = threading.Thread(target=update_loop, daemon=True)
            update_thread.start()
            return True
        
        # Start the simulated feed
        return simulated_real_time_feed()
    
    def _get_fallback_data(self, symbol: str) -> pd.DataFrame:
        """Generate fallback data when API is unavailable"""
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        np.random.seed(42)  # For reproducible "random" data
        opens = 100 + np.cumsum(np.random.randn(100) * 0.5)
        highs = opens + np.abs(np.random.randn(100) * 0.5)
        lows = opens - np.abs(np.random.randn(100) * 0.5)
        closes = opens + np.random.randn(100) * 0.25
        
        df = pd.DataFrame({
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': closes,
            'Volume': np.random.randint(1000000, 5000000, 100)
        }, index=dates)
        
        return df


class TechnicalIndicators:
    """Technical analysis indicators"""
    
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
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Moving Average Convergence Divergence"""
        ema_fast = TechnicalIndicators.calculate_ema(data, fast)
        ema_slow = TechnicalIndicators.calculate_ema(data, slow)
        macd = ema_fast - ema_slow
        signal_line = TechnicalIndicators.calculate_ema(macd, signal)
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Bollinger Bands"""
        sma = TechnicalIndicators.calculate_sma(data, period)
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band


class PatternRecognition:
    """Pattern recognition for technical analysis"""
    
    @staticmethod
    def detect_support_resistance(df: pd.Series, window: int = 20, threshold: float = 0.02) -> list:
        """Detect potential support and resistance levels"""
        local_min = df.rolling(window=window, center=True).min()
        local_max = df.rolling(window=window, center=True).max()
        
        # Find points where price is at local min/max
        support_levels = df[df == local_min]
        resistance_levels = df[df == local_max]
        
        patterns = []
        if len(support_levels) > 0:
            patterns.append(f"Support at ~${support_levels.iloc[-1]:.2f}")
        if len(resistance_levels) > 0:
            patterns.append(f"Resistance at ~${resistance_levels.iloc[-1]:.2f}")
        
        return patterns
    
    @staticmethod
    def detect_patterns(data: pd.DataFrame) -> list:
        """Detect common technical patterns in price data"""
        if data is None or data.empty or len(data) < 20:
            return []
        
        patterns = []
        
        # Get the latest portion of data for pattern detection
        recent_data = data.tail(50) if len(data) > 50 else data
        
        # Detect support and resistance levels
        if 'Close' in recent_data.columns:
            sr_patterns = PatternRecognition.detect_support_resistance(recent_data['Close'])
            patterns.extend(sr_patterns)
        
        # Detect double tops/bottoms
        double_top_bottom = PatternRecognition._detect_double_top_bottom(recent_data)
        patterns.extend(double_top_bottom)
        
        # Detect head and shoulders
        head_shoulders = PatternRecognition._detect_head_and_shoulders(recent_data)
        patterns.extend(head_shoulders)
        
        # Detect triangles
        triangles = PatternRecognition._detect_triangles(recent_data)
        patterns.extend(triangles)
        
        # Detect flags and pennants
        flags_pennants = PatternRecognition._detect_flags_pennants(recent_data)
        patterns.extend(flags_pennants)
        
        return patterns
    
    @staticmethod
    def _detect_double_top_bottom(data: pd.DataFrame) -> list:
        """Detect double top and double bottom patterns"""
        patterns = []
        
        if data is None or data.empty or len(data) < 20:
            return patterns
        
        if 'High' not in data.columns or 'Low' not in data.columns:
            return patterns
        
        # Simplified double top/bottom detection
        # In a real implementation, this would be more sophisticated
        close_prices = data['Close'].values if 'Close' in data.columns else []
        
        if len(close_prices) >= 20:
            # Check for potential double tops (two peaks at similar levels)
            peaks = []
            for i in range(1, len(close_prices) - 1):
                if (close_prices[i] > close_prices[i-1] and 
                    close_prices[i] > close_prices[i+1] and
                    close_prices[i] > np.mean(close_prices)):
                    peaks.append((i, close_prices[i]))
            
            # Check for potential double bottoms (two troughs at similar levels)
            troughs = []
            for i in range(1, len(close_prices) - 1):
                if (close_prices[i] < close_prices[i-1] and 
                    close_prices[i] < close_prices[i+1] and
                    close_prices[i] < np.mean(close_prices)):
                    troughs.append((i, close_prices[i]))
            
            # Check if we have similar peaks (double top)
            if len(peaks) >= 2:
                peak_prices = [peak[1] for peak in peaks[-2:]]  # Last two peaks
                if abs(peak_prices[0] - peak_prices[1]) / ((peak_prices[0] + peak_prices[1]) / 2) < 0.03:  # Within 3%
                    patterns.append("Potential Double Top Pattern")
            
            # Check if we have similar troughs (double bottom)
            if len(troughs) >= 2:
                trough_prices = [trough[1] for trough in troughs[-2:]]  # Last two troughs
                if abs(trough_prices[0] - trough_prices[1]) / ((trough_prices[0] + trough_prices[1]) / 2) < 0.03:  # Within 3%
                    patterns.append("Potential Double Bottom Pattern")
        
        return patterns
    
    @staticmethod
    def _detect_head_and_shoulders(data: pd.DataFrame) -> list:
        """Detect head and shoulders patterns (simplified)"""
        patterns = []
        
        if data is None or data.empty or len(data) < 20:
            return patterns
        
        close_prices = data['Close'].values if 'Close' in data.columns else []
        
        if len(close_prices) >= 15:
            # Simplified head and shoulders detection
            # This is a placeholder - in a real implementation this would be much more complex
            price_changes = np.diff(close_prices)
            volatility = np.std(price_changes) if len(price_changes) > 1 else 0
            
            if volatility > 0:
                # Just checking for potential pattern formation
                if len(close_prices) >= 5:
                    recent_volatility = np.std(price_changes[-5:]) if len(price_changes) >= 5 else volatility
                    if recent_volatility < volatility * 0.5:  # Decreasing volatility
                        patterns.append("Potential Head and Shoulders Pattern Formation")
        
        return patterns
    
    @staticmethod
    def _detect_triangles(data: pd.DataFrame) -> list:
        """Detect triangle patterns (simplified)"""
        patterns = []
        
        if data is None or data.empty or len(data) < 15:
            return patterns
        
        high_prices = data['High'].values if 'High' in data.columns else []
        low_prices = data['Low'].values if 'Low' in data.columns else []
        
        if len(high_prices) >= 10 and len(low_prices) >= 10:
            # Check for converging highs and lows (triangle pattern)
            high_trend = np.polyfit(range(len(high_prices[-10:])), high_prices[-10:], 1)[0]
            low_trend = np.polyfit(range(len(low_prices[-10:])), low_prices[-10:], 1)[0]
            
            # If highs and lows are converging, it might be a triangle
            if high_trend < 0 and low_trend > 0:
                patterns.append("Potential Triangle Pattern (Symmetrical)")
            elif high_trend < 0 and abs(low_trend) < 0.5:
                patterns.append("Potential Triangle Pattern (Descending)")
            elif abs(high_trend) < 0.5 and low_trend > 0:
                patterns.append("Potential Triangle Pattern (Ascending)")
        
        return patterns
    
    @staticmethod
    def _detect_flags_pennants(data: pd.DataFrame) -> list:
        """Detect flag and pennant patterns (simplified)"""
        patterns = []
        
        if data is None or data.empty or len(data) < 10:
            return patterns
        
        close_prices = data['Close'].values if 'Close' in data.columns else []
        
        if len(close_prices) >= 10:
            # Check for sharp price moves followed by consolidation (flag/pennant)
            recent_changes = np.diff(close_prices[-10:])
            if len(recent_changes) >= 5:
                # Look for strong move followed by small changes
                initial_move = np.sum(recent_changes[:3])
                consolidation = np.sum(recent_changes[3:])
                
                if abs(initial_move) > np.mean(np.abs(recent_changes)) * 2 and abs(consolidation) < np.mean(np.abs(recent_changes)):
                    if initial_move > 0:
                        patterns.append("Potential Bullish Flag/Pennant Pattern")
                    else:
                        patterns.append("Potential Bearish Flag/Pennant Pattern")
        
        return patterns


class WatchlistManager:
    """Manages user watchlist"""
    
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database for watchlist"""
        self.conn = sqlite3.connect('watchlist.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY,
                symbol TEXT UNIQUE,
                asset_type TEXT DEFAULT 'stock'  -- 'stock' or 'crypto'
            )
        ''')
        self.conn.commit()
    
    def add_to_watchlist(self, symbol: str, asset_type: str = 'stock'):
        """Add a symbol to the watchlist"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO watchlist (symbol, asset_type) VALUES (?, ?)", (symbol, asset_type))
            self.conn.commit()
            print(f"Added {symbol} ({asset_type}) to watchlist")
        except Exception as e:
            print(f"Error adding to watchlist: {e}")
    
    def remove_from_watchlist(self, symbol: str):
        """Remove a symbol from the watchlist"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
        self.conn.commit()
        print(f"Removed {symbol} from watchlist")
    
    def get_watchlist(self):
        """Get all symbols in the watchlist"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT symbol, asset_type FROM watchlist")
        return cursor.fetchall()
    
    def get_watchlist_symbols(self):
        """Get just the symbols (without asset type) in the watchlist"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT symbol FROM watchlist")
        return [row[0] for row in cursor.fetchall()]
    
    def get_watchlist_data(self) -> dict:
        """Get current data for all symbols in the watchlist"""
        watchlist_items = self.get_watchlist()
        data = {}
        api = MarketDataAPI()
        
        for symbol, asset_type in watchlist_items:
            if asset_type.lower() == 'crypto':
                data[symbol] = api.get_crypto_data(symbol)
            else:
                data[symbol] = api.get_stock_data(symbol)
        
        return data
    
    def get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Get stock data for a symbol"""
        api = MarketDataAPI()
        return api.get_stock_data(symbol, period, interval)
    
    def _get_stock_data(self, symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """Get stock data for a symbol (fallback method)"""
        api = MarketDataAPI()
        return api.get_stock_data(symbol, period, interval)
    
class RealTimeDataManager:
    """Manages real-time market data subscriptions and updates"""
    
    def __init__(self):
        self.subscriptions = {}  # Track active subscriptions
        self.data_cache = {}  # Cache of real-time data
        self.callbacks = {}  # Callback functions for data updates
        self.api = MarketDataAPI()
    
    def subscribe(self, symbol: str, asset_type: str = 'stock', callback_func=None) -> bool:
        """
        Subscribe to real-time updates for a symbol
        """
        try:
            # Store subscription info
            subscription_key = f"{symbol}_{asset_type}"
            self.subscriptions[subscription_key] = {
                'symbol': symbol,
                'asset_type': asset_type,
                'callback': callback_func,
                'active': True
            }
            
            # Start real-time data feed
            success = self.api.subscribe_to_real_time_updates(
                symbol, asset_type, 
                callback_func=self._handle_data_update
            )
            
            return success
        except Exception as e:
            print(f"Error subscribing to real-time data for {symbol}: {e}")
            return False
    
    def unsubscribe(self, symbol: str, asset_type: str = 'stock') -> bool:
        """
        Unsubscribe from real-time updates for a symbol
        """
        try:
            subscription_key = f"{symbol}_{asset_type}"
            if subscription_key in self.subscriptions:
                self.subscriptions[subscription_key]['active'] = False
                del self.subscriptions[subscription_key]
                return True
            return False
        except Exception as e:
            print(f"Error unsubscribing from real-time data for {symbol}: {e}")
            return False
    
    def get_latest_data(self, symbol: str, asset_type: str = 'stock') -> dict:
        """
        Get the latest real-time data for a symbol
        """
        subscription_key = f"{symbol}_{asset_type}"
        return self.data_cache.get(subscription_key, {})
    
    def _handle_data_update(self, data: dict):
        """
        Handle incoming real-time data updates
        """
        try:
            symbol = data.get('symbol', 'UNKNOWN')
            asset_type = data.get('asset_type', 'stock')
            subscription_key = f"{symbol}_{asset_type}"
            
            # Update data cache
            self.data_cache[subscription_key] = data
            
            # Call registered callback if it exists
            if subscription_key in self.subscriptions:
                subscription = self.subscriptions[subscription_key]
                if subscription.get('active', False) and subscription.get('callback'):
                    try:
                        subscription['callback'](data)
                    except Exception as e:
                        print(f"Error in callback for {symbol}: {e}")
        except Exception as e:
            print(f"Error handling data update: {e}")


# Add the real-time data methods to the MarketDataAPI class after the crypto data method
        """Get crypto data for a symbol"""
        api = MarketDataAPI()
        return api.get_crypto_data(symbol, market, period, interval)


class SentimentAnalyzer:
    """Advanced sentiment analysis for market research"""
    
    def __init__(self):
        # In a real implementation, we would load a pre-trained sentiment model
        # For now, we'll simulate sentiment analysis based on news headlines and social media
        pass
    
    def analyze_sentiment_from_news(self, symbol: str, news_articles: list) -> dict:
        """Analyze sentiment from news articles"""
        # Simulate sentiment analysis based on news content
        positive_keywords = [
            'rise', 'gain', 'up', 'bullish', 'strong', 'positive', 'profit', 
            'outperform', 'upgrade', 'buy', 'optimistic', 'breakout', 'high',
            'record', 'surge', 'rally', 'gain', 'outlook', 'success', 'strong',
            'expansion', 'growth', 'prosper', 'rebound', 'recover', 'improve'
        ]
        negative_keywords = [
            'fall', 'loss', 'down', 'bearish', 'weak', 'negative', 'losses',
            'underperform', 'downgrade', 'sell', 'pessimistic', 'breakdown', 'low', 'crash',
            'decline', 'drop', 'downturn', 'recession', 'loss', 'trouble', 'concern',
            'decrease', 'fall', 'slump', 'worries', 'risk', 'volatile', 'volatile market'
        ]
        
        sentiment_score = 0
        positive_count = 0
        negative_count = 0
        total_articles = len(news_articles)
        
        for article in news_articles:
            title = article.get('title', '')
            summary = article.get('summary', '')
            content = f"{title} {summary}".lower()
            
            for word in positive_keywords:
                if word in content:
                    sentiment_score += 1
                    positive_count += 1
            for word in negative_keywords:
                if word in content:
                    sentiment_score -= 1
                    negative_count += 1
        
        total_keywords = positive_count + negative_count
        if total_keywords > 0:
            sentiment_ratio = sentiment_score / total_keywords
        else:
            sentiment_ratio = 0  # Neutral if no keywords found
        
        # Normalize to -1 (very negative) to +1 (very positive)
        sentiment_normalized = max(-1, min(1, sentiment_ratio))
        
        if sentiment_normalized > 0.3:
            sentiment_label = "Very Positive"
        elif sentiment_normalized > 0.1:
            sentiment_label = "Positive"
        elif sentiment_normalized > -0.1:
            sentiment_label = "Neutral"
        elif sentiment_normalized > -0.3:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Very Negative"
        
        return {
            'symbol': symbol,
            'sentiment_score': sentiment_normalized,
            'sentiment_label': sentiment_label,
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'total_analyzed': total_articles,
            'source': 'news'
        }
    
    def analyze_sentiment_from_headlines(self, symbol: str, headlines: list) -> dict:
        """Analyze sentiment from financial headlines"""
        # Simulate sentiment analysis based on headline keywords
        positive_keywords = [
            'rise', 'gain', 'up', 'bullish', 'strong', 'positive', 'profit', 
            'outperform', 'upgrade', 'buy', 'optimistic', 'breakout', 'high'
        ]
        negative_keywords = [
            'fall', 'loss', 'down', 'bearish', 'weak', 'negative', 'losses',
            'underperform', 'downgrade', 'sell', 'pessimistic', 'breakdown', 'low', 'crash'
        ]
        
        sentiment_score = 0
        positive_count = 0
        negative_count = 0
        
        for headline in headlines:
            headline_lower = headline.lower()
            for word in positive_keywords:
                if word in headline_lower:
                    sentiment_score += 1
                    positive_count += 1
            for word in negative_keywords:
                if word in headline_lower:
                    sentiment_score -= 1
                    negative_count += 1
        
        total_keywords = positive_count + negative_count
        if total_keywords > 0:
            sentiment_ratio = sentiment_score / total_keywords
        else:
            sentiment_ratio = 0  # Neutral if no keywords found
        
        # Normalize to -1 (very negative) to +1 (very positive)
        sentiment_normalized = max(-1, min(1, sentiment_ratio))
        
        if sentiment_normalized > 0.3:
            sentiment_label = "Very Positive"
        elif sentiment_normalized > 0.1:
            sentiment_label = "Positive"
        elif sentiment_normalized > -0.1:
            sentiment_label = "Neutral"
        elif sentiment_normalized > -0.3:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Very Negative"
        
        return {
            'symbol': symbol,
            'sentiment_score': sentiment_normalized,
            'sentiment_label': sentiment_label,
            'positive_mentions': positive_count,
            'negative_mentions': negative_count,
            'total_analyzed': len(headlines)
        }

    def analyze_social_sentiment(self, symbol: str, social_data: list) -> dict:
        """Analyze sentiment from social media posts"""
        # Simulate social media sentiment analysis
        # In a real implementation, we would analyze actual social media data
        sentiment_score = 0
        engagement_score = 0
        
        for post in social_data:
            text = post.get('text', '').lower()
            likes = post.get('likes', 0)
            shares = post.get('shares', 0)
            
            # Simple keyword-based sentiment
            if any(word in text for word in ['bullish', 'moon', 'rocket', 'buy', 'strong', 'gain']):
                sentiment_score += 1
            if any(word in text for word in ['bearish', 'dump', 'sell', 'crash', 'fall', 'weak']):
                sentiment_score -= 1
                
            # Weight by engagement
            total_engagement = likes + shares
            engagement_score += total_engagement
            
        # Normalize sentiment by engagement
        if engagement_score > 0:
            sentiment_normalized = sentiment_score / (engagement_score / 100 + 1)
        else:
            sentiment_normalized = 0
            
        sentiment_normalized = max(-1, min(1, sentiment_normalized))
        
        if sentiment_normalized > 0.3:
            sentiment_label = "Very Positive"
        elif sentiment_normalized > 0.1:
            sentiment_label = "Positive"
        elif sentiment_normalized > -0.1:
            sentiment_label = "Neutral"
        elif sentiment_normalized > -0.3:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Very Negative"
        
        return {
            'symbol': symbol,
            'sentiment_score': sentiment_normalized,
            'sentiment_label': sentiment_label,
            'total_engagement': engagement_score,
            'posts_analyzed': len(social_data)
        }

    def combined_sentiment_score(self, news_sentiment: dict, social_sentiment: dict) -> float:
        """Combine news and social sentiment scores with weights"""
        # Weight news sentiment slightly higher than social sentiment
        news_weight = 0.6
        social_weight = 0.4
        
        combined_score = (
            news_sentiment['sentiment_score'] * news_weight + 
            social_sentiment['sentiment_score'] * social_weight
        )
        
        return combined_score


class MarketRegimeDetector:
    """Detects market regime (bullish, bearish, or sideways)"""
    
    def __init__(self):
        pass
    
    def detect_regime(self, analysis: dict) -> dict:
        """Detect the current market regime based on technical indicators"""
        indicators = analysis['indicators']
        risk_metrics = analysis['risk_metrics']
        
        # Calculate regime based on multiple factors
        sma_trend = indicators['sma_50'] / analysis.get('prev_close', analysis['current_price'])
        volatility = risk_metrics['volatility']
        rsi = indicators['rsi']
        
        # Determine trend direction
        if sma_trend > 1.02:  # 2% above previous level
            trend = "BULLISH"
            trend_strength = "Strong"
        elif sma_trend > 1.005:  # 0.5% above
            trend = "BULLISH"
            trend_strength = "Moderate"
        elif sma_trend < 0.98:  # 2% below
            trend = "BEARISH"
            trend_strength = "Strong"
        elif sma_trend < 0.995:  # 0.5% below
            trend = "BEARISH"
            trend_strength = "Moderate"
        else:
            trend = "SIDEWAYS"
            trend_strength = "Neutral"
        
        # Determine regime based on volatility and trend
        if volatility < 0.02 and trend != "SIDEWAYS":
            regime_confidence = "High"
        elif volatility < 0.05:
            regime_confidence = "Medium"
        else:
            regime_confidence = "Low"
        
        return {
            'regime': trend,
            'trend_strength': trend_strength,
            'confidence': regime_confidence,
            'volatility_regime': "Low" if volatility < 0.02 else "Normal" if volatility < 0.05 else "High"
        }


class AdvancedAIInsights:
    """Advanced AI-powered insights engine with multiple analysis components"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.risk_tolerance = 0.1  # Default risk tolerance
        self.market_regime_detector = MarketRegimeDetector()
    
    def generate_comprehensive_insights(self, symbol: str, analysis: dict, asset_type: str = 'stock') -> dict:
        """Generate comprehensive AI insights combining technical, fundamental, and sentiment analysis"""
        
        # Technical analysis insights (from existing analysis)
        tech_insights = self._generate_technical_insights(analysis)
        
        # Market regime detection
        regime_insights = self.market_regime_detector.detect_regime(analysis)
        
        # Sentiment analysis (simulated)
        sentiment_insights = self._generate_sentiment_insights(symbol, asset_type)
        
        # Enhanced ML analysis
        ml_insights = self.enhanced_machine_learning_analysis(symbol, analysis, asset_type)
        
        # Combine all insights
        overall_recommendation = self._combine_insights(tech_insights, regime_insights, sentiment_insights)
        
        return {
            'symbol': symbol,
            'asset_type': asset_type,
            'timestamp': datetime.now(),
            'technical_insights': tech_insights,
            'market_regime_insights': regime_insights,
            'sentiment_insights': sentiment_insights,
            'ml_insights': ml_insights,  # Add the enhanced ML insights
            'combined_recommendation': overall_recommendation,
            'confidence_score': self._calculate_confidence_score(analysis, sentiment_insights),
            'risk_assessment': self._calculate_risk_assessment(analysis)
        }
    
    def _generate_technical_insights(self, analysis: dict) -> dict:
        """Generate insights from technical analysis"""
        indicators = analysis['indicators']
        signals = analysis['signals']
        risk_metrics = analysis['risk_metrics']
        
        # Count bullish and bearish signals
        bullish_signals = sum([
            indicators['rsi'] < 30,  # Oversold
            indicators['sma_20'] > indicators['sma_50'],  # Bullish trend
            indicators['macd'] > indicators['macd_signal'],  # Bullish momentum
            analysis['current_price'] > indicators['bb_middle']  # Above middle BB
        ])
        
        bearish_signals = sum([
            indicators['rsi'] > 70,  # Overbought
            indicators['sma_20'] < indicators['sma_50'],  # Bearish trend
            indicators['macd'] < indicators['macd_signal'],  # Bearish momentum
            analysis['current_price'] < indicators['bb_middle']  # Below middle BB
        ])
        
        # Momentum strength
        momentum_strength = abs(indicators['macd']) * 100  # Scale to 0-100
        
        # Trend strength
        sma_diff = abs(indicators['sma_20'] - indicators['sma_50']) / analysis['current_price']
        trend_strength = min(100, sma_diff * 1000)  # Scale appropriately
        
        return {
            'bullish_signals_count': bullish_signals,
            'bearish_signals_count': bearish_signals,
            'momentum_strength': momentum_strength,
            'trend_strength': trend_strength,
            'support_resistance_levels': analysis.get('patterns', []),
            'volatility_assessment': self._assess_volatility(risk_metrics['volatility']),
            'rsi_assessment': self._assess_rsi(indicators['rsi'])
        }
    
    def _assess_volatility(self, volatility: float) -> str:
        """Assess the level of volatility"""
        if volatility < 0.02:
            return "Low"
        elif volatility < 0.05:
            return "Moderate"
        elif volatility < 0.1:
            return "High"
        else:
            return "Very High"
    
    def _assess_rsi(self, rsi: float) -> str:
        """Assess the RSI value"""
        if rsi < 30:
            return "Oversold"
        elif rsi < 40:
            return "Undervalued"
        elif rsi < 60:
            return "Neutral"
        elif rsi < 70:
            return "Overvalued"
        else:
            return "Overbought"
    
    def _generate_sentiment_insights(self, symbol: str, asset_type: str) -> dict:
        """Generate sentiment insights (simulated)"""
        # In a real implementation, this would fetch actual news and social data
        # For simulation, we'll generate some sample data
        
        # Simulate some news headlines
        sample_headlines = [
            f"{symbol} posts strong quarterly results",
            f"{symbol} beats earnings expectations",
            f"Analysts remain bullish on {symbol}",
            f"{symbol} faces regulatory headwinds",
            f"Market concerns about {symbol} growth"
        ]
        
        # Simulate social media posts
        sample_social_posts = [
            {'text': f'Bullish on {symbol}! Great potential', 'likes': 45, 'shares': 12},
            {'text': f'{symbol} is going to the moon!', 'likes': 32, 'shares': 8},
            {'text': f'Bearish on {symbol}, too risky', 'likes': 8, 'shares': 3},
            {'text': f'Holding {symbol} long term', 'likes': 22, 'shares': 5}
        ]
        
        news_sentiment = self.sentiment_analyzer.analyze_sentiment_from_headlines(symbol, sample_headlines)
        social_sentiment = self.sentiment_analyzer.analyze_social_sentiment(symbol, sample_social_posts)
        combined_score = self.sentiment_analyzer.combined_sentiment_score(news_sentiment, social_sentiment)
        
        return {
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'combined_sentiment': combined_score,
            'sentiment_label': self._sentiment_label(combined_score)
        }
    
    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return "Very Positive"
        elif score > 0.1:
            return "Positive"
        elif score > -0.1:
            return "Neutral"
        elif score > -0.3:
            return "Negative"
        else:
            return "Very Negative"
    
    def _combine_insights(self, tech_insights: dict, regime_insights: dict, sentiment_insights: dict) -> str:
        """Combine all insights to generate an overall recommendation"""
        # Calculate weighted scores
        technical_score = tech_insights['bullish_signals_count'] - tech_insights['bearish_signals_count']
        sentiment_score = sentiment_insights['combined_sentiment'] * 10  # Scale to match technical
        regime_score = 1 if regime_insights['regime'] == 'BULLISH' else -1 if regime_insights['regime'] == 'BEARISH' else 0
        
        # Combine scores (with different weights)
        combined_score = (
            technical_score * 0.5 +  # Technical analysis is most important
            sentiment_score * 0.3 +  # Sentiment is secondary
            regime_score * 0.2       # Market regime provides context
        )
        
        if combined_score > 1.5:
            return "STRONG BUY"
        elif combined_score > 0.5:
            return "BUY"
        elif combined_score > -0.5:
            return "HOLD"
        elif combined_score > -1.5:
            return "SELL"
        else:
            return "STRONG SELL"
    
    def _calculate_confidence_score(self, analysis: dict, sentiment_insights: dict) -> float:
        """Calculate a confidence score for the recommendation"""
        # Confidence based on the number of indicators and data points
        indicators = analysis['indicators']
        
        # Calculate consistency of indicators
        rsi = indicators['rsi']
        macd = indicators['macd']
        macd_signal = indicators['macd_signal']
        sma_20 = indicators['sma_20']
        sma_50 = indicators['sma_50']
        current_price = analysis['current_price']
        
        # Count consistent signals
        consistency_count = 0
        total_signals = 4  # RSI, MACD, Trend, Bollinger
        
        # RSI consistency with price action
        if (rsi < 30 and current_price < sma_20) or (rsi > 70 and current_price > sma_20):
            consistency_count += 1
        
        # MACD trend consistency
        if (macd > macd_signal and current_price > sma_20) or (macd < macd_signal and current_price < sma_20):
            consistency_count += 1
            
        # Moving average trend
        if (sma_20 > sma_50 and current_price > sma_20) or (sma_20 < sma_50 and current_price < sma_20):
            consistency_count += 1
            
        # Bollinger band position consistency
        bb_upper = indicators['bb_upper']
        bb_lower = indicators['bb_lower']
        bb_middle = indicators['bb_middle']
        
        if (current_price > bb_middle and rsi > 50) or (current_price < bb_middle and rsi < 50):
            consistency_count += 1
        
        # Base confidence on technical consistency
        technical_confidence = consistency_count / total_signals
        
        # Incorporate sentiment confidence
        # Higher weight if sentiment matches technical direction
        sentiment_direction = 1 if sentiment_insights['combined_sentiment'] > 0 else -1
        tech_direction = 1 if analysis['current_price'] > analysis['prev_close'] else -1
        
        sentiment_confidence = 0.7 if sentiment_direction == tech_direction else 0.3
        
        # Overall confidence is weighted average
        overall_confidence = (technical_confidence * 0.7) + (sentiment_confidence * 0.3)
        
        # Add market regime impact to confidence
        # In trending markets, signals are generally more reliable
        risk_metrics = analysis['risk_metrics']
        volatility = risk_metrics['volatility']
        
        # Adjust confidence based on market environment
        if volatility < 0.02:  # Low volatility environment
            overall_confidence *= 0.9  # Slightly reduce due to potential false signals
        elif volatility > 0.06:  # High volatility environment
            overall_confidence *= 0.8  # Reduce due to increased uncertainty
        else:  # Moderate volatility - optimal for technical analysis
            overall_confidence *= 1.1  # Slightly increase confidence
        
        # Ensure confidence is within 0-1 range
        return max(0.0, min(1.0, overall_confidence))
    
    def enhanced_machine_learning_analysis(self, symbol: str, analysis: dict, asset_type: str = 'stock') -> dict:
        """Enhanced ML model for more accurate predictions and insights"""
        # This function implements more advanced ML techniques
        indicators = analysis['indicators']
        risk_metrics = analysis['risk_metrics']
        current_price = analysis['current_price']
        prev_close = analysis.get('prev_close', current_price)
        
        # Calculate derived features for ML model
        features = {}
        
        # Technical features
        features['rsi_normalized'] = indicators['rsi'] / 100  # Normalize to 0-1
        features['sma_ratio'] = indicators['sma_20'] / indicators['sma_50'] if indicators['sma_50'] != 0 else 1.0
        features['macd_histogram'] = indicators['macd_histogram']
        features['bb_position'] = ((current_price - indicators['bb_lower']) / 
                                  (indicators['bb_upper'] - indicators['bb_lower'])) if (indicators['bb_upper'] - indicators['bb_lower']) != 0 else 0.5
        features['price_change_pct'] = (current_price - prev_close) / prev_close if prev_close != 0 else 0
        features['volatility'] = risk_metrics['volatility']
        
        # Calculate ensemble prediction combining multiple ML approaches
        ensemble_pred = self._calculate_ensemble_prediction(features, analysis)
        
        # Generate enhanced insights based on ML model
        return {
            'ensemble_prediction': ensemble_pred,
            'ml_features': features,
            'pattern_recognition': self._enhanced_pattern_recognition(analysis),
            'price_targets': self._calculate_ml_price_targets(features, current_price),
            'risk_adjusted_signals': self._calculate_risk_adjusted_signals(features, analysis),
            'regime_awareness': self._calculate_regime_adjusted_signals(features, analysis)
        }
    
    def _calculate_ensemble_prediction(self, features: dict, analysis: dict) -> dict:
        """Calculate ensemble prediction using multiple ML approaches"""
        # Simple ensemble of 3 approaches:
        # 1. Momentum-based prediction
        # 2. Mean-reversion prediction
        # 3. Trend-following prediction
        
        indicators = analysis['indicators']
        current_price = analysis['current_price']
        
        # 1. Momentum prediction (weighted towards MACD and RSI)
        momentum_score = 0
        if indicators['rsi'] < 30:
            momentum_score += 0.4
        elif indicators['rsi'] > 70:
            momentum_score -= 0.4
            
        if indicators['macd'] > indicators['macd_signal']:
            momentum_score += 0.3
        else:
            momentum_score -= 0.3
            
        # 2. Mean-reversion prediction (based on RSI and Bollinger bands)
        mean_rev_score = 0
        if features['bb_position'] < 0.2:  # Near lower band
            mean_rev_score += 0.5
        elif features['bb_position'] > 0.8:  # Near upper band
            mean_rev_score -= 0.5
        
        # 3. Trend prediction (based on moving averages)
        trend_score = 0
        if current_price > indicators['sma_20'] > indicators['sma_50']:
            trend_score += 0.4
        elif current_price < indicators['sma_20'] < indicators['sma_50']:
            trend_score -= 0.4
        
        # Weighted ensemble (momentum: 40%, mean-reversion: 35%, trend: 25%)
        ensemble_score = (momentum_score * 0.4 + 
                         mean_rev_score * 0.35 + 
                         trend_score * 0.25)
        
        # Map score to recommendation
        if ensemble_score > 0.3:
            recommendation = "STRONG BUY"
        elif ensemble_score > 0.1:
            recommendation = "BUY"
        elif ensemble_score > -0.1:
            recommendation = "HOLD"
        elif ensemble_score > -0.3:
            recommendation = "SELL"
        else:
            recommendation = "STRONG SELL"
        
        # Calculate confidence based on signal agreement
        agreement = sum([abs(momentum_score) > 0.2, 
                        abs(mean_rev_score) > 0.2,
                        abs(trend_score) > 0.2])
        confidence = min(1.0, (abs(ensemble_score) + agreement * 0.1) * 1.5)
        
        return {
            'recommendation': recommendation,
            'score': ensemble_score,
            'confidence': max(0.0, min(1.0, confidence)),
            'momentum_component': momentum_score,
            'mean_reversion_component': mean_rev_score,
            'trend_component': trend_score
        }
    
    def _enhanced_pattern_recognition(self, analysis: dict) -> dict:
        """Enhanced pattern recognition using multiple indicators"""
        indicators = analysis['indicators']
        current_price = analysis['current_price']
        patterns = {}
        
        # Detect various candlestick and technical patterns
        if indicators['rsi'] < 30 and indicators['macd'] > indicators['macd_signal']:
            patterns['bullish_divergence'] = "RSI oversold with bullish MACD crossover"
        
        if indicators['rsi'] > 70 and indicators['macd'] < indicators['macd_signal']:
            patterns['bearish_divergence'] = "RSI overbought with bearish MACD crossover"
        
        if current_price > indicators['sma_20'] > indicators['sma_50']:
            patterns['golden_cross'] = "Bullish moving average crossover pattern"
        
        if current_price < indicators['sma_20'] < indicators['sma_50']:
            patterns['death_cross'] = "Bearish moving average crossover pattern"
        
        # Bollinger Band patterns
        bb_width = (indicators['bb_upper'] - indicators['bb_lower']) / current_price
        if bb_width < 0.02:  # Squeeze
            patterns['bb_squeeze'] = "Bollinger Band squeeze - potential breakout"
        
        # Stochastic patterns (if available)
        if 'stoch_k' in indicators and 'stoch_d' in indicators:
            if indicators['stoch_k'] < 20 and indicators['stoch_d'] < 20:
                patterns['stoch_oversold'] = "Stochastic indicators in oversold territory"
            elif indicators['stoch_k'] > 80 and indicators['stoch_d'] > 80:
                patterns['stoch_overbought'] = "Stochastic indicators in overbought territory"
        
        return patterns
    
    def _calculate_ml_price_targets(self, features: dict, current_price: float) -> dict:
        """Calculate ML-based price targets"""
        # These are simple ML-inspired targets based on technical patterns
        
        # Calculate targets based on volatility and technical levels
        volatility = features['volatility']
        bb_position = features['bb_position']
        
        # Short-term target (1-3 days)
        short_term_target = current_price
        if features['rsi_normalized'] < 0.3:  # Oversold - potential bounce
            short_term_target *= 1.02
        elif features['rsi_normalized'] > 0.7:  # Overbought - potential pullback
            short_term_target *= 0.98
        else:  # Neutral - slight trend continuation
            if features['price_change_pct'] > 0:
                short_term_target *= 1.01
            else:
                short_term_target *= 0.99
        
        # Medium-term target (1-4 weeks)
        if bb_position < 0.2:  # Near support
            medium_term_target = current_price * 1.05
        elif bb_position > 0.8:  # Near resistance
            medium_term_target = current_price * 0.95
        else:  # In middle - trend following
            if features['sma_ratio'] > 1.0:
                medium_term_target = current_price * 1.08
            else:
                medium_term_target = current_price * 0.92
        
        # Calculate stop loss based on volatility
        stop_loss = current_price * (1 - volatility * 1.5) if features['price_change_pct'] >= 0 else current_price * (1 + volatility * 1.5)
        
        return {
            'short_term': short_term_target,
            'medium_term': medium_term_target,
            'stop_loss': stop_loss,
            'volatility_adjusted': True
        }
    
    def _calculate_risk_adjusted_signals(self, features: dict, analysis: dict) -> dict:
        """Calculate risk-adjusted trading signals"""
        indicators = analysis['indicators']
        risk_metrics = analysis['risk_metrics']
        
        # Adjust signals based on risk metrics
        risk_adjusted_signals = {}
        
        # Adjust RSI signals based on volatility
        if risk_metrics['volatility'] > 0.05:  # High volatility
            rsi_signal = "NEUTRAL"  # Reduce confidence in RSI in high vol
        else:
            if indicators['rsi'] < 30:
                rsi_signal = "STRONG BUY"
            elif indicators['rsi'] > 70:
                rsi_signal = "STRONG SELL"
            else:
                rsi_signal = "NEUTRAL"
        
        risk_adjusted_signals['rsi_signal'] = rsi_signal
        risk_adjusted_signals['volatility_factor'] = risk_metrics['volatility']
        
        # Adjust trend signals based on trend strength (ADX if available)
        if 'adx' in indicators:
            if indicators['adx'] > 25:  # Strong trend
                trend_confidence = "HIGH"
            elif indicators['adx'] > 20:  # Moderate trend
                trend_confidence = "MEDIUM"
            else:  # Weak trend
                trend_confidence = "LOW"
        else:
            trend_confidence = "MEDIUM"  # Default assumption
        
        risk_adjusted_signals['trend_confidence'] = trend_confidence
        
        return risk_adjusted_signals
    
    def _calculate_regime_adjusted_signals(self, features: dict, analysis: dict) -> dict:
        """Calculate signals adjusted for market regime"""
        indicators = analysis['indicators']
        risk_metrics = analysis['risk_metrics']
        
        # Determine market regime based on volatility and trend strength
        volatility = risk_metrics['volatility']
        if volatility < 0.02:
            regime = "LOW_VOLATILITY"
        elif volatility < 0.05:
            regime = "MODERATE_VOLATILITY"
        else:
            regime = "HIGH_VOLATILITY"
        
        # Adjust signals based on regime
        if regime == "LOW_VOLATILITY":
            # In low volatility, trends may be weak, focus on mean reversion
            if 30 <= indicators['rsi'] <= 70:
                regime_signal = "MEAN_REVERSION_OPS"
            else:
                regime_signal = "TREND_FOLLOW"
        elif regime == "HIGH_VOLATILITY":
            # In high volatility, trend following may work better
            if indicators['sma_20'] != 0 and indicators['sma_50'] != 0:
                if analysis['current_price'] > indicators['sma_20'] > indicators['sma_50']:
                    regime_signal = "TREND_FOLLOW_LONG"
                elif analysis['current_price'] < indicators['sma_20'] < indicators['sma_50']:
                    regime_signal = "TREND_FOLLOW_SHORT"
                else:
                    regime_signal = "CAUTION"
        else:  # MODERATE_VOLATILITY
            # Balanced approach
            regime_signal = "BALANCED"
        
        return {
            'regime': regime,
            'regime_signal': regime_signal,
            'regime_confidence': 0.7  # Default confidence
        }
    
    def _calculate_risk_assessment(self, analysis: dict) -> dict:
        """Calculate a comprehensive risk assessment"""
        risk_metrics = analysis['risk_metrics']
        indicators = analysis['indicators']
        
        volatility = risk_metrics['volatility']
        max_drawdown = risk_metrics['max_drawdown']
        var_95 = risk_metrics['var_95']
        rsi = indicators['rsi']
        
        # Calculate risk levels
        volatility_risk = self._risk_level_from_metric(volatility, 0.02, 0.05, 0.1)
        drawdown_risk = self._risk_level_from_metric(abs(max_drawdown), 0.05, 0.1, 0.15)
        var_risk = self._risk_level_from_metric(abs(var_95), 0.02, 0.04, 0.08)
        
        # RSI risk (extreme RSI values can indicate reversal risk)
        rsi_risk_score = min(abs(rsi - 50) / 50, 1.0)  # Max risk when RSI is 0 or 100
        rsi_risk = self._risk_level_from_metric(rsi_risk_score, 0.3, 0.6, 0.9)
        
        return {
            'volatility_risk': volatility_risk,
            'drawdown_risk': drawdown_risk,
            'value_at_risk': var_risk,
            'rsi_risk': rsi_risk,
            'overall_risk_level': max(volatility_risk, drawdown_risk, var_risk, rsi_risk),
            'risk_summary': self._risk_summary(max(volatility_risk, drawdown_risk, var_risk, rsi_risk))
        }
    
    def _risk_level_from_metric(self, value: float, low_threshold: float, medium_threshold: float, high_threshold: float) -> str:
        """Convert a metric value to a risk level"""
        if value <= low_threshold:
            return "Low"
        elif value <= medium_threshold:
            return "Medium"
        elif value <= high_threshold:
            return "High"
        else:
            return "Very High"
    
    def _risk_summary(self, overall_risk_level: str) -> str:
        """Provide a summary of the risk level"""
        if overall_risk_level == "Very High":
            return "Exercise extreme caution. This asset carries significant risk."
        elif overall_risk_level == "High":
            return "High risk asset. Consider reducing position size."
        elif overall_risk_level == "Medium":
            return "Moderate risk. Appropriate for balanced portfolios."
        else:
            return "Low risk asset. Generally safer investment option."


class ExternalDataSource:
    """Handles integration with multiple external data sources"""
    
    def __init__(self, alpha_vantage_key: str = None, fred_key: str = None):
        self.alpha_vantage_key = alpha_vantage_key
        self.fred_key = fred_key
        self.session = requests.Session()
        
    def get_yahoo_finance_data(self, symbol: str) -> dict:
        """Get data from Yahoo Finance (simulated)"""
        # In a real implementation, this would connect to Yahoo Finance API
        # For now, we'll simulate the data structure
        try:
            # This is just a simulation - in reality, you would make an API request
            return {
                'symbol': symbol,
                'dividend_yield': 0.015,  # 1.5%
                'pe_ratio': 25.4,
                'eps': 4.20,
                'market_cap': '1.5T',
                'beta': 1.2,
                'recommendation': 'BUY',
                'target_price': 180.00,
                'price_to_book': 3.2,
                'debt_to_equity': 0.8,
                'roe': 0.25  # 25% Return on Equity
            }
        except Exception as e:
            print(f"Error fetching Yahoo Finance data for {symbol}: {e}")
            return {}
    
    def get_fred_data(self, series_id: str) -> dict:
        """Get economic data from FRED (Federal Reserve Economic Data)"""
        # In a real implementation, this would connect to FRED API
        # For simulation, we'll provide sample economic data
        try:
            # This would normally be: https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={fred_key}
            # For simulation, we'll return sample data
            sample_data = {
                'GDP': {'latest_value': 2.1, 'unit': '%', 'frequency': 'quarterly', 'last_updated': '2023-10-26'},
                'CPIAUCSL': {'latest_value': 3.2, 'unit': '%', 'frequency': 'monthly', 'last_updated': '2023-10-12'},
                'UNRATE': {'latest_value': 3.8, 'unit': '%', 'frequency': 'monthly', 'last_updated': '2023-10-06'},
                'FEDFUNDS': {'latest_value': 5.3, 'unit': '%', 'frequency': 'daily', 'last_updated': '2023-10-27'},
                'DGS10': {'latest_value': 4.25, 'unit': '%', 'frequency': 'daily', 'last_updated': '2023-10-27'}
            }
            return sample_data.get(series_id, {})
        except Exception as e:
            print(f"Error fetching FRED data for {series_id}: {e}")
            return {}
    
    def get_fundamental_data(self, symbol: str) -> dict:
        """Get fundamental data for a stock"""
        # Simulate getting fundamental data from various sources
        try:
            yahoo_data = self.get_yahoo_finance_data(symbol)
            return {
                'symbol': symbol,
                'financial_ratios': {
                    'pe_ratio': yahoo_data.get('pe_ratio', 'N/A'),
                    'peg_ratio': 'N/A',  # Would require growth estimates
                    'price_to_sales': 'N/A',
                    'price_to_book': yahoo_data.get('price_to_book', 'N/A'),
                    'dividend_yield': yahoo_data.get('dividend_yield', 'N/A'),
                    'debt_to_equity': yahoo_data.get('debt_to_equity', 'N/A'),
                    'current_ratio': 'N/A',
                    'return_on_equity': yahoo_data.get('roe', 'N/A')
                },
                'company_metrics': {
                    'market_cap': yahoo_data.get('market_cap', 'N/A'),
                    'eps': yahoo_data.get('eps', 'N/A'),
                    'eps_growth': 'N/A',
                    'revenue': 'N/A',
                    'revenue_growth': 'N/A',
                    'net_income': 'N/A'
                },
                'recommendations': {
                    'recommendation': yahoo_data.get('recommendation', 'N/A'),
                    'target_price': yahoo_data.get('target_price', 'N/A'),
                    'upside_potential': 'N/A'
                }
            }
        except Exception as e:
            print(f"Error fetching fundamental data for {symbol}: {e}")
            return {}
    
    def get_economic_indicators(self) -> dict:
        """Get key economic indicators"""
        return {
            'gdp_growth': self.get_fred_data('GDP'),
            'inflation_rate': self.get_fred_data('CPIAUCSL'),
            'unemployment_rate': self.get_fred_data('UNRATE'),
            'federal_funds_rate': self.get_fred_data('FEDFUNDS'),
            '10y_treasury_yield': self.get_fred_data('DGS10')
        }
    
    def get_sector_etf_performance(self) -> dict:
        """Get performance of sector ETFs as market benchmarks"""
        # Simulate sector ETF data
        sector_etfs = {
            'Technology': {'symbol': 'XLK', 'change_1d': 1.2, 'change_1m': 5.3, 'change_3m': 8.7},
            'Healthcare': {'symbol': 'XLV', 'change_1d': 0.5, 'change_1m': 2.1, 'change_3m': 4.2},
            'Financials': {'symbol': 'XLF', 'change_1d': -0.3, 'change_1m': 1.8, 'change_3m': -1.2},
            'Consumer Discretionary': {'symbol': 'XLY', 'change_1d': 0.8, 'change_1m': 3.5, 'change_3m': 6.1},
            'Energy': {'symbol': 'XLE', 'change_1d': 1.5, 'change_1m': -2.3, 'change_3m': 5.8},
            'Industrials': {'symbol': 'XLI', 'change_1d': 0.6, 'change_1m': 2.7, 'change_3m': 3.9},
            'Utilities': {'symbol': 'XLU', 'change_1d': -0.2, 'change_1m': 0.9, 'change_3m': 2.1},
            'Real Estate': {'symbol': 'XLRE', 'change_1d': 0.3, 'change_1m': -1.1, 'change_3m': 1.5},
            'Communication': {'symbol': 'XLC', 'change_1d': 0.9, 'change_1m': 4.2, 'change_3m': 7.3},
            'Materials': {'symbol': 'XLB', 'change_1d': 0.4, 'change_1m': 1.6, 'change_3m': 2.8},
            'Consumer Staples': {'symbol': 'XLP', 'change_1d': 0.1, 'change_1m': 1.2, 'change_3m': 2.5}
        }
        return sector_etfs


class EconomicCalendar:
    """Provides economic calendar data for market research"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.external_source = ExternalDataSource()
    
    def get_upcoming_events(self) -> list:
        """Get upcoming economic events"""
        # In a real implementation, this would fetch from an economic calendar API
        # For simulation, we'll return sample events
        return [
            {
                'date': '2024-01-15',
                'event': 'Consumer Price Index (CPI)',
                'impact': 'High',
                'currency': 'USD',
                'forecast': '0.3%',
                'previous': '0.2%',
                'actual': 'N/A'
            },
            {
                'date': '2024-01-16',
                'event': 'Federal Reserve Interest Rate Decision',
                'impact': 'Very High',
                'currency': 'USD',
                'forecast': '5.25%',
                'previous': '5.25%',
                'actual': 'N/A'
            },
            {
                'date': '2024-01-17',
                'event': 'Retail Sales',
                'impact': 'High',
                'currency': 'USD',
                'forecast': '0.4%',
                'previous': '0.3%',
                'actual': 'N/A'
            },
            {
                'date': '2024-01-18',
                'event': 'Housing Starts',
                'impact': 'Medium',
                'currency': 'USD',
                'forecast': '1.25M',
                'previous': '1.23M',
                'actual': 'N/A'
            }
        ]
    
    def get_impact_description(self, impact_level: str) -> str:
        """Get description for impact level"""
        impact_descriptions = {
            'Low': 'May have minimal impact on markets',
            'Medium': 'May cause moderate market movement',
            'High': 'Likely to cause significant market movement',
            'Very High': 'Expected to cause major market volatility'
        }
        return impact_descriptions.get(impact_level, 'Impact unknown')
    
    def get_market_moving_events(self) -> list:
        """Get high-impact events that are likely to move markets"""
        all_events = self.get_upcoming_events()
        market_moving_events = []
        
        for event in all_events:
            if event['impact'] in ['High', 'Very High']:
                market_moving_events.append(event)
                
        return market_moving_events


class MarketResearcher:
    """Comprehensive market research engine"""
    
    def __init__(self):
        self.data_api = MarketDataAPI()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.economic_calendar = EconomicCalendar()
    
    def get_sector_analysis(self, symbol: str) -> dict:
        """Analyze the sector performance for a given symbol"""
        # In a real implementation, this would fetch sector data
        # For now, we'll simulate sector analysis based on asset type
        
        # This would normally fetch sector performance data
        # For simulation, we'll provide some sample data
        sector_data = {
            'sector_peers': [
                {'symbol': 'COMP1', 'change': 2.5, 'volume': 1500000},
                {'symbol': 'COMP2', 'change': -1.2, 'volume': 2100000},
                {'symbol': 'COMP3', 'change': 0.8, 'volume': 950000}
            ],
            'sector_performance': {
                'sector': 'Technology' if symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA'] else 
                         'Financial' if symbol in ['JPM', 'BAC', 'GS'] else
                         'Healthcare' if symbol in ['JNJ', 'PFE', 'MRK'] else
                         'Crypto' if symbol.upper() in ['BTC', 'ETH', 'SOL', 'ADA'] else
                         'General',
                '1_day': 1.2,
                '1_week': -0.5,
                '1_month': 3.4,
                'relative_performance': 'Outperforming'
            },
            'sector_news': [
                f"Tech sector sees renewed investor interest",
                f"Regulatory concerns impact sector valuations",
                f"Quarterly earnings beat expectations across sector"
            ]
        }
        
        return sector_data
    
    def analyze_fundamentals(self, symbol: str, asset_type: str = 'stock') -> dict:
        """Analyze fundamental metrics for a symbol"""
        if asset_type == 'crypto':
            # For crypto, analyze on-chain metrics and other crypto-specific fundamentals
            return {
                'type': 'crypto',
                'metrics': {
                    'market_cap_rank': 'N/A',  # Would require real API call
                    '24h_volume': 'N/A',
                    'circulating_supply': 'N/A',
                    'total_supply': 'N/A',
                    'on_chain_metrics': {
                        'transaction_volume': 'N/A',
                        'active_addresses': 'N/A',
                        'network_hashrate': 'N/A'
                    }
                }
            }
        else:
            # For stocks, analyze traditional fundamental metrics
            return {
                'type': 'stock',
                'metrics': {
                    'pe_ratio': 'N/A',  # Would require real API call
                    'eps': 'N/A',
                    'dividend_yield': 'N/A',
                    'market_cap': 'N/A',
                    'revenue_growth': 'N/A',
                    'profit_margin': 'N/A',
                    'debt_to_equity': 'N/A'
                }
            }
    
    def get_market_regime_analysis(self, symbol: str, data: pd.DataFrame) -> dict:
        """Analyze current market regime for the asset"""
        # Calculate various regime indicators
        returns = data['Close'].pct_change().dropna()
        
        # Volatility regime
        recent_vol = returns.tail(20).std()
        long_term_vol = returns.std()
        
        if recent_vol > long_term_vol * 1.5:
            volatility_regime = "High Volatility"
        elif recent_vol < long_term_vol * 0.7:
            volatility_regime = "Low Volatility"
        else:
            volatility_regime = "Normal Volatility"
        
        # Trend regime
        sma_50 = data['Close'].rolling(50).mean().iloc[-1]
        sma_200 = data['Close'].rolling(200).mean().iloc[-1]
        
        if data['Close'].iloc[-1] > sma_50 > sma_200:
            trend_regime = "Bullish"
        elif data['Close'].iloc[-1] < sma_50 < sma_200:
            trend_regime = "Bearish"
        else:
            trend_regime = "Sideways"
        
        # Momentum regime
        momentum_1m = (data['Close'].iloc[-1] / data['Close'].iloc[-22]) - 1
        momentum_3m = (data['Close'].iloc[-1] / data['Close'].iloc[-66]) - 1
        
        if momentum_1m > 0.1 or momentum_3m > 0.2:
            momentum_regime = "High Momentum"
        elif momentum_1m > 0 or momentum_3m > 0:
            momentum_regime = "Positive Momentum"
        elif momentum_1m < -0.1 or momentum_3m < -0.2:
            momentum_regime = "Negative Momentum"
        else:
            momentum_regime = "Low Momentum"
        
        return {
            'volatility_regime': volatility_regime,
            'trend_regime': trend_regime,
            'momentum_regime': momentum_regime,
            'regime_summary': f"{volatility_regime}, {trend_regime}, {momentum_regime}"
        }
    
    def get_earnings_calendar(self, symbol: str) -> dict:
        """Get upcoming earnings information"""
        # This would normally fetch from an earnings calendar API
        # For simulation, we'll return sample data
        return {
            'symbol': symbol,
            'next_earnings_date': 'N/A',  # Would require real API call
            'quarterly_earnings_dates': ['2024-01-30', '2024-04-30', '2024-07-30', '2024-10-30'],
            'historical_surprises': []  # Would contain past earnings surprises
        }
    
    def analyze_correlation_with_market(self, symbol: str, data: pd.DataFrame) -> dict:
        """Analyze how the asset correlates with the broader market"""
        # In a real implementation, we would fetch market index data (SPY, QQQ, etc.)
        # For simulation, we'll create a correlation analysis framework
        
        # Calculate returns
        asset_returns = data['Close'].pct_change().dropna()
        
        # Simulated market returns (would come from SPY or other index)
        np.random.seed(42)  # For reproducible results
        market_returns = pd.Series(np.random.normal(0.0005, 0.015, len(asset_returns)))
        
        # Calculate correlation
        correlation = asset_returns.corr(market_returns) if len(asset_returns) > 1 and len(market_returns) > 1 else 0
        
        # Beta calculation (slope of regression line)
        if len(asset_returns) > 1 and len(market_returns) > 1:
            # Use a simple linear regression to estimate beta
            cov_matrix = np.cov(asset_returns, market_returns)
            beta = cov_matrix[0, 1] / cov_matrix[1, 1] if cov_matrix[1, 1] != 0 else 0
        else:
            beta = 1.0  # Default beta if insufficient data
            
        # Alpha calculation (excess return over what CAPM predicts)
        asset_return = asset_returns.mean() * 252  # Annualized
        market_return = market_returns.mean() * 252  # Annualized
        risk_free_rate = 0.05  # Assumed risk-free rate
        alpha = asset_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        
        return {
            'correlation_with_market': correlation,
            'beta': beta,
            'alpha': alpha,
            'correlation_label': self._correlation_label(abs(correlation))
        }
    
    def _correlation_label(self, correlation: float) -> str:
        """Convert correlation value to a descriptive label"""
        if correlation > 0.7:
            return "Highly Correlated"
        elif correlation > 0.4:
            return "Moderately Correlated"
        elif correlation > 0.1:
            return "Slightly Correlated"
        else:
            return "Uncorrelated"

    def get_comprehensive_research_report(self, symbol: str, asset_type: str = 'stock') -> str:
        """Generate a comprehensive research report for the asset"""
        # Get latest data
        if asset_type == 'crypto':
            data = self.data_api.get_crypto_data(symbol)
        else:
            data = self.data_api.get_stock_data(symbol)
        
        if data is None or data.empty:
            return f"No data available for {symbol}"
        
        # Initialize external data source
        external_source = ExternalDataSource()
        sentiment_analyzer = SentimentAnalyzer()
        
        # Perform various analyses
        sector_analysis = self.get_sector_analysis(symbol)
        market_regime = self.get_market_regime_analysis(symbol, data)
        correlation_analysis = self.analyze_correlation_with_market(symbol, data)
        
        # Get fundamental data from external sources (if stock)
        if asset_type == 'stock':
            fundamentals = external_source.get_fundamental_data(symbol)
        else:
            fundamentals = self.analyze_fundamentals(symbol, asset_type)
        
        # Get economic environment
        economic_environment = external_source.get_economic_indicators()
        
        # Get sector performance
        sector_performance = external_source.get_sector_etf_performance()
        
        # Get news sentiment (simulated)
        news_sentiment = self._get_news_sentiment(symbol, asset_type, sentiment_analyzer)
        
        # Format the report
        report = []
        report.append(f"🔍 COMPREHENSIVE RESEARCH REPORT FOR {symbol} ({asset_type.upper()})")
        report.append("="*70)
        
        # Market regime
        report.append(f"📊 TECHNICAL ANALYSIS & MARKET REGIME")
        report.append(f"  Volatility regime: {market_regime['volatility_regime']}")
        report.append(f"  Trend regime: {market_regime['trend_regime']}")
        report.append(f"  Momentum regime: {market_regime['momentum_regime']}")
        report.append(f"  Correlation with market: {correlation_analysis['correlation_with_market']:.3f}")
        report.append(f"  Beta: {correlation_analysis['beta']:.3f}")
        report.append(f"  Alpha: {correlation_analysis['alpha']:.3f}")
        
        # Sentiment Analysis
        report.append(f"\n🧠 MARKET SENTIMENT ANALYSIS")
        if news_sentiment:
            report.append(f"  Sentiment Score: {news_sentiment['sentiment_score']:.3f}")
            report.append(f"  Sentiment Label: {news_sentiment['sentiment_label']}")
            report.append(f"  Positive Mentions: {news_sentiment['positive_mentions']}")
            report.append(f"  Negative Mentions: {news_sentiment['negative_mentions']}")
        
        # Fundamental metrics (if available and for stocks)
        if asset_type == 'stock' and fundamentals:
            report.append(f"\n💼 FUNDAMENTAL ANALYSIS")
            if 'financial_ratios' in fundamentals:
                report.append(f"  Financial Ratios:")
                for key, value in fundamentals['financial_ratios'].items():
                    if value != 'N/A':
                        report.append(f"    {key.replace('_', ' ').title()}: {value}")
            if 'company_metrics' in fundamentals:
                report.append(f"  Company Metrics:")
                for key, value in fundamentals['company_metrics'].items():
                    if value != 'N/A':
                        report.append(f"    {key.replace('_', ' ').title()}: {value}")
            if 'recommendations' in fundamentals:
                report.append(f"  Analyst Recommendations:")
                for key, value in fundamentals['recommendations'].items():
                    if value != 'N/A':
                        report.append(f"    {key.replace('_', ' ').title()}: {value}")
        
        # Economic environment
        report.append(f"\n🏛️ MACROECONOMIC ENVIRONMENT")
        for indicator, data in economic_environment.items():
            if data:
                report.append(f"  {indicator.replace('_', ' ').upper()}: {data.get('latest_value', 'N/A')} ({data.get('unit', '')})")
        
        # Sector analysis
        report.append(f"\n🏢 SECTOR ANALYSIS")
        report.append(f"  Sector: {sector_analysis['sector_performance']['sector']}")
        report.append(f"  Sector relative performance: {sector_analysis['sector_performance']['relative_performance']}")
        report.append(f"  1D sector performance: {sector_analysis['sector_performance']['1_day']:.2f}%")
        report.append(f"  1W sector performance: {sector_analysis['sector_performance']['1_week']:.2f}%")
        report.append(f"  1M sector performance: {sector_analysis['sector_performance']['1_month']:.2f}%")
        
        # Sector ETF performance for comparison
        if asset_type == 'stock':
            report.append(f"\n📈 SECTOR ETF PERFORMANCE (for comparison)")
            for sector_name, etf_data in sector_performance.items():
                report.append(f"  {sector_name}: {etf_data['symbol']} ({etf_data['change_1m']:+.2f}% 1M)")
        
        # Economic calendar events
        upcoming_events = self.economic_calendar.get_upcoming_events()
        if upcoming_events:
            report.append(f"\n📅 UPCOMING ECONOMIC EVENTS")
            for event in upcoming_events[:3]:  # Show top 3 events
                report.append(f"  {event['date']}: {event['event']} ({event['impact']})")
        
        # Risk factors
        report.append(f"\n⚠️ KEY RISK FACTORS")
        report.append(f"  High market correlation may increase systematic risk")
        report.append(f"  Sector concentration risk")
        report.append(f"  Regulatory/compliance risks")
        report.append(f"  Macroeconomic sensitivity")
        report.append(f"  Sentiment volatility risk")
        
        # Overall recommendation based on multiple factors
        report.append(f"\n🎯 INTEGRATED RECOMMENDATION")
        if asset_type == 'stock' and fundamentals.get('recommendations', {}).get('recommendation') != 'N/A':
            report.append(f"  Analyst recommendation: {fundamentals['recommendations']['recommendation']}")
        
        report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report)

    def _get_news_sentiment(self, symbol: str, asset_type: str, sentiment_analyzer: SentimentAnalyzer) -> dict:
        """Get and analyze news sentiment for the symbol (simulated)"""
        # Simulate news articles for the symbol
        simulated_news = [
            {
                'title': f'{symbol} Posts Strong Quarterly Earnings',
                'summary': f'{symbol} reports better than expected quarterly results with strong revenue growth'
            },
            {
                'title': f'{symbol} Faces Regulatory Challenges',
                'summary': f'New regulations may impact {symbol} business model, analysts say'
            },
            {
                'title': f'{symbol} Announces New Partnership',
                'summary': f'{symbol} partners with major player to expand market presence'
            },
            {
                'title': f'Market Turmoil Affects {symbol}',
                'summary': f'{symbol} stock falls with broader market concerns'
            }
        ]
        
        # Analyze sentiment from simulated news
        return sentiment_analyzer.analyze_sentiment_from_news(symbol, simulated_news)


class RealTimeDataStream:
    """Handles real-time market data streaming"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.is_streaming = False
        self.subscribed_symbols = set()
        self.callbacks = []  # List of callback functions to call when new data arrives
        
    def start_stream(self, symbols: list):
        """Start streaming real-time data for specified symbols"""
        import threading
        self.subscribed_symbols = set(symbols)
        self.is_streaming = True
        
        # For this simulation, we'll create a thread that generates mock real-time data
        self.stream_thread = threading.Thread(target=self._simulate_stream, daemon=True)
        self.stream_thread.start()
    
    def stop_stream(self):
        """Stop the real-time data stream"""
        self.is_streaming = False
    
    def add_callback(self, callback_func):
        """Add a callback function to be called when new data arrives"""
        self.callbacks.append(callback_func)
    
    def _simulate_stream(self):
        """Simulate real-time data stream"""
        import time
        import random
        
        while self.is_streaming:
            if self.subscribed_symbols:
                # Generate mock real-time data for each symbol
                for symbol in self.subscribed_symbols:
                    mock_data = {
                        'symbol': symbol,
                        'price': self._get_mock_price(symbol),
                        'change': self._get_mock_change(),
                        'volume': self._get_mock_volume(),
                        'timestamp': datetime.now(),
                        'type': 'stock' if symbol not in ['BTC', 'ETH', 'SOL', 'ADA', 'XRP'] else 'crypto'
                    }
                    
                    # Call all registered callbacks with the new data
                    for callback in self.callbacks:
                        try:
                            callback(mock_data)
                        except Exception as e:
                            print(f"Error in callback function: {e}")
            
            # Simulate real-time updates every 2 seconds
            time.sleep(2)
    
    def _get_mock_price(self, symbol):
        """Generate a mock price based on the symbol"""
        # Create a base price for the symbol
        base_prices = {
            'AAPL': 175.00, 'GOOGL': 2750.00, 'MSFT': 325.00, 'TSLA': 250.00,
            'AMZN': 3200.00, 'META': 480.00, 'NVDA': 425.00, 'JPM': 150.00,
            'BTC': 40000.00, 'ETH': 2500.00, 'SOL': 100.00, 'ADA': 0.50, 'XRP': 0.60
        }
        
        base_price = base_prices.get(symbol, 100.00)  # Default to 100 if not found
        
        # Add small random fluctuations
        fluctuation = random.uniform(-1, 1)
        return base_price + fluctuation
    
    def _get_mock_change(self):
        """Generate a mock change value"""
        return random.uniform(-1, 1)
    
    def _get_mock_volume(self):
        """Generate a mock volume"""
        return random.randint(1000000, 5000000)


class AdvancedTechnicalIndicators:
    """Advanced technical indicators beyond the basic ones"""
    
    @staticmethod
    def calculate_stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> tuple:
        """Calculate Stochastic Oscillator (%K and %D lines)"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r
    
    @staticmethod
    def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=period).mean()
        mean_deviation = typical_price.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        return cci
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> tuple:
        """Calculate Average Directional Index (ADX)"""
        # Calculate directional movements
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        # Calculate true range
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        
        # Calculate directional indicators
        plus_dm = pd.Series(0.0, index=high.index)
        minus_dm = pd.Series(0.0, index=high.index)
        
        plus_dm[up_move > down_move] = up_move[up_move > down_move]
        plus_dm[up_move < 0] = 0
        minus_dm[down_move > up_move] = down_move[down_move > up_move]
        minus_dm[down_move < 0] = 0
        
        # Smooth the directional indicators
        plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / tr.ewm(alpha=1/period).mean())
        minus_di = 100 * (minus_dm.ewm(alpha=1/period).mean() / tr.ewm(alpha=1/period).mean())
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/period).mean()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def calculate_bollinger_bands_width(bb_upper: pd.Series, bb_middle: pd.Series, bb_lower: pd.Series) -> pd.Series:
        """Calculate Bollinger Bands Width"""
        bb_width = (bb_upper - bb_lower) / bb_middle
        return bb_width
    
    @staticmethod
    def calculate_macd_histogram(macd: pd.Series, signal: pd.Series) -> pd.Series:
        """Calculate MACD Histogram"""
        return macd - signal
    
    @staticmethod
    def calculate_ultimate_oscillator(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """Calculate Ultimate Oscillator"""
        # Calculate buying pressure and true range
        buying_pressure = close - pd.concat([low, close.shift()], axis=1).min(axis=1)
        true_range = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        
        # Calculate average of buying pressure over different timeframes
        avg7 = buying_pressure.rolling(7).sum() / true_range.rolling(7).sum()
        avg14 = buying_pressure.rolling(14).sum() / true_range.rolling(14).sum()
        avg28 = buying_pressure.rolling(28).sum() / true_range.rolling(28).sum()
        
        uo = 100 * ((7 * avg7) + (14 * avg14) + (28 * avg28)) / (7 + 14 + 28)
        return uo


class Backtester:
    """Backtesting engine for trading strategies"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.advanced_indicators = AdvancedTechnicalIndicators()
    
    def backtest_strategy(self, data: pd.DataFrame, strategy_func, initial_capital: float = 10000.0, **strategy_params) -> dict:
        """
        Backtest a trading strategy on historical data
        """
        # Initialize portfolio
        portfolio = {
            'cash': initial_capital,
            'holdings': 0,  # Number of shares held
            'value_history': [],
            'trades': [],
            'positions': []  # Track positions
        }
        
        # Generate signals using the strategy function
        signals = strategy_func(data)
        
        # Create a series to track positions
        position = pd.Series(0, index=data.index)
        
        # Process signals and calculate positions
        for signal in signals:
            date = signal['date']
            action = signal['action']
            
            # For simplicity, we'll implement a basic position sizing
            if action == 'BUY' and position.get(date, 0) == 0:  # New long position
                position[date:] = 1  # Enter long position
            elif action == 'SELL' and position.get(date, 0) == 1:  # Exit long position
                position[date:] = 0  # Exit long position
        
        # Calculate portfolio value over time
        portfolio_value = initial_capital
        
        for i in range(len(data)):
            current_date = data.index[i]
            current_price = data['Close'].iloc[i]
            
            # Calculate current portfolio value
            current_holdings_value = portfolio['holdings'] * current_price if portfolio['holdings'] > 0 else 0
            portfolio_value = portfolio['cash'] + current_holdings_value
            
            # Record value history
            portfolio['value_history'].append({
                'date': current_date,
                'value': portfolio_value,
                'cash': portfolio['cash'],
                'holdings_value': current_holdings_value,
                'total_shares': portfolio['holdings'],
                'price': current_price
            })
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(portfolio, initial_capital)
        
        return {
            'portfolio': portfolio,
            'metrics': metrics,
            'signals': signals
        }
    
    def _calculate_performance_metrics(self, portfolio: dict, initial_capital: float) -> dict:
        """Calculate performance metrics for backtested strategy"""
        if not portfolio['value_history']:
            return {
                'total_return': 0.0,
                'annualized_return': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'total_trades': 0
            }
        
        # Convert value history to series for calculations
        values = [v['value'] for v in portfolio['value_history']]
        returns = pd.Series(values).pct_change().dropna()
        
        # Calculate total return
        if values:
            total_return = (values[-1] - values[0]) / values[0]
        else:
            total_return = 0.0
        
        # Calculate annualized return (assuming daily data)
        years = len(values) / 252  # Trading days per year
        annualized_return = (values[-1] / values[0]) ** (1 / years) - 1 if years > 0 and values[0] > 0 else 0.0
        
        # Calculate volatility (annualized standard deviation)
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0.0
        
        # Calculate Sharpe ratio (assuming 0% risk-free rate)
        sharpe_ratio = annualized_return / volatility if volatility != 0 else 0.0
        
        # Calculate max drawdown
        if values:
            running_max = pd.Series(values).expanding().max()
            drawdown = (pd.Series(values) - running_max) / running_max
            max_drawdown = drawdown.min()
        else:
            max_drawdown = 0.0
        
        # Win rate and profit factor would require actual trade tracking
        # For now, return placeholder values
        total_trades = len(portfolio['trades'])
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': 0.0,  # Placeholder
            'profit_factor': 0.0,  # Placeholder
            'total_trades': total_trades
        }


class TradingStrategies:
    """Implementation of various trading strategies"""
    
    def __init__(self):
        self.indicators = AdvancedTechnicalIndicators()
        self.backtester = Backtester()  # Add backtester instance
    
    def golden_cross_strategy(self, data: pd.DataFrame) -> list:
        """Golden Cross/Death Cross strategy using SMA50 and SMA200"""
        signals = []
        
        sma_50 = data['Close'].rolling(50).mean()
        sma_200 = data['Close'].rolling(200).mean()
        
        # Find golden cross (SMA50 crosses above SMA200) and death cross (SMA50 crosses below SMA200)
        golden_cross = (sma_50 > sma_200) & (sma_50.shift(1) <= sma_200.shift(1))
        death_cross = (sma_50 < sma_200) & (sma_50.shift(1) >= sma_200.shift(1))
        
        for i in range(len(data)):
            if golden_cross.iloc[i]:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',  # Will be filled by calling function
                    'strategy': 'Golden Cross',
                    'action': 'BUY',
                    'reason': 'SMA50 crossed above SMA200 (Bullish signal)'
                })
            elif death_cross.iloc[i]:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'Golden Cross',
                    'action': 'SELL',
                    'reason': 'SMA50 crossed below SMA200 (Bearish signal)'
                })
        
        return signals
    
    def rsi_divergence_strategy(self, data: pd.DataFrame) -> list:
        """RSI Divergence strategy - looks for price and RSI divergences"""
        signals = []
        
        # Calculate RSI
        rsi = TechnicalIndicators.calculate_rsi(data['Close'])
        
        # Find divergences by comparing price highs/lows with RSI highs/lows
        # This is a simplified version - real divergence detection is more complex
        for i in range(50, len(data)-1):  # Start from 50 to have enough data
            # Look for bullish divergence (price makes lower low but RSI makes higher low)
            if (data['Low'].iloc[i] < data['Low'].iloc[i-10] and  # Price made lower low
                rsi.iloc[i] > rsi.iloc[i-10] and  # RSI made higher low
                rsi.iloc[i] < 30):  # RSI is in oversold territory
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'RSI Divergence',
                    'action': 'BUY',
                    'reason': 'Bullish divergence: Price made lower low but RSI made higher low'
                })
            
            # Look for bearish divergence (price makes higher high but RSI makes lower high)
            if (data['High'].iloc[i] > data['High'].iloc[i-10] and  # Price made higher high
                rsi.iloc[i] < rsi.iloc[i-10] and  # RSI made lower high
                rsi.iloc[i] > 70):  # RSI is in overbought territory
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'RSI Divergence',
                    'action': 'SELL',
                    'reason': 'Bearish divergence: Price made higher high but RSI made lower high'
                })
        
        return signals
    
    def bollinger_breakout_strategy(self, data: pd.DataFrame) -> list:
        """Bollinger Bands breakout strategy"""
        signals = []
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(data['Close'])
        
        # Generate signals when price breaks out of Bollinger Bands
        for i in range(len(data)):
            # Breakout above upper band (potential sell signal as overbought)
            if data['Close'].iloc[i] > bb_upper.iloc[i] and data['Close'].iloc[i-1] <= bb_upper.iloc[i-1]:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'Bollinger Breakout',
                    'action': 'SELL',
                    'reason': 'Price broke above upper Bollinger Band (potential overbought condition)'
                })
            # Breakout below lower band (potential buy signal as oversold)
            elif data['Close'].iloc[i] < bb_lower.iloc[i] and data['Close'].iloc[i-1] >= bb_lower.iloc[i-1]:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'Bollinger Breakout',
                    'action': 'BUY',
                    'reason': 'Price broke below lower Bollinger Band (potential oversold condition)'
                })
        
        return signals
    
    def stochastic_oscillator_strategy(self, data: pd.DataFrame) -> list:
        """Stochastic Oscillator strategy"""
        signals = []
        
        # Calculate Stochastic Oscillator
        k_line, d_line = self.indicators.calculate_stochastic_oscillator(
            data['High'], data['Low'], data['Close']
        )
        
        for i in range(1, len(data)):
            # Look for buy signal: %K crosses above %D in oversold area (< 20)
            if (k_line.iloc[i] > d_line.iloc[i] and 
                k_line.iloc[i-1] <= d_line.iloc[i-1] and 
                k_line.iloc[i] < 20):
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'Stochastic Oscillator',
                    'action': 'BUY',
                    'reason': 'K-line crossed above D-line in oversold territory (< 20)'
                })
            
            # Look for sell signal: %K crosses below %D in overbought area (> 80)
            if (k_line.iloc[i] < d_line.iloc[i] and 
                k_line.iloc[i-1] >= d_line.iloc[i-1] and 
                k_line.iloc[i] > 80):
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'Stochastic Oscillator',
                    'action': 'SELL',
                    'reason': 'K-line crossed below D-line in overbought territory (> 80)'
                })
        
        return signals
    
    def adx_trend_following_strategy(self, data: pd.DataFrame) -> list:
        """ADX Trend Following Strategy"""
        signals = []
        
        # Calculate ADX
        adx, plus_di, minus_di = self.indicators.calculate_adx(
            data['High'], data['Low'], data['Close']
        )
        
        for i in range(1, len(data)):
            # Strong trend with +DI above -DI (bullish)
            if adx.iloc[i] > 25 and plus_di.iloc[i] > minus_di.iloc[i] and plus_di.iloc[i-1] <= minus_di.iloc[i-1]:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'ADX Trend Following',
                    'action': 'BUY',
                    'reason': 'Strong bullish trend detected (ADX > 25, +DI above -DI)'
                })
            
            # Strong trend with -DI above +DI (bearish)
            if adx.iloc[i] > 25 and minus_di.iloc[i] > plus_di.iloc[i] and minus_di.iloc[i-1] <= plus_di.iloc[i-1]:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'ADX Trend Following',
                    'action': 'SELL',
                    'reason': 'Strong bearish trend detected (ADX > 25, -DI above +DI)'
                })
        
        return signals
    
    def cci_mean_reversion_strategy(self, data: pd.DataFrame) -> list:
        """Commodity Channel Index Mean Reversion Strategy"""
        signals = []
        
        # Calculate CCI
        cci = self.indicators.calculate_cci(data['High'], data['Low'], data['Close'])
        
        for i in range(1, len(data)):
            # Buy when CCI moves from oversold (-100) back above -100
            if cci.iloc[i] > -100 and cci.iloc[i-1] <= -100:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'CCI Mean Reversion',
                    'action': 'BUY',
                    'reason': 'CCI moved from oversold territory back above -100 (mean reversion)'
                })
            
            # Sell when CCI moves from overbought (+100) back below +100
            if cci.iloc[i] < 100 and cci.iloc[i-1] >= 100:
                signals.append({
                    'date': data.index[i],
                    'symbol': 'N/A',
                    'strategy': 'CCI Mean Reversion',
                    'action': 'SELL',
                    'reason': 'CCI moved from overbought territory back below +100 (mean reversion)'
                })
        
        return signals
    
    def all_strategies(self, data: pd.DataFrame, symbol: str = 'N/A') -> list:
        """Apply all strategies to generate trading signals"""
        all_signals = []
        
        # Apply each strategy
        strategies = [
            ('Golden Cross', self.golden_cross_strategy),
            ('RSI Divergence', self.rsi_divergence_strategy),
            ('Bollinger Breakout', self.bollinger_breakout_strategy),
            ('Stochastic Oscillator', self.stochastic_oscillator_strategy),
            ('ADX Trend Following', self.adx_trend_following_strategy),
            ('CCI Mean Reversion', self.cci_mean_reversion_strategy)
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                signals = strategy_func(data)
                # Add symbol to each signal
                for signal in signals:
                    signal['symbol'] = symbol
                all_signals.extend(signals)
            except Exception as e:
                print(f"Error in {strategy_name} strategy: {e}")
        
        return all_signals
    
    def backtest_strategy(self, data: pd.DataFrame, strategy_func, symbol: str, initial_capital: float = 10000.0) -> dict:
        """Backtest a specific strategy on historical data"""
        return self.backtester.backtest_strategy(data, strategy_func, initial_capital)
    
    def backtest_all_strategies(self, data: pd.DataFrame, symbol: str, initial_capital: float = 10000.0) -> dict:
        """Backtest all available strategies and compare results"""
        results = {}
        
        strategies = {
            'Golden Cross': self.golden_cross_strategy,
            'RSI Divergence': self.rsi_divergence_strategy,
            'Bollinger Breakout': self.bollinger_breakout_strategy,
            'Stochastic Oscillator': self.stochastic_oscillator_strategy,
            'ADX Trend Following': self.adx_trend_following_strategy,
            'CCI Mean Reversion': self.cci_mean_reversion_strategy
        }
        
        for strategy_name, strategy_func in strategies.items():
            try:
                result = self.backtest_strategy(data, strategy_func, symbol, initial_capital)
                results[strategy_name] = result
            except Exception as e:
                print(f"Error backtesting {strategy_name}: {e}")
                results[strategy_name] = {
                    'portfolio': {},
                    'metrics': {'total_return': 0, 'sharpe_ratio': 0, 'max_drawdown': 0},
                    'error': str(e)
                }
        
        return results


class PortfolioOptimizer:
    """Advanced portfolio optimization engine"""
    
    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate  # Default risk-free rate (5%)
    
    def calculate_portfolio_metrics(self, weights: np.array, returns: pd.DataFrame) -> dict:
        """Calculate portfolio metrics based on weights and returns"""
        # Calculate portfolio return
        portfolio_return = np.sum(returns.mean() * weights) * 252  # Annualized
        
        # Calculate portfolio volatility
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        
        # Calculate Sharpe ratio
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol != 0 else 0
        
        # Calculate maximum drawdown
        portfolio_returns = (returns * weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': portfolio_returns.quantile(0.05) * np.sqrt(252)  # Annualized VaR
        }
    
    def optimize_portfolio(self, returns: pd.DataFrame, method: str = 'sharpe') -> dict:
        """
        Optimize portfolio based on different methods:
        - 'sharpe': Maximize Sharpe ratio
        - 'min_vol': Minimize volatility
        - 'max_return': Maximize return (with volatility constraint)
        """
        from scipy.optimize import minimize
        import numpy as np
        
        n_assets = len(returns.columns)
        
        # Define objective function based on method
        def objective(weights):
            if method == 'sharpe':
                # Minimize negative Sharpe ratio (i.e., maximize Sharpe ratio)
                portfolio_metrics = self.calculate_portfolio_metrics(weights, returns)
                return -portfolio_metrics['sharpe_ratio']
            elif method == 'min_vol':
                # Minimize volatility
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
                return portfolio_vol
            elif method == 'max_return':
                # Minimize negative return (i.e., maximize return)
                portfolio_return = np.sum(returns.mean() * weights) * 252
                return -portfolio_return
            else:
                # Default to Sharpe ratio
                portfolio_metrics = self.calculate_portfolio_metrics(weights, returns)
                return -portfolio_metrics['sharpe_ratio']
        
        # Constraints: weights sum to 1, no shorting
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
        ]
        
        # Bounds: each weight between 0 and 1 (no shorting)
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        init_guess = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            objective,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            metrics = self.calculate_portfolio_metrics(optimal_weights, returns)
            
            return {
                'weights': optimal_weights,
                'metrics': metrics,
                'success': True,
                'message': 'Optimization successful'
            }
        else:
            return {
                'weights': init_guess,  # Return equal weights if optimization fails
                'metrics': self.calculate_portfolio_metrics(init_guess, returns),
                'success': False,
                'message': 'Optimization failed: ' + result.message
            }
    
    def efficient_frontier(self, returns: pd.DataFrame, n_points: int = 20) -> dict:
        """Calculate the efficient frontier"""
        # Calculate minimum and maximum possible returns
        min_return = returns.mean().min() * 252
        max_return = returns.mean().max() * 252
        
        target_returns = np.linspace(min_return, max_return, n_points)
        
        portfolio_points = []
        
        for target in target_returns:
            portfolio = self._optimize_for_target_return(returns, target)
            if portfolio['success']:
                portfolio_points.append({
                    'return': portfolio['metrics']['return'],
                    'volatility': portfolio['metrics']['volatility'],
                    'sharpe_ratio': portfolio['metrics']['sharpe_ratio'],
                    'weights': portfolio['weights']
                })
        
        return {
            'points': portfolio_points,
            'target_returns': target_returns
        }
    
    def _optimize_for_target_return(self, returns: pd.DataFrame, target_return: float):
        """Optimize portfolio for a specific target return (minimize volatility)"""
        from scipy.optimize import minimize
        import numpy as np
        
        n_assets = len(returns.columns)
        
        # Objective: minimize volatility
        def objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            return portfolio_vol
        
        # Constraints: weights sum to 1, target return achieved
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # Weights sum to 1
            {'type': 'eq', 'fun': lambda x: np.sum(returns.mean() * x) * 252 - target_return}  # Target return
        ]
        
        # Bounds: each weight between 0 and 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        init_guess = np.array([1/n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            objective,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            metrics = self.calculate_portfolio_metrics(optimal_weights, returns)
            
            return {
                'weights': optimal_weights,
                'metrics': metrics,
                'success': True,
                'message': 'Optimization successful'
            }
        else:
            return {
                'weights': init_guess,  # Return equal weights if optimization fails
                'metrics': self.calculate_portfolio_metrics(init_guess, returns),
                'success': False,
                'message': 'Optimization failed: ' + result.message
            }
    
    def risk_parity_allocation(self, returns: pd.DataFrame) -> dict:
        """Calculate risk parity allocation"""
        # Risk parity tries to equalize risk contribution of each asset
        # This is a simplified version - full implementation would use more sophisticated methods
        volatilities = returns.std() * np.sqrt(252)  # Annualized volatility
        inverse_vols = 1 / volatilities
        weights = inverse_vols / inverse_vols.sum()
        
        # Normalize weights to sum to 1
        weights = weights / weights.sum()
        
        metrics = self.calculate_portfolio_metrics(weights.values, returns)
        
        return {
            'weights': weights.values,
            'metrics': metrics,
            'success': True,
            'message': 'Risk parity allocation calculated'
        }
    
    def get_portfolio_allocation_report(self, returns: pd.DataFrame, allocation_method: str = 'sharpe') -> str:
        """Generate a comprehensive portfolio allocation report"""
        if allocation_method == 'sharpe':
            result = self.optimize_portfolio(returns, 'sharpe')
        elif allocation_method == 'min_vol':
            result = self.optimize_portfolio(returns, 'min_vol')
        elif allocation_method == 'risk_parity':
            result = self.risk_parity_allocation(returns)
        else:
            result = self.optimize_portfolio(returns, 'sharpe')  # Default to Sharpe
        
        # Format the report
        report = []
        report.append(f"💰 PORTFOLIO OPTIMIZATION REPORT")
        report.append("="*50)
        report.append(f"Allocation Method: {allocation_method.upper()}")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Assets: {list(returns.columns)}")
        
        if result['success']:
            report.append(f"\n📊 OPTIMIZED PORTFOLIO METRICS:")
            report.append(f"  Expected Annual Return: {result['metrics']['return']:.2%}")
            report.append(f"  Annual Volatility: {result['metrics']['volatility']:.2%}")
            report.append(f"  Sharpe Ratio: {result['metrics']['sharpe_ratio']:.3f}")
            report.append(f"  Max Drawdown: {result['metrics']['max_drawdown']:.2%}")
            report.append(f"  Value at Risk (95%): {result['metrics']['var_95']:.2%}")
            
            report.append(f"\n📈 ASSET ALLOCATION:")
            for i, asset in enumerate(returns.columns):
                weight = result['weights'][i]
                report.append(f"  {asset}: {weight:.2%}")
            
            # Calculate diversification metrics
            total_weight = sum(result['weights'])
            if len(returns.columns) > 1:
                concentration_ratio = sum([w**2 for w in result['weights']])  # Herfindahl-Hirschman Index
                report.append(f"\n⚖️ DIVERSIFICATION METRICS:")
                report.append(f"  Portfolio Concentration: {concentration_ratio:.3f} (lower is better)")
                report.append(f"  Number of Assets: {len(returns.columns)}")
        else:
            report.append(f"\n❌ OPTIMIZATION FAILED: {result['message']}")
        
        return "\n".join(report)


class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self):
        self.risk_models = {}
        self.position_limits = {}
        self.correlation_matrix = {}
    
    def calculate_position_sizing(self, account_size: float, risk_per_trade: float, 
                                 stop_loss_distance: float, current_price: float,
                                 volatility: float = None, correlation_factor: float = 1.0) -> dict:
        """
        Calculate optimal position size based on risk parameters
        """
        # Basic position sizing calculation
        if stop_loss_distance <= 0:
            return {
                'position_size': 0,
                'position_value': 0,
                'risk_amount': 0,
                'error': 'Stop loss distance must be greater than 0'
            }
        
        # Calculate risk amount for this trade
        risk_amount = account_size * risk_per_trade
        
        # Calculate position size based on stop loss
        position_size = risk_amount / stop_loss_distance
        
        # Adjust for volatility if provided
        if volatility is not None:
            # Reduce position size in high volatility environments
            volatility_adjustment = max(0.5, min(2.0, 1 / (volatility * 100)))
            position_size *= volatility_adjustment
        
        # Adjust for correlation with other positions
        correlation_adjustment = max(0.5, min(1.5, 1 / correlation_factor))
        position_size *= correlation_adjustment
        
        # Calculate position value
        position_value = position_size * current_price
        
        return {
            'position_size': round(position_size, 2),
            'position_value': round(position_value, 2),
            'risk_amount': round(risk_amount, 2),
            'volatility_adjustment': volatility_adjustment if volatility is not None else 1.0,
            'correlation_adjustment': correlation_adjustment
        }
    
    def calculate_value_at_risk(self, portfolio_value: float, confidence_level: float = 0.95,
                               time_horizon: int = 1, volatility: float = None, 
                               expected_return: float = 0) -> dict:
        """
        Calculate Value at Risk (VaR) for a portfolio
        """
        import scipy.stats as stats
        
        if volatility is None:
            # Default volatility assumption
            volatility = 0.02  # 2% daily volatility
        
        # Calculate VaR using parametric method
        # For a normal distribution, VaR = portfolio_value * (expected_return - z_score * volatility)
        z_score = stats.norm.ppf(1 - confidence_level)
        daily_var = portfolio_value * volatility * z_score
        
        # Scale to time horizon (assuming square root of time scaling)
        var_scaled = daily_var * (time_horizon ** 0.5)
        
        # Calculate expected shortfall (Conditional VaR)
        # ES = portfolio_value * volatility * (pdf(z_score) / (1 - confidence_level))
        pdf_z = stats.norm.pdf(z_score)
        expected_shortfall = portfolio_value * volatility * (pdf_z / (1 - confidence_level))
        expected_shortfall_scaled = expected_shortfall * (time_horizon ** 0.5)
        
        # VaR should be a positive value representing maximum loss
        # So we take the absolute value
        var_scaled = abs(var_scaled)
        expected_shortfall_scaled = abs(expected_shortfall_scaled)
        
        return {
            'var': round(var_scaled, 2),
            'expected_shortfall': round(expected_shortfall_scaled, 2),
            'confidence_level': confidence_level,
            'time_horizon_days': time_horizon,
            'volatility_assumption': volatility,
            'daily_var': round(abs(daily_var), 2)
        }
    
    def assess_portfolio_risk(self, positions: dict, market_data: dict) -> dict:
        """
        Assess overall portfolio risk
        """
        total_value = 0
        weighted_volatility = 0
        position_values = {}
        
        # Calculate position values and weights
        for symbol, position in positions.items():
            shares = position.get('shares', 0)
            entry_price = position.get('entry_price', 0)
            
            # Get current price from market data
            current_price = market_data.get(symbol, {}).get('price', entry_price)
            if current_price == 0:
                current_price = entry_price
            
            position_value = shares * current_price
            position_values[symbol] = position_value
            total_value += position_value
        
        # Calculate portfolio weights and risk contributions
        risk_contributions = {}
        for symbol, position_value in position_values.items():
            if total_value > 0:
                weight = position_value / total_value
                # Simplified risk contribution (would use actual correlations in production)
                risk_contribution = weight * 0.1  # Placeholder volatility
                risk_contributions[symbol] = {
                    'weight': round(weight, 4),
                    'value': round(position_value, 2),
                    'risk_contribution': round(risk_contribution, 4)
                }
        
        # Calculate portfolio concentration risk
        concentration_risk = self._calculate_concentration_risk(position_values)
        
        return {
            'total_portfolio_value': round(total_value, 2),
            'risk_contributions': risk_contributions,
            'concentration_risk': concentration_risk,
            'diversification_score': self._calculate_diversification_score(position_values)
        }
    
    def _calculate_concentration_risk(self, position_values: dict) -> dict:
        """
        Calculate portfolio concentration risk
        """
        if not position_values:
            return {'score': 0, 'level': 'None'}
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        total_value = sum(position_values.values())
        if total_value == 0:
            return {'score': 0, 'level': 'None'}
        
        hhi = sum((value / total_value) ** 2 for value in position_values.values())
        
        # Convert to concentration score (0-1 scale)
        concentration_score = hhi
        
        if concentration_score > 0.3:
            level = 'High'
        elif concentration_score > 0.15:
            level = 'Moderate'
        else:
            level = 'Low'
        
        return {
            'score': round(concentration_score, 4),
            'level': level,
            'top_positions': sorted(position_values.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _calculate_diversification_score(self, position_values: dict) -> float:
        """
        Calculate a diversification score (0-1 scale, higher is better)
        """
        if not position_values:
            return 1.0  # Fully diversified (no positions)
        
        num_positions = len(position_values)
        total_value = sum(position_values.values())
        
        if total_value == 0 or num_positions == 0:
            return 1.0
        
        # Calculate effective number of positions (entropy-based)
        weights = [value / total_value for value in position_values.values()]
        entropy = -sum(w * (np.log(w) if w > 0 else 0) for w in weights)
        max_entropy = np.log(num_positions) if num_positions > 0 else 1
        diversification_score = entropy / max_entropy if max_entropy > 0 else 1.0
        
        return round(diversification_score, 4)
    
    def suggest_risk_controls(self, portfolio_risk: dict, market_conditions: dict) -> list:
        """
        Suggest risk controls based on portfolio risk assessment and market conditions
        """
        suggestions = []
        
        concentration = portfolio_risk.get('concentration_risk', {})
        concentration_level = concentration.get('level', 'Low')
        
        if concentration_level == 'High':
            suggestions.append("HIGH CONCENTRATION RISK: Consider diversifying your portfolio")
            suggestions.append("   * Add positions in different sectors or asset classes")
            suggestions.append("   * Reduce exposure to largest positions")
        elif concentration_level == 'Moderate':
            suggestions.append("MODERATE CONCENTRATION RISK: Monitor position sizes")
            suggestions.append("   * Consider gradual diversification")
        
        diversification_score = portfolio_risk.get('diversification_score', 1.0)
        if diversification_score < 0.5:
            suggestions.append("LOW DIVERSIFICATION: Portfolio lacks diversification")
            suggestions.append("   * Add uncorrelated assets to reduce risk")
            suggestions.append("   * Consider ETFs for instant diversification")
        
        market_volatility = market_conditions.get('volatility', 0.02)
        if market_volatility > 0.05:  # High volatility
            suggestions.append("HIGH MARKET VOLATILITY: Increase caution")
            suggestions.append("   * Consider reducing position sizes")
            suggestions.append("   * Tighten stop-loss levels")
            suggestions.append("   * Use options for defined risk")
        elif market_volatility > 0.03:  # Moderate volatility
            suggestions.append("MODERATE MARKET VOLATILITY: Maintain disciplined risk management")
            suggestions.append("   * Monitor positions more frequently")
            suggestions.append("   * Review stop-loss levels regularly")
        
        return suggestions


class MarketAnalyzer:
    """Main market analysis class that integrates all components"""
    
    def __init__(self):
        self.data_api = MarketDataAPI()  # In production, provide actual API key
        self.indicators = TechnicalIndicators()
        self.advanced_indicators = AdvancedTechnicalIndicators()
        self.patterns = PatternRecognition()
        self.trading_strategies = TradingStrategies()
        self.watchlist = WatchlistManager()
        self.alerts = []
        self.real_time_stream = RealTimeDataStream()
        self.latest_realtime_data = {}  # Store latest real-time data
        self.portfolio_optimizer = PortfolioOptimizer()
        self.real_time_manager = RealTimeDataManager()  # Add real-time data manager
        self.risk_manager = RiskManager()  # Add risk manager
    
    def analyze_asset(self, symbol: str, data: pd.DataFrame, asset_type: str = 'stock') -> dict:
        """Comprehensive analysis of an asset"""
        # Calculate basic indicators
        indicators = self.calculate_indicators(data)
        
        # Detect patterns
        patterns = self.patterns.detect_patterns(data)
        
        # Generate trading signals
        signals = self.trading_strategies.all_strategies(data, symbol)
        
        # Calculate risk metrics
        risk_metrics = self.calculate_risk_metrics(data)
        
        # Calculate market metrics
        market_metrics = self.calculate_market_metrics(data, indicators)
        
        # Get current price and previous close
        current_price = data['Close'].iloc[-1] if not data.empty else 0
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
        
        # Get company name (for stocks)
        company_name = 'N/A'
        if asset_type == 'stock':
            company_name = self.get_company_name(symbol)
        
        return {
            'symbol': symbol,
            'asset_type': asset_type,
            'company_name': company_name,
            'current_price': current_price,
            'prev_close': prev_close,
            'indicators': indicators,
            'patterns': patterns,
            'signals': signals,
            'risk_metrics': risk_metrics,
            'market_metrics': market_metrics,
            'volume': data['Volume'].iloc[-1] if not data.empty and 'Volume' in data.columns else 0
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> dict:
        """Calculate comprehensive technical indicators"""
        if data is None or data.empty:
            return {}
        
        # Basic indicators
        indicators = {
            'rsi': self.indicators.calculate_rsi(data['Close']).iloc[-1],
            'sma_20': self.indicators.calculate_sma(data['Close'], 20).iloc[-1],
            'sma_50': self.indicators.calculate_sma(data['Close'], 50).iloc[-1],
            'ema_12': self.indicators.calculate_ema(data['Close'], 12).iloc[-1],
            'ema_26': self.indicators.calculate_ema(data['Close'], 26).iloc[-1],
            'macd': self.indicators.calculate_macd(data['Close'])[0].iloc[-1],
            'macd_signal': self.indicators.calculate_macd(data['Close'])[1].iloc[-1],
            'macd_histogram': self.indicators.calculate_macd(data['Close'])[2].iloc[-1],
            'bb_upper': self.indicators.calculate_bollinger_bands(data['Close'])[0].iloc[-1],
            'bb_middle': self.indicators.calculate_bollinger_bands(data['Close'])[1].iloc[-1],
            'bb_lower': self.indicators.calculate_bollinger_bands(data['Close'])[2].iloc[-1]
        }
        
        # Advanced indicators
        if 'High' in data.columns and 'Low' in data.columns and 'Volume' in data.columns:
            indicators['stochastic_k'], indicators['stochastic_d'] = self.advanced_indicators.calculate_stochastic_oscillator(
                data['High'], data['Low'], data['Close'])
            indicators['stochastic_k'] = indicators['stochastic_k'].iloc[-1]
            indicators['stochastic_d'] = indicators['stochastic_d'].iloc[-1]
            
            indicators['adx'] = self.advanced_indicators.calculate_adx(
                data['High'], data['Low'], data['Close'])[0].iloc[-1]
            indicators['cci'] = self.advanced_indicators.calculate_cci(
                data['High'], data['Low'], data['Close']).iloc[-1]
            
            # Only calculate ATR if we have enough data points
            if len(data) >= 14:
                indicators['atr'] = self.advanced_indicators.calculate_atr(
                    data['High'], data['Low'], data['Close']).iloc[-1]
        
        return indicators
    
    def calculate_risk_metrics(self, data: pd.DataFrame) -> dict:
        """Calculate risk metrics"""
        if data is None or data.empty:
            return {}
        
        returns = data['Close'].pct_change().dropna()
        
        return {
            'volatility': returns.std(),
            'avg_return': returns.mean(),
            'sharpe_ratio': returns.mean() / returns.std() if returns.std() != 0 else 0,
            'max_drawdown': (returns.min() if len(returns) > 0 else 0),
            'var_95': returns.quantile(0.05) if len(returns) > 0 else 0,
            'beta': 1.0,  # Would calculate against benchmark in real implementation
            'alpha': 0.0  # Would calculate against benchmark in real implementation
        }
    
    def calculate_market_metrics(self, data: pd.DataFrame, indicators: dict) -> dict:
        """Calculate market metrics"""
        if data is None or data.empty:
            return {}
        
        current_price = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
        
        return {
            'price_change': current_price - prev_close,
            'price_change_pct': ((current_price - prev_close) / prev_close * 100) if prev_close != 0 else 0,
            'volume': data['Volume'].iloc[-1] if 'Volume' in data.columns else 0,
            'rsi': indicators.get('rsi', 0)
        }
    
    def get_company_name(self, symbol: str) -> str:
        """Get company name for a stock symbol (placeholder implementation)"""
        # In a real implementation, this would query a database or API
        company_names = {
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla, Inc.',
            'META': 'Meta Platforms, Inc.',
            'NVDA': 'NVIDIA Corporation',
            'JPM': 'JPMorgan Chase & Co.',
            'JNJ': 'Johnson & Johnson',
            'V': 'Visa Inc.',
            'PG': 'Procter & Gamble Co.',
            'UNH': 'UnitedHealth Group Inc.',
            'HD': 'The Home Depot, Inc.',
            'MA': 'Mastercard Incorporated',
            'DIS': 'The Walt Disney Company',
            'ADBE': 'Adobe Inc.',
            'CRM': 'Salesforce, Inc.',
            'NFLX': 'Netflix, Inc.',
            'PYPL': 'PayPal Holdings, Inc.',
            'BAC': 'Bank of America Corporation',
            'VZ': 'Verizon Communications Inc.',
            'KO': 'The Coca-Cola Company',
            'XOM': 'Exxon Mobil Corporation',
            'PFE': 'Pfizer Inc.',
            'INTC': 'Intel Corporation',
            'CSCO': 'Cisco Systems, Inc.',
            'WMT': 'Walmart Inc.',
            'MRK': 'Merck & Co., Inc.',
            'T': 'AT&T Inc.',
            'ABBV': 'AbbVie Inc.',
            'CVX': 'Chevron Corporation',
            'LLY': 'Eli Lilly and Company',
            'AVGO': 'Broadcom Inc.',
            'ACN': 'Accenture plc',
            'TXN': 'Texas Instruments Incorporated',
            'CMCSA': 'Comcast Corporation',
            'DHR': 'Danaher Corporation',
            'COST': 'Costco Wholesale Corporation',
            'QCOM': 'Qualcomm Incorporated',
            'HON': 'Honeywell International Inc.',
            'NEE': 'NextEra Energy, Inc.',
            'BMY': 'Bristol-Myers Squibb Company'
        }
        
        return company_names.get(symbol.upper(), 'Unknown Company')
    
    def get_trading_signals(self, symbol: str, strategy_name: str = None) -> list:
        """Get trading signals for a symbol based on various strategies"""
        data = None
        # Determine if symbol is crypto or stock to fetch the right data
        watchlist_items = self.watchlist.get_watchlist()
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                if item_type == 'crypto':
                    data = self.watchlist.get_crypto_data(symbol)
                else:
                    data = self.watchlist.get_stock_data(symbol)
                break
        
        if data is None or data.empty:
            return []
        
        if strategy_name:
            # Get signals for a specific strategy
            strategy_method = getattr(self.trading_strategies, f"{strategy_name.lower().replace(' ', '_')}_strategy", None)
            if strategy_method:
                signals = strategy_method(data)
                # Add symbol to each signal
                for signal in signals:
                    signal['symbol'] = symbol
                return signals
            else:
                return []
        else:
            # Get signals for all strategies
            return self.trading_strategies.all_strategies(data, symbol)
    
    def backtest_strategy(self, symbol: str, strategy_name: str, initial_capital: float = 10000.0) -> dict:
        """Backtest a specific strategy for a symbol"""
        # Get the data for the symbol
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get data based on asset type
        if asset_type == 'crypto':
            data = self.watchlist.get_crypto_data(symbol)
        else:
            data = self.watchlist.get_stock_data(symbol)
        
        if data is None or data.empty:
            return {'error': f'No data available for {symbol}'}
        
        # Get the strategy function
        strategy_method = getattr(self.trading_strategies, f"{strategy_name.lower().replace(' ', '_')}_strategy", None)
        if not strategy_method:
            return {'error': f'Strategy {strategy_name} not found'}
        
        # Run the backtest
        try:
            result = self.trading_strategies.backtest_strategy(data, strategy_method, symbol, initial_capital)
            return result
        except Exception as e:
            return {'error': f'Error running backtest: {str(e)}'}
    
    def backtest_all_strategies(self, symbol: str, initial_capital: float = 10000.0) -> dict:
        """Backtest all available strategies for a symbol and compare results"""
        # Get the data for the symbol
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get data based on asset type
        if asset_type == 'crypto':
            data = self.watchlist.get_crypto_data(symbol)
        else:
            data = self.watchlist.get_stock_data(symbol)
        
        if data is None or data.empty:
            return {'error': f'No data available for {symbol}'}
        
        # Run all backtests
        try:
            results = self.trading_strategies.backtest_all_strategies(data, symbol, initial_capital)
            return results
        except Exception as e:
            return {'error': f'Error running backtests: {str(e)}'}
    
    def get_real_time_quote(self, symbol: str) -> dict:
        """Get real-time quote for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get real-time quote from API
        return self.data_api.get_real_time_quote(symbol, asset_type)
    
    def subscribe_to_real_time_updates(self, symbol: str, callback_func=None) -> bool:
        """Subscribe to real-time updates for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Subscribe through real-time manager
        return self.real_time_manager.subscribe(symbol, asset_type, callback_func)
    
    def unsubscribe_from_real_time_updates(self, symbol: str) -> bool:
        """Unsubscribe from real-time updates for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Unsubscribe through real-time manager
        return self.real_time_manager.unsubscribe(symbol, asset_type)
    
    def get_latest_real_time_data(self, symbol: str) -> dict:
        """Get the latest real-time data for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get latest data from real-time manager
        return self.real_time_manager.get_latest_data(symbol, asset_type)
    
    def calculate_position_sizing(self, account_size: float, risk_per_trade: float, 
                                 stop_loss_distance: float, current_price: float,
                                 volatility: float = None, correlation_factor: float = 1.0) -> dict:
        """Calculate optimal position size using risk management"""
        return self.risk_manager.calculate_position_sizing(
            account_size, risk_per_trade, stop_loss_distance, 
            current_price, volatility, correlation_factor
        )
    
    def calculate_value_at_risk(self, portfolio_value: float, confidence_level: float = 0.95,
                               time_horizon: int = 1, volatility: float = None, 
                               expected_return: float = 0) -> dict:
        """Calculate Value at Risk for a portfolio"""
        return self.risk_manager.calculate_value_at_risk(
            portfolio_value, confidence_level, time_horizon, 
            volatility, expected_return
        )
    
    def assess_portfolio_risk(self, positions: dict, market_data: dict) -> dict:
        """Assess overall portfolio risk"""
        return self.risk_manager.assess_portfolio_risk(positions, market_data)
    
    def suggest_risk_controls(self, portfolio_risk: dict, market_conditions: dict) -> list:
        """Suggest risk controls based on portfolio risk assessment"""
        return self.risk_manager.suggest_risk_controls(portfolio_risk, market_conditions)


def analyze_asset(symbol: str, asset_type: str = 'stock', period: str = "6mo", interval: str = "1d"):
    
    def add_to_watchlist(self, symbol: str, asset_type: str = 'stock'):
        """Add a symbol to the watchlist"""
        self.watchlist.add_to_watchlist(symbol, asset_type)
    
    def add_stock_to_watchlist(self, symbol: str):
        """Add a stock to the watchlist"""
        self.watchlist.add_to_watchlist(symbol, 'stock')
    
    def add_crypto_to_watchlist(self, symbol: str):
        """Add a cryptocurrency to the watchlist"""
        self.watchlist.add_to_watchlist(symbol, 'crypto')

    def analyze_asset(self, symbol: str, data: pd.DataFrame, asset_type: str = 'stock') -> dict:
        """Perform comprehensive analysis on a single asset (stock or crypto)"""
        analysis = {
            'symbol': symbol,
            'asset_type': asset_type,
            'timestamp': datetime.now(),
            'current_price': data['Close'].iloc[-1],
            'prev_close': data['Close'].iloc[-2] if len(data) > 1 else data['Close'].iloc[-1],
            'indicators': {},
            'patterns': [],
            'signals': [],
            'risk_metrics': {},
            'market_metrics': {}  # Additional metrics specific to crypto or stock
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
        analysis['indicators']['macd_histogram'] = histogram.iloc[-1]
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.indicators.calculate_bollinger_bands(close_prices)
        analysis['indicators']['bb_upper'] = bb_upper.iloc[-1]
        analysis['indicators']['bb_middle'] = bb_middle.iloc[-1]
        analysis['indicators']['bb_lower'] = bb_lower.iloc[-1]
        
        # Calculate advanced technical indicators
        # Stochastic Oscillator
        k_percent, d_percent = self.advanced_indicators.calculate_stochastic_oscillator(
            data['High'], data['Low'], data['Close']
        )
        analysis['indicators']['stoch_k'] = k_percent.iloc[-1]
        analysis['indicators']['stoch_d'] = d_percent.iloc[-1]
        
        # Williams %R
        williams_r = self.advanced_indicators.calculate_williams_r(
            data['High'], data['Low'], data['Close']
        )
        analysis['indicators']['williams_r'] = williams_r.iloc[-1]
        
        # Commodity Channel Index
        cci = self.advanced_indicators.calculate_cci(
            data['High'], data['Low'], data['Close']
        )
        analysis['indicators']['cci'] = cci.iloc[-1]
        
        # Average True Range
        atr = self.advanced_indicators.calculate_atr(
            data['High'], data['Low'], data['Close']
        )
        analysis['indicators']['atr'] = atr.iloc[-1]
        
        # ADX (Average Directional Index)
        adx, plus_di, minus_di = self.advanced_indicators.calculate_adx(
            data['High'], data['Low'], data['Close']
        )
        analysis['indicators']['adx'] = adx.iloc[-1]
        analysis['indicators']['plus_di'] = plus_di.iloc[-1]
        analysis['indicators']['minus_di'] = minus_di.iloc[-1]
        
        # Bollinger Bands Width
        bb_upper_series = data['Close'].rolling(20).mean() + (data['Close'].rolling(20).std() * 2)
        bb_lower_series = data['Close'].rolling(20).mean() - (data['Close'].rolling(20).std() * 2)
        bb_middle_series = data['Close'].rolling(20).mean()
        
        bb_width = self.advanced_indicators.calculate_bollinger_bands_width(
            bb_upper_series, bb_middle_series, bb_lower_series
        )
        analysis['indicators']['bb_width'] = bb_width.iloc[-1]
        
        # Generate trading signals
        current_price = analysis['current_price']
        sma_20 = analysis['indicators']['sma_20']
        sma_50 = analysis['indicators']['sma_50']
        rsi_value = analysis['indicators']['rsi']
        macd_val = analysis['indicators']['macd']
        macd_sig = analysis['indicators']['macd_signal']
        
        # Signal generation
        if rsi_value < 30:
            analysis['signals'].append("RSI: POTENTIALLY OVERSOLD")
        elif rsi_value > 70:
            analysis['signals'].append("RSI: POTENTIALLY OVERBOUGHT")
            
        if current_price > sma_20 and sma_20 > sma_50:
            analysis['signals'].append("SMA: BULLISH TREND (Golden Cross)")
        elif current_price < sma_20 and sma_20 < sma_50:
            analysis['signals'].append("SMA: BEARISH TREND (Death Cross)")
        
        if macd_val > macd_sig:
            analysis['signals'].append("MACD: BULLISH SIGNAL")
        else:
            analysis['signals'].append("MACD: BEARISH SIGNAL")
        
        # Pattern recognition
        analysis['patterns'] = self.patterns.detect_support_resistance(close_prices)
        
        # Risk metrics
        returns = close_prices.pct_change().dropna()
        analysis['risk_metrics'] = {
            'volatility': returns.std(),
            'avg_return': returns.mean(),
            'sharpe_ratio': returns.mean() / returns.std() if returns.std() != 0 else 0,
            'max_drawdown': (returns.min() if len(returns) > 0 else 0),
            'var_95': returns.quantile(0.05) if len(returns) > 0 else 0
        }
        
        # Market-specific metrics
        if asset_type == 'crypto':
            # Additional crypto-specific metrics
            analysis['market_metrics'] = {
                '24h_change': ((data['Close'].iloc[-1] - data['Close'].iloc[-24]) / data['Close'].iloc[-24] * 100) if len(data) >= 24 else 0,
                'volume_trend': 'Increasing' if len(data) > 1 and data['Volume'].iloc[-1] > data['Volume'].iloc[-2] else 'Decreasing',
                'market_cap_rank': 'N/A'  # Would require additional API call in production
            }
        else:
            # Stock-specific metrics
            analysis['market_metrics'] = {
                'pe_ratio': 'N/A',  # Would require additional API call in production
                'dividend_yield': 'N/A',  # Would require additional API call in production
                'eps': 'N/A'  # Would require additional API call in production
            }
        
        return analysis

    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> dict:
        """Perform comprehensive analysis on a single stock (wrapper for analyze_asset)"""
        return self.analyze_asset(symbol, data, 'stock')

    def analyze_watchlist(self) -> list:
        """Analyze all assets in the watchlist"""
        watchlist_items = self.watchlist.get_watchlist()
        results = []
        
        for symbol, asset_type in watchlist_items:
            try:
                if asset_type.lower() == 'crypto':
                    data = self.watchlist.get_crypto_data(symbol)
                else:
                    data = self.watchlist.get_stock_data(symbol)
                    
                if data is not None and not data.empty:
                    analysis = self.analyze_asset(symbol, data, asset_type)
                    results.append(analysis)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
        
        return results

    def get_analysis_summary(self) -> str:
        """Get a summary of all watchlist analyses"""
        analyses = self.analyze_watchlist()
        summary = []
        
        for analysis in analyses:
            symbol = analysis['symbol']
            asset_type = analysis['asset_type']
            price = analysis['current_price']
            rsi = analysis['indicators']['rsi']
            volatility = analysis['risk_metrics']['volatility']
            
            if analysis['asset_type'] == 'crypto':
                summary.append(f"🪙 {symbol} (Crypto): ${price:.2f}, RSI: {rsi:.2f}, Vol: {volatility:.4f}")
            else:
                summary.append(f"📈 {symbol} (Stock): ${price:.2f}, RSI: {rsi:.2f}, Vol: {volatility:.4f}")
        
        return "\n".join(summary) if summary else "No assets in watchlist or no data available"

    def get_research_report(self, symbol: str, asset_type: str = 'stock') -> str:
        """Get comprehensive market research report for a symbol"""
        researcher = MarketResearcher()
        return researcher.get_comprehensive_research_report(symbol, asset_type)

    def get_fundamental_data(self, symbol: str) -> dict:
        """Get fundamental data for a stock from external sources"""
        external_source = ExternalDataSource()
        return external_source.get_fundamental_data(symbol)
    
    def get_economic_environment(self) -> dict:
        """Get the current economic environment"""
        external_source = ExternalDataSource()
        return external_source.get_economic_indicators()
    
    def get_sector_performance(self, symbol: str) -> dict:
        """Get sector performance data"""
        # This would identify the sector of the symbol and return sector performance
        external_source = ExternalDataSource()
        return external_source.get_sector_etf_performance()
    
    def generate_advanced_ai_insights(self, symbol: str, analysis: dict) -> str:
        """Generate advanced AI insights using the AdvancedAIInsights engine"""
        advanced_insights = AdvancedAIInsights()
        comprehensive_insights = advanced_insights.generate_comprehensive_insights(
            symbol, analysis, analysis.get('asset_type', 'stock')
        )
        
        # Format the insights for display
        output = []
        output.append(f"🤖 ADVANCED AI INSIGHTS FOR {symbol}")
        output.append("="*50)
        
        # Technical insights
        tech = comprehensive_insights['technical_insights']
        output.append(f"📈 TECHNICAL ANALYSIS")
        output.append(f"  Bullish signals: {tech['bullish_signals_count']}")
        output.append(f"  Bearish signals: {tech['bearish_signals_count']}")
        output.append(f"  Momentum strength: {tech['momentum_strength']:.2f}")
        output.append(f"  Trend strength: {tech['trend_strength']:.2f}")
        output.append(f"  Volatility: {tech['volatility_assessment']}")
        output.append(f"  RSI: {tech['rsi_assessment']}")
        
        # Market regime
        regime = comprehensive_insights['market_regime_insights']
        output.append(f"\n📊 MARKET REGIME")
        output.append(f"  Regime: {regime['regime']}")
        output.append(f"  Trend strength: {regime['trend_strength']}")
        output.append(f"  Confidence: {regime['confidence']}")
        
        # Sentiment analysis
        sentiment = comprehensive_insights['sentiment_insights']
        output.append(f"\n🧠 SENTIMENT ANALYSIS")
        output.append(f"  News sentiment: {sentiment['news_sentiment']['sentiment_label']}")
        output.append(f"  Social sentiment: {sentiment['social_sentiment']['sentiment_label']}")
        output.append(f"  Combined sentiment: {sentiment['sentiment_label']}")
        
        # Risk assessment
        risk = comprehensive_insights['risk_assessment']
        output.append(f"\n⚠️ RISK ASSESSMENT")
        output.append(f"  Overall risk: {risk['overall_risk_level']}")
        output.append(f"  Volatility risk: {risk['volatility_risk']}")
        output.append(f"  Drawdown risk: {risk['drawdown_risk']}")
        output.append(f"  Value-at-risk: {risk['value_at_risk']}")
        output.append(f"  RSI risk: {risk['rsi_risk']}")
        output.append(f"  Summary: {risk['risk_summary']}")
        
        # Final recommendation
        output.append(f"\n🎯 FINAL RECOMMENDATION")
        output.append(f"  Action: {comprehensive_insights['combined_recommendation']}")
        output.append(f"  Confidence: {comprehensive_insights['confidence_score']:.2%}")
        
        output.append(f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)

    def generate_ai_insights(self, symbol, analysis):
        """Generate AI-powered insights for an asset (stock or crypto)"""
        asset_type = analysis.get('asset_type', 'stock')
        if asset_type == 'crypto':
            insights = [f"🤖 AI Insights for {symbol} (Crypto)", "="*40]
        else:
            insights = [f"🤖 AI Insights for {symbol} (Stock)", "="*40]
        
        rsi = analysis['indicators']['rsi']
        sma_20 = analysis['indicators']['sma_20']
        sma_50 = analysis['indicators']['sma_50']
        current_price = analysis['current_price']
        macd = analysis['indicators']['macd']
        macd_signal = analysis['indicators']['macd_signal']
        volatility = analysis['risk_metrics']['volatility']
        
        # RSI insight
        if rsi < 30:
            insights.append(f"📈 RSI: {rsi:.2f} - POTENTIALLY OVERSOLD (Potential buying opportunity)")
        elif rsi > 70:
            insights.append(f"📉 RSI: {rsi:.2f} - POTENTIALLY OVERBOUGHT (Potential selling opportunity)")
        else:
            insights.append(f"⚖️ RSI: {rsi:.2f} - NEUTRAL (No strong signal)")
        
        # Moving average insight
        if current_price > sma_20 > sma_50:
            insights.append(f"📈 Trend: BULLISH (Price > SMA20 > SMA50)")
        elif current_price < sma_20 < sma_50:
            insights.append(f"📉 Trend: BEARISH (Price < SMA20 < SMA50)")
        else:
            insights.append(f"⚖️ Trend: NEUTRAL (No clear moving average trend)")
        
        # MACD insight
        if macd > macd_signal:
            insights.append(f"📊 MACD: Bullish momentum (MACD above signal line)")
        else:
            insights.append(f"📊 MACD: Bearish momentum (MACD below signal line)")
        
        # Risk insight
        if volatility < 0.02:
            insights.append(f"🛡️ Risk: LOW (Volatility: {volatility:.4f})")
        elif volatility < 0.05:
            insights.append(f"⚠️ Risk: MODERATE (Volatility: {volatility:.4f})")
        else:
            insights.append(f"🚨 Risk: HIGH (Volatility: {volatility:.4f})")
        
        # Market-specific insights
        market_metrics = analysis.get('market_metrics', {})
        if asset_type == 'crypto':
            # Crypto-specific insights
            change_24h = market_metrics.get('24h_change', 0)
            volume_trend = market_metrics.get('volume_trend', 'N/A')
            insights.append(f"🪙 24h Change: {change_24h:.2f}%")
            insights.append(f"📈 Volume Trend: {volume_trend}")
            insights.append(f"💡 Crypto markets are generally more volatile than traditional stocks")
        else:
            # Stock-specific insights
            pe_ratio = market_metrics.get('pe_ratio', 'N/A')
            div_yield = market_metrics.get('dividend_yield', 'N/A')
            insights.append(f"💼 P/E Ratio: {pe_ratio}")
            insights.append(f"💰 Dividend Yield: {div_yield}")
        
        # Signal summary
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
        
        # Additional market context
        if asset_type == 'crypto':
            insights.append(f"\n🌐 Crypto Market Note: Cryptocurrencies can be affected by regulatory news, technological developments, and macroeconomic factors.")
        else:
            insights.append(f"\n🏢 Stock Market Note: Consider company fundamentals, earnings reports, and sector performance alongside technical analysis.")
        
        return "\n".join(insights) + "\n\nLast updated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def get_advanced_technical_indicators(self, data: pd.DataFrame) -> dict:
        """Calculate and return advanced technical indicators"""
        indicators = {}
        
        # Stochastic Oscillator
        k_percent, d_percent = self.advanced_indicators.calculate_stochastic_oscillator(
            data['High'], data['Low'], data['Close']
        )
        indicators['stoch_k'] = k_percent
        indicators['stoch_d'] = d_percent
        
        # Williams %R
        williams_r = self.advanced_indicators.calculate_williams_r(
            data['High'], data['Low'], data['Close']
        )
        indicators['williams_r'] = williams_r
        
        # Commodity Channel Index
        cci = self.advanced_indicators.calculate_cci(
            data['High'], data['Low'], data['Close']
        )
        indicators['cci'] = cci
        
        # Average True Range
        atr = self.advanced_indicators.calculate_atr(
            data['High'], data['Low'], data['Close']
        )
        indicators['atr'] = atr
        
        # ADX (Average Directional Index)
        adx, plus_di, minus_di = self.advanced_indicators.calculate_adx(
            data['High'], data['Low'], data['Close']
        )
        indicators['adx'] = adx
        indicators['plus_di'] = plus_di
        indicators['minus_di'] = minus_di
        
        # Bollinger Bands Width
        bb_upper = data['Close'].rolling(20).mean() + (data['Close'].rolling(20).std() * 2)
        bb_lower = data['Close'].rolling(20).mean() - (data['Close'].rolling(20).std() * 2)
        bb_middle = data['Close'].rolling(20).mean()
        
        bb_width = self.advanced_indicators.calculate_bollinger_bands_width(
            bb_upper, bb_middle, bb_lower
        )
        indicators['bb_width'] = bb_width
        
        return indicators

    def get_trading_signals(self, symbol: str, strategy_name: str = None) -> list:
        """Get trading signals for a symbol based on various strategies"""
        data = None
        # Determine if symbol is crypto or stock to fetch the right data
        watchlist_items = self.watchlist.get_watchlist()
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                if item_type == 'crypto':
                    data = self.watchlist.get_crypto_data(symbol)
                else:
                    data = self.watchlist.get_stock_data(symbol)
                break
        
        if data is None or data.empty:
            return []
        
        if strategy_name:
            # Get signals for a specific strategy
            strategy_method = getattr(self.trading_strategies, f"{strategy_name.lower().replace(' ', '_')}_strategy", None)
            if strategy_method:
                signals = strategy_method(data)
                # Add symbol to each signal
                for signal in signals:
                    signal['symbol'] = symbol
                return signals
            else:
                return []
        else:
            # Get signals for all strategies
            return self.trading_strategies.all_strategies(data, symbol)
    
    def backtest_strategy(self, symbol: str, strategy_name: str, initial_capital: float = 10000.0) -> dict:
        """Backtest a specific strategy for a symbol"""
        # Get the data for the symbol
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get data based on asset type
        if asset_type == 'crypto':
            data = self.watchlist.get_crypto_data(symbol)
        else:
            data = self.watchlist.get_stock_data(symbol)
        
        if data is None or data.empty:
            return {'error': f'No data available for {symbol}'}
        
        # Get the strategy function
        strategy_method = getattr(self.trading_strategies, f"{strategy_name.lower().replace(' ', '_')}_strategy", None)
        if not strategy_method:
            return {'error': f'Strategy {strategy_name} not found'}
        
        # Run the backtest
        try:
            result = self.trading_strategies.backtest_strategy(data, strategy_method, symbol, initial_capital)
            return result
        except Exception as e:
            return {'error': f'Error running backtest: {str(e)}'}
    
    def get_real_time_quote(self, symbol: str) -> dict:
        """Get real-time quote for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get real-time quote from API
        return self.data_api.get_real_time_quote(symbol, asset_type)
    
    def subscribe_to_real_time_updates(self, symbol: str, callback_func=None) -> bool:
        """Subscribe to real-time updates for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Subscribe through real-time manager
        return self.real_time_manager.subscribe(symbol, asset_type, callback_func)
    
    def unsubscribe_from_real_time_updates(self, symbol: str) -> bool:
        """Unsubscribe from real-time updates for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Unsubscribe through real-time manager
        return self.real_time_manager.unsubscribe(symbol, asset_type)
    
    def get_latest_real_time_data(self, symbol: str) -> dict:
        """Get the latest real-time data for a symbol"""
        # Determine asset type from watchlist
        watchlist_items = self.watchlist.get_watchlist()
        asset_type = 'stock'  # Default
        
        for item_symbol, item_type in watchlist_items:
            if item_symbol == symbol:
                asset_type = item_type
                break
        
        # Get latest data from real-time manager
        return self.real_time_manager.get_latest_data(symbol, asset_type)

    def get_all_trading_signals(self, symbol: str) -> dict:
        """Get all trading signals for a symbol with detailed information"""
        signals = self.get_trading_signals(symbol)
        
        # Group signals by strategy
        strategy_signals = {}
        for signal in signals:
            strategy = signal.get('strategy', 'Unknown')
            if strategy not in strategy_signals:
                strategy_signals[strategy] = []
            strategy_signals[strategy].append(signal)
        
        # Format results
        result = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'total_signals': len(signals),
            'strategy_breakdown': strategy_signals,
            'buy_signals': [s for s in signals if s.get('action') == 'BUY'],
            'sell_signals': [s for s in signals if s.get('action') == 'SELL']
        }
        
        return result

    def start_real_time_stream(self, symbols: list = None):
        """Start real-time data streaming for symbols in the watchlist or specified symbols"""
        if symbols is None:
            # Get all symbols from the watchlist
            watchlist_items = self.watchlist.get_watchlist()
            symbols = [item[0] for item in watchlist_items]
        
        self.real_time_stream = RealTimeDataStream()
        
        def update_callback(data):
            """Callback function to update data when new real-time data arrives"""
            # For now, we'll just store the latest data
            # In a real application, this would update charts, alerts, etc.
            self.latest_realtime_data[data['symbol']] = data
        
        self.real_time_stream.add_callback(update_callback)
        self.real_time_stream.start_stream(symbols)
        
        # Initialize the latest_realtime_data dict if not already done
        if not hasattr(self, 'latest_realtime_data'):
            self.latest_realtime_data = {}
        
        return True

    def stop_real_time_stream(self):
        """Stop the real-time data stream"""
        if hasattr(self, 'real_time_stream'):
            self.real_time_stream.stop_stream()
        return True

    def get_real_time_data(self, symbol: str):
        """Get the latest real-time data for a symbol"""
        if hasattr(self, 'latest_realtime_data') and symbol in self.latest_realtime_data:
            return self.latest_realtime_data[symbol]
        return None

    def build_optimal_portfolio(self, symbols: list, allocation_method: str = 'sharpe', lookback_days: int = 252) -> dict:
        """Build an optimal portfolio from a list of symbols"""
        # Fetch historical data for all symbols
        all_data = {}
        valid_symbols = []
        
        for symbol in symbols:
            # Determine if symbol is crypto or stock to fetch the right data
            watchlist_items = self.watchlist.get_watchlist()
            asset_type = 'stock'  # Default to stock
            for item_symbol, item_type in watchlist_items:
                if item_symbol == symbol:
                    asset_type = item_type
                    break
            
            if asset_type == 'crypto':
                data = self.watchlist.get_crypto_data(symbol)
            else:
                data = self.watchlist.get_stock_data(symbol)
            
            if data is not None and not data.empty and 'Close' in data.columns:
                # Get the last N days of data
                if len(data) > lookback_days:
                    data = data.tail(lookback_days)
                
                # Calculate returns
                data['Returns'] = data['Close'].pct_change().dropna()
                all_data[symbol] = data['Returns']
                valid_symbols.append(symbol)
        
        if len(valid_symbols) < 2:
            return {
                'success': False,
                'message': 'Need at least 2 valid symbols with sufficient data to build a portfolio',
                'allocation': {},
                'metrics': {}
            }
        
        # Combine returns into a single DataFrame
        returns_df = pd.DataFrame(all_data)
        returns_df = returns_df.dropna()  # Remove any days where not all assets have data
        
        if len(returns_df) < 30:  # Need at least 30 days of data
            return {
                'success': False,
                'message': 'Insufficient data to build portfolio (need at least 30 days)',
                'allocation': {},
                'metrics': {}
            }
        
        # Use the portfolio optimizer
        report = self.portfolio_optimizer.get_portfolio_allocation_report(returns_df, allocation_method)
        
        # Get the allocation result
        if allocation_method == 'sharpe':
            result = self.portfolio_optimizer.optimize_portfolio(returns_df, 'sharpe')
        elif allocation_method == 'min_vol':
            result = self.portfolio_optimizer.optimize_portfolio(returns_df, 'min_vol')
        elif allocation_method == 'risk_parity':
            result = self.portfolio_optimizer.risk_parity_allocation(returns_df)
        else:
            result = self.portfolio_optimizer.optimize_portfolio(returns_df, 'sharpe')
        
        portfolio_allocation = {}
        for i, symbol in enumerate(returns_df.columns):
            portfolio_allocation[symbol] = result['weights'][i]
        
        return {
            'success': result['success'],
            'message': result['message'],
            'allocation': portfolio_allocation,
            'metrics': result['metrics'],
            'report': report,
            'allocation_method': allocation_method
        }

    def get_portfolio_recommendation(self, symbols: list) -> str:
        """Generate a comprehensive portfolio recommendation report"""
        # Get optimal portfolio with different methods for comparison
        methods = ['sharpe', 'min_vol', 'risk_parity']
        reports = {}
        
        for method in methods:
            result = self.build_optimal_portfolio(symbols, method)
            if result['success']:
                reports[method] = result
        
        # Format the recommendation report
        report = []
        report.append("🏆 PORTFOLIO RECOMMENDATION REPORT")
        report.append("="*60)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Assets in analysis: {symbols}")
        
        if not reports:
            report.append("\n❌ No valid portfolio could be constructed with the provided symbols")
            return "\n".join(report)
        
        # Compare methods
        report.append(f"\n📊 COMPARISON OF ALLOCATION METHODS:")
        
        for method, result in reports.items():
            report.append(f"\n{method.upper().replace('_', ' ')} ALLOCATION:")
            for symbol, weight in result['allocation'].items():
                report.append(f"  {symbol}: {weight:.2%}")
            
            metrics = result['metrics']
            report.append(f"  Expected Return: {metrics['return']:.2%}")
            report.append(f"  Risk (Volatility): {metrics['volatility']:.2%}")
            report.append(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
        
        # Identify the best approach based on Sharpe ratio
        best_method = max(reports.keys(), key=lambda x: reports[x]['metrics']['sharpe_ratio'])
        best_metrics = reports[best_method]['metrics']
        
        report.append(f"\n🎯 RECOMMENDED APPROACH: {best_method.upper().replace('_', ' ')}")
        report.append(f"   This method provides the highest Sharpe Ratio: {best_metrics['sharpe_ratio']:.3f}")
        report.append(f"   Expected Annual Return: {best_metrics['return']:.2%}")
        report.append(f"   Expected Risk: {best_metrics['volatility']:.2%}")
        
        # Allocation for the recommended portfolio
        report.append(f"\n📋 RECOMMENDED ALLOCATION:")
        for symbol, weight in reports[best_method]['allocation'].items():
            report.append(f"  {symbol}: {weight:.2%}")
        
        # Risk considerations
        report.append(f"\n⚠️ RISK CONSIDERATIONS:")
        report.append(f"  - Maximum potential drawdown: {best_metrics['max_drawdown']:.2%}")
        report.append(f"  - Value at Risk (95% confidence): {best_metrics['var_95']:.2%}")
        report.append(f"  - This analysis is based on historical data and may not predict future performance")
        
        return "\n".join(report)


def analyze_asset(symbol: str, asset_type: str = 'stock', period: str = "6mo", interval: str = "1d"):
    """
    Module-level function to analyze an asset (stock or crypto).
    Creates a MarketAnalyzer instance and calls its analyze_asset method.
    """
    analyzer = MarketAnalyzer()
    if asset_type.lower() == 'crypto':
        data = analyzer.watchlist.get_crypto_data(symbol, "USD", period, interval)
    else:
        data = analyzer.watchlist.get_stock_data(symbol, period, interval)
    
    if data is not None and not data.empty:
        return analyzer.analyze_asset(symbol, data, asset_type)
    else:
        # Return a default analysis if no data is available
        return {
            'symbol': symbol,
            'asset_type': asset_type,
            'current_price': 0,
            'indicators': {},
            'patterns': [],
            'signals': [],
            'risk_metrics': {},
            'market_metrics': {},
            'company_name': 'Unknown' if asset_type == 'stock' else 'N/A'
        }


def analyze_stock(symbol: str, period: str = "6mo", interval: str = "1d"):
    """
    Module-level function to analyze a stock.
    Creates a MarketAnalyzer instance and calls its analyze_asset method.
    """
    return analyze_asset(symbol, 'stock', period, interval)


def get_options_data(symbol: str, expiration: str = None):
    """
    Module-level function to get options data for a symbol
    """
    # Check if yfinance is available
    if not YFINANCE_AVAILABLE:
        print("yfinance not available, returning empty options data")
        return {
            'symbol': symbol,
            'expiration_dates': [],
            'calls': [],
            'puts': [],
            'current_price': 0,
            'error': 'yfinance not available'
        }
    
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        
        # Get available expiration dates
        expiration_dates = ticker.options
        
        if not expiration_dates:
            return {
                'symbol': symbol,
                'expiration_dates': [],
                'calls': [],
                'puts': [],
                'current_price': 0,
                'error': 'No options data available for this symbol'
            }
        
        # Use specified expiration or the first available one
        if expiration is None:
            expiration = expiration_dates[0] if expiration_dates else None
        elif expiration not in expiration_dates:
            # If requested expiration not available, use the first one
            expiration = expiration_dates[0] if expiration_dates else None
        
        if expiration:
            # Get options data for the specified expiration
            opt = ticker.option_chain(expiration)
            
            # Process calls
            calls_list = []
            if not opt.calls.empty:
                for idx, row in opt.calls.iterrows():
                    calls_list.append({
                        'strike': row.get('strike', 0),
                        'last': row.get('lastPrice', 0),
                        'bid': row.get('bid', 0), 
                        'ask': row.get('ask', 0),
                        'volume': row.get('volume', 0),
                        'open_interest': row.get('openInterest', 0),
                        'iv': row.get('impliedVolatility', 0),
                        'delta': row.get('delta', 0),
                        'gamma': row.get('gamma', 0),
                        'theta': row.get('theta', 0),
                        'vega': row.get('vega', 0)
                    })
            
            # Process puts
            puts_list = []
            if not opt.puts.empty:
                for idx, row in opt.puts.iterrows():
                    puts_list.append({
                        'strike': row.get('strike', 0),
                        'last': row.get('lastPrice', 0),
                        'bid': row.get('bid', 0), 
                        'ask': row.get('ask', 0),
                        'volume': row.get('volume', 0),
                        'open_interest': row.get('openInterest', 0),
                        'iv': row.get('impliedVolatility', 0),
                        'delta': row.get('delta', 0),
                        'gamma': row.get('gamma', 0),
                        'theta': row.get('theta', 0),
                        'vega': row.get('vega', 0)
                    })
            
            # Get current stock price
            hist = ticker.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            return {
                'symbol': symbol,
                'expiration_dates': list(expiration_dates),
                'selected_expiration': expiration,
                'calls': calls_list,
                'puts': puts_list,
                'current_price': current_price
            }
        else:
            return {
                'symbol': symbol,
                'expiration_dates': [],
                'calls': [],
                'puts': [],
                'current_price': 0,
                'error': 'No expiration dates available'
            }
            
    except Exception as e:
        print(f"Error fetching options data for {symbol}: {e}")
        return {
            'symbol': symbol,
            'expiration_dates': [],
            'calls': [],
            'puts': [],
            'current_price': 0,
            'error': str(e)
        }


def get_options_strategies(symbol: str):
    """
    Module-level function to get suggested options strategies
    """
    options_analyzer = OptionsAnalyzer()
    return options_analyzer.find_options_strategies(symbol)


def analyze_portfolio_risk(symbols: list, weights: list, account_size: float = 100000):
    """
    Analyze portfolio risk metrics for multiple symbols
    """
    analyzer = AdvancedAnalyzer()
    
    # Get data for each symbol
    symbols_data = {}
    for symbol in symbols:
        data = analyze_stock(symbol)
        if data and 'current_price' in data:
            symbols_data[symbol] = data
    
    # Calculate correlation between symbols
    correlation_analysis = analyzer.analyze_correlation(symbols_data)
    
    # Calculate individual metrics and combined portfolio metrics
    individual_metrics = {}
    for symbol, data in symbols_data.items():
        # Placeholder for individual metrics
        individual_metrics[symbol] = {
            'current_price': data.get('current_price', 0),
            'rsi': data.get('indicators', {}).get('rsi', 50),
            'volatility': data.get('risk_metrics', {}).get('volatility', 0.2)
        }
    
    return {
        'individual_metrics': individual_metrics,
        'correlation_analysis': correlation_analysis,
        'account_size': account_size,
        'symbols': symbols,
        'weights': weights
    }


def calculate_position_size(account_size: float, risk_percentage: float, stop_loss_pct: float, current_price: float):
    """
    Calculate optimal position size based on risk management
    """
    analyzer = AdvancedAnalyzer()
    
    # Calculate stop loss distance in dollars
    stop_loss_distance = current_price * stop_loss_pct
    
    return analyzer.calculate_position_size(account_size, risk_percentage, stop_loss_distance)


# Since the code mentions OptionsAnalyzer and AdvancedAnalyzer but they are not defined in the 
# current file, I need to add these classes to complete the functionality

class OptionsAnalyzer:
    """Options analysis functionality"""
    
    def __init__(self):
        # In a real implementation, this would connect to options data providers
        pass
    
    def get_options_chain(self, symbol: str, expiration_date: str = None) -> dict:
        """
        Get options chain for a symbol
        In a real implementation, this would fetch from a data provider
        """
        # Simulated options chain data for demonstration
        import random
        from datetime import datetime, timedelta
        
        # Generate simulated options data
        current_price = 150.0  # This would come from real price data
        
        # Create mock expiration dates
        if not expiration_date:
            # Use the next 3 Fridays
            today = datetime.today()
            days_ahead = 4 - today.weekday()  # 4 is Friday
            if days_ahead <= 0:
                days_ahead += 7
            exp_date = today + timedelta(days=days_ahead)
            expiration_date = exp_date.strftime('%Y-%m-%d')
        
        strikes = [round(current_price + i * 5 - 25, 2) for i in range(11)]  # 11 strikes around current price
        
        calls = []
        puts = []
        
        for strike in strikes:
            # Simulate option prices based on moneyness
            call_iv = max(0.15, 0.30 - abs(current_price - strike) / current_price * 0.5)
            put_iv = max(0.15, 0.30 - abs(current_price - strike) / current_price * 0.5)
            
            call_price = max(0.10, (current_price - strike) * 0.6 + random.uniform(0.5, 2.0))
            put_price = max(0.10, (strike - current_price) * 0.6 + random.uniform(0.5, 2.0))
            
            if call_price < 0: call_price = random.uniform(0.10, 2.0)
            if put_price < 0: put_price = random.uniform(0.10, 2.0)
            
            calls.append({
                'strike': strike,
                'bid': round(call_price - 0.05, 2),
                'ask': round(call_price + 0.05, 2),
                'last': call_price,
                'volume': random.randint(10, 1000),
                'open_interest': random.randint(100, 5000),
                'iv': round(call_iv, 4),
                'delta': round(min(0.95, max(0.05, (current_price - strike + 25) / 50)), 3),
                'gamma': round(random.uniform(0.01, 0.1), 4),
                'theta': round(-random.uniform(0.01, 0.05), 4),
                'vega': round(random.uniform(0.1, 0.3), 4)
            })
            
            puts.append({
                'strike': strike,
                'bid': round(put_price - 0.05, 2),
                'ask': round(put_price + 0.05, 2),
                'last': put_price,
                'volume': random.randint(10, 1000),
                'open_interest': random.randint(100, 5000),
                'iv': round(put_iv, 4),
                'delta': round(max(-0.95, min(-0.05, (strike - current_price - 25) / 50)), 3),
                'gamma': round(random.uniform(0.01, 0.1), 4),
                'theta': round(-random.uniform(0.01, 0.05), 4),
                'vega': round(random.uniform(0.1, 0.3), 4)
            })
        
        return {
            'symbol': symbol,
            'expiration_date': expiration_date,
            'current_price': current_price,
            'calls': calls,
            'puts': puts,
            'timestamp': datetime.now()
        }
    
    def analyze_options_greeks(self, option_data: dict) -> dict:
        """
        Analyze options Greeks for a given option
        This is a simplified model for demonstration
        """
        # In a real system, this would calculate actual Greeks
        # For simulation purposes:
        greeks = {
            'delta': option_data.get('delta', 0),
            'gamma': option_data.get('gamma', 0),
            'theta': option_data.get('theta', 0),
            'vega': option_data.get('vega', 0),
            'rho': round(random.uniform(-0.01, 0.02), 4)  # Placeholder
        }
        
        return greeks
    
    def find_options_strategies(self, symbol: str) -> list:
        """
        Suggest options strategies based on market conditions
        """
        # Get current market data
        stock_analysis = analyze_stock(symbol)
        current_price = stock_analysis.get('current_price', 0)
        rsi = stock_analysis.get('indicators', {}).get('rsi', 50)
        volatility = stock_analysis.get('risk_metrics', {}).get('volatility', 0.3)
        
        strategies = []
        
        # Suggest strategies based on RSI and volatility
        if rsi < 30 and volatility > 0.3:  # Oversold high volatility
            strategies.append({
                'strategy': 'Long Straddle',
                'description': 'Bet on high volatility with uncertain direction',
                'risk': 'Limited to premium paid',
                'target': 'Large price movement in either direction'
            })
            strategies.append({
                'strategy': 'Long Call',
                'description': 'Bullish strategy when expecting price increase',
                'risk': 'Limited to premium paid',
                'target': f'Price needs to rise above strike + premium ({current_price + 2:.2f})'
            })
        elif rsi > 70 and volatility > 0.3:  # Overbought high volatility
            strategies.append({
                'strategy': 'Long Strangle',
                'description': 'Bet on high volatility with defined risk',
                'risk': 'Limited to premium paid',
                'target': 'Large price movement in either direction'
            })
            strategies.append({
                'strategy': 'Long Put',
                'description': 'Bearish strategy when expecting price decrease',
                'risk': 'Limited to premium paid',
                'target': f'Price needs to fall below strike - premium ({current_price - 2:.2f})'
            })
        elif rsi < 30:  # Oversold, low volatility
            strategies.append({
                'strategy': 'Bull Call Spread',
                'description': 'Moderately bullish with limited risk',
                'risk': 'Limited to spread cost',
                'target': 'Price increase with defined risk'
            })
            strategies.append({
                'strategy': 'Selling Put Spreads',
                'description': 'Bullish strategy with income generation',
                'risk': 'Limited to spread width',
                'target': 'Price stays above short strike'
            })
        elif rsi > 70:  # Overbought, low volatility
            strategies.append({
                'strategy': 'Bear Put Spread',
                'description': 'Moderately bearish with limited risk',
                'risk': 'Limited to spread cost',
                'target': 'Price decrease with defined risk'
            })
            strategies.append({
                'strategy': 'Selling Call Spreads',
                'description': 'Bearish strategy with income generation',
                'risk': 'Limited to spread width',
                'target': 'Price stays below short strike'
            })
        elif volatility > 0.4:  # High volatility neutral
            strategies.append({
                'strategy': 'Iron Condor',
                'description': 'Neutral strategy for high volatility',
                'risk': 'Defined risk between short strikes',
                'target': 'Price staying within defined range'
            })
            strategies.append({
                'strategy': 'Short Strangle',
                'description': 'Neutral strategy with income generation',
                'risk': 'Undefined on one side',
                'target': 'Price staying between strikes'
            })
        else:  # Normal conditions
            strategies.append({
                'strategy': 'Iron Condor',
                'description': 'Neutral strategy for sideways market',
                'risk': 'Defined risk between short strikes',
                'target': 'Price staying within defined range'
            })
            strategies.append({
                'strategy': 'Long Butterfly',
                'description': 'Neutral strategy for low volatility expectation',
                'risk': 'Limited to premium paid',
                'target': 'Price consolidation near center strike'
            })
        
        return strategies


class AdvancedAnalyzer:
    """Advanced AI-powered market analysis"""
    
    def __init__(self):
        # For a more sophisticated analysis, we'd load ML models here
        # For now, we'll implement enhanced algorithmic analysis
        self.risk_tolerance = 0.1  # Default risk tolerance (10%)
        self.real_time_stream = RealTimeDataStream()
    
    def calculate_portfolio_metrics(self, stock_data: dict) -> dict:
        """
        Calculate advanced portfolio metrics
        """
        if 'returns' in stock_data:
            returns = stock_data['returns']
            
            # Calculate performance metrics
            cumulative_return = (1 + returns).prod() - 1
            volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            sharpe_ratio = returns.mean() / returns.std() * (252 ** 0.5) if returns.std() != 0 else 0
            
            # Calculate maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Calculate Value at Risk (VaR)
            var_95 = returns.quantile(0.05)
            
            return {
                'cumulative_return': cumulative_return,
                'annualized_volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95': var_95,
                'win_rate': (returns > 0).sum() / len(returns)
            }
    
    def generate_ai_signals(self, data: pd.DataFrame) -> list:
        """
        Generate AI-powered trading signals using multiple indicators
        """
        signals = []
        close_prices = data['Close']
        
        # Calculate additional technical indicators
        # Moving Average Convergence Divergence (MACD)
        exp12 = close_prices.ewm(span=12).mean()
        exp26 = close_prices.ewm(span=26).mean()
        macd = exp12 - exp26
        signal_line = macd.ewm(span=9).mean()
        macd_histogram = macd - signal_line
        
        # Relative Strength Index (RSI)
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        sma20 = close_prices.rolling(window=20).mean()
        std20 = close_prices.rolling(window=20).std()
        bb_upper = sma20 + (std20 * 2)
        bb_lower = sma20 - (std20 * 2)
        
        # Stochastic Oscillator
        low_14 = data['Low'].rolling(window=14).min()
        high_14 = data['High'].rolling(window=14).max()
        k_percent = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
        d_percent = k_percent.rolling(window=3).mean()
        
        # Generate signals based on multiple confirmations
        current_price = close_prices.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_k = k_percent.iloc[-1]
        current_d = d_percent.iloc[-1]
        
        # Multiple confirmation buy signals
        buy_signals = 0
        sell_signals = 0
        
        # RSI conditions
        if current_rsi < 30:  # Oversold
            buy_signals += 1
            signals.append("RSI: POTENTIALLY OVERSOLD")
        elif current_rsi > 70:  # Overbought
            sell_signals += 1
            signals.append("RSI: POTENTIALLY OVERBOUGHT")
        
        # MACD conditions
        if current_macd > current_signal:  # Bullish crossover
            buy_signals += 1
            signals.append("MACD: BULLISH CROSSOVER")
        else:
            sell_signals += 1
            signals.append("MACD: BEARISH CROSSOVER")
        
        # Bollinger Bands conditions
        if current_price < bb_lower.iloc[-1]:  # Price below lower band
            buy_signals += 1
            signals.append("BOLLINGER: PRICE BELOW LOWER BAND")
        elif current_price > bb_upper.iloc[-1]:  # Price above upper band
            sell_signals += 1
            signals.append("BOLLINGER: PRICE ABOVE UPPER BAND")
        
        # Stochastic conditions
        if current_k < 20 and current_d < 20 and current_k > current_d:  # Oversold bullish
            buy_signals += 1
            signals.append("STOCHASTIC: BULLISH CROSS IN OVERSOLD")
        elif current_k > 80 and current_d > 80 and current_k < current_d:  # Overbought bearish
            sell_signals += 1
            signals.append("STOCHASTIC: BEARISH CROSS IN OVERBOUGHT")
        
        # Overall signal
        if buy_signals > sell_signals:
            signals.append(f"AI RECOMMENDATION: BUY SIGNAL ({buy_signals} positive indicators)")
        elif sell_signals > buy_signals:
            signals.append(f"AI RECOMMENDATION: SELL SIGNAL ({sell_signals} negative indicators)")
        else:
            signals.append("AI RECOMMENDATION: HOLD (Mixed signals)")
        
        return signals
    
    def calculate_position_size(self, account_size: float, risk_percentage: float, stop_loss_distance: float) -> dict:
        """
        Calculate position size based on risk management principles
        """
        risk_amount = account_size * risk_percentage
        
        if stop_loss_distance > 0:
            num_shares = risk_amount / stop_loss_distance
            position_value = num_shares * (account_size / 10)  # Using a proxy for current price
        else:
            num_shares = 0
            position_value = 0
        
        return {
            'account_size': account_size,
            'risk_percentage': risk_percentage,
            'risk_amount': risk_amount,
            'stop_loss_distance': stop_loss_distance,
            'position_size_shares': round(num_shares, 2),
            'position_value': position_value
        }
    
    def analyze_correlation(self, symbols_data: dict) -> dict:
        """
        Analyze correlation between different stocks
        """
        if len(symbols_data) < 2:
            return {'error': 'Need at least 2 symbols for correlation analysis'}
        
        # Create a combined DataFrame
        df_combined = pd.DataFrame()
        for symbol, data in symbols_data.items():
            if 'Close' in data:
                df_combined[f'{symbol}_Close'] = data['Close']
        
        if df_combined.empty:
            return {'error': 'No valid data for correlation analysis'}
        
        correlation_matrix = df_combined.corr()
        
        # Identify highly correlated pairs
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # High correlation threshold
                    high_corr_pairs.append({
                        'pair': f"{correlation_matrix.columns[i]} vs {correlation_matrix.columns[j]}",
                        'correlation': corr_value
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'high_correlation_pairs': high_corr_pairs
        }