"""
Market Data Integration Module

Integrates with multiple real-time market data APIs:
- CoinGecko (Cryptocurrency)
- Alpha Vantage (Stocks)
- OANDA (Forex)
"""

import requests
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """Handles real-time market data from multiple sources."""

    def __init__(self):
        """Initialize market data provider with API keys."""
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.oanda_key = os.getenv("OANDA_API_KEY", "")
        self.oanda_base = "https://api.oanda.com/v3"

    def get_crypto_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch cryptocurrency data from CoinGecko (free API).
        
        Args:
            symbol: Crypto symbol (e.g., 'bitcoin', 'ethereum')
        
        Returns:
            Market data dictionary
        """
        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'XRP': 'ripple',
                'ADA': 'cardano',
                'SOL': 'solana',
                'DOT': 'polkadot',
                'DOGE': 'dogecoin',
                'USDT': 'tether',
                'USDC': 'usd-coin',
                'BNB': 'binancecoin'
            }
            
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if coin_id in data:
                market_data = data[coin_id]
                return {
                    'symbol': symbol.upper(),
                    'price': market_data.get('usd'),
                    'market_cap': market_data.get('usd_market_cap'),
                    'volume_24h': market_data.get('usd_24h_vol'),
                    'change_24h': market_data.get('usd_24h_change'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'CoinGecko'
                }
            return None
            
        except requests.RequestException as e:
            logger.error(f"CoinGecko API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching crypto data: {e}")
            return None

    def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch stock data from Alpha Vantage.
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'GOOGL')
        
        Returns:
            Market data dictionary
        """
        if not self.alpha_vantage_key:
            logger.warning("Alpha Vantage API key not configured")
            return None
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol.upper(),
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.alpha_vantage_base, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'Global Quote' in data and data['Global Quote']:
                quote = data['Global Quote']
                return {
                    'symbol': symbol.upper(),
                    'price': float(quote.get('05. price', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': quote.get('10. change percent', '0%'),
                    'volume': int(quote.get('06. volume', 0)),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Alpha Vantage'
                }
            return None
            
        except requests.RequestException as e:
            logger.error(f"Alpha Vantage API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            return None

    def get_forex_data(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Fetch forex data from OANDA.
        
        Args:
            pair: Currency pair (e.g., 'EUR_USD')
        
        Returns:
            Market data dictionary
        """
        if not self.oanda_key:
            logger.warning("OANDA API key not configured")
            return None
        
        try:
            # Normalize pair format
            pair = pair.replace('/', '_').upper()
            
            url = f"{self.oanda_base}/instruments/{pair}/candles"
            headers = {
                'Authorization': f'Bearer {self.oanda_key}',
                'Content-Type': 'application/json'
            }
            params = {
                'granularity': 'H1',
                'count': 1
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'candles' in data and data['candles']:
                candle = data['candles'][0]
                return {
                    'symbol': pair,
                    'open': float(candle['mid']['o']),
                    'high': float(candle['mid']['h']),
                    'low': float(candle['mid']['l']),
                    'close': float(candle['mid']['c']),
                    'timestamp': candle['time'],
                    'source': 'OANDA'
                }
            return None
            
        except requests.RequestException as e:
            logger.error(f"OANDA API error for {pair}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching forex data: {e}")
            return None

    def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Intelligently fetch market data based on symbol type.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Market data dictionary
        """
        # Try to determine symbol type and fetch accordingly
        if '/' in symbol or '_' in symbol:
            return self.get_forex_data(symbol)
        elif symbol.upper() in ['BTC', 'ETH', 'XRP', 'ADA', 'SOL', 'DOT', 'DOGE', 'USDT', 'USDC', 'BNB']:
            return self.get_crypto_data(symbol)
        else:
            return self.get_stock_data(symbol)


class TechnicalIndicators:
    """Calculate technical indicators for trading analysis."""

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of price data
            period: RSI period (default 14)
        
        Returns:
            RSI value (0-100)
        """
        if len(prices) < period + 1:
            return 0.0
        
        try:
            deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
            gains = [delta if delta > 0 else 0 for delta in deltas]
            losses = [-delta if delta < 0 else 0 for delta in deltas]
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100.0 if avg_gain > 0 else 0.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi, 2)
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 0.0

    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: List of price data
        
        Returns:
            MACD values (macd, signal, histogram)
        """
        if len(prices) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        try:
            ema_12 = TechnicalIndicators._calculate_ema(prices, 12)
            ema_26 = TechnicalIndicators._calculate_ema(prices, 26)
            
            macd_line = ema_12 - ema_26
            signal_line = TechnicalIndicators._calculate_ema([macd_line], 9)
            histogram = macd_line - signal_line
            
            return {
                'macd': round(macd_line, 4),
                'signal': round(signal_line, 4),
                'histogram': round(histogram, 4)
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {'macd': 0, 'signal': 0, 'histogram': 0}

    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of price data
            period: Moving average period
            std_dev: Standard deviations
        
        Returns:
            Bollinger Bands values (upper, middle, lower)
        """
        if len(prices) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0}
        
        try:
            sma = sum(prices[-period:]) / period
            variance = sum((x - sma) ** 2 for x in prices[-period:]) / period
            std = variance ** 0.5
            
            return {
                'upper': round(sma + (std * std_dev), 4),
                'middle': round(sma, 4),
                'lower': round(sma - (std * std_dev), 4)
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {'upper': 0, 'middle': 0, 'lower': 0}

    @staticmethod
    def calculate_moving_averages(prices: List[float]) -> Dict[str, float]:
        """
        Calculate multiple moving averages.
        
        Args:
            prices: List of price data
        
        Returns:
            Moving averages (MA20, MA50, MA200)
        """
        try:
            ma20 = sum(prices[-20:]) / min(20, len(prices)) if len(prices) >= 20 else 0
            ma50 = sum(prices[-50:]) / min(50, len(prices)) if len(prices) >= 50 else 0
            ma200 = sum(prices[-200:]) / min(200, len(prices)) if len(prices) >= 200 else 0
            
            return {
                'ma20': round(ma20, 4),
                'ma50': round(ma50, 4),
                'ma200': round(ma200, 4)
            }
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return {'ma20': 0, 'ma50': 0, 'ma200': 0}

    @staticmethod
    def _calculate_ema(prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) == 0:
            return 0.0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:min(period, len(prices))]) / min(period, len(prices))
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema

    @staticmethod
    def analyze_indicators(indicators: Dict[str, Any]) -> str:
        """
        Generate analysis based on indicators.
        
        Args:
            indicators: Dictionary of calculated indicators
        
        Returns:
            Analysis text
        """
        analysis = []
        
        # RSI Analysis
        rsi = indicators.get('rsi', 0)
        if rsi > 70:
            analysis.append("📈 RSI indicates overbought conditions (>70)")
        elif rsi < 30:
            analysis.append("📉 RSI indicates oversold conditions (<30)")
        else:
            analysis.append(f"📊 RSI at {rsi} - Neutral")
        
        # MACD Analysis
        macd = indicators.get('macd', {})
        if macd.get('macd', 0) > macd.get('signal', 0):
            analysis.append("✅ MACD: Bullish crossover signal")
        elif macd.get('macd', 0) < macd.get('signal', 0):
            analysis.append("❌ MACD: Bearish crossover signal")
        
        # Bollinger Bands Analysis
        bb = indicators.get('bollinger_bands', {})
        current_price = indicators.get('current_price', 0)
        if current_price:
            if current_price > bb.get('upper', 0):
                analysis.append("⚠️ Price above Bollinger upper band - Potential pullback")
            elif current_price < bb.get('lower', 0):
                analysis.append("⚠️ Price below Bollinger lower band - Potential bounce")
        
        # Moving Averages Analysis
        ma = indicators.get('moving_averages', {})
        if current_price and ma.get('ma20'):
            if current_price > ma.get('ma20') > ma.get('ma50') > ma.get('ma200'):
                analysis.append("🚀 Uptrend: Price above all major moving averages")
            elif current_price < ma.get('ma20') < ma.get('ma50') < ma.get('ma200'):
                analysis.append("📉 Downtrend: Price below all major moving averages")
        
        return "\n".join(analysis) if analysis else "Unable to generate analysis"
