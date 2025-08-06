"""
Data processing and analysis utilities
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
from loguru import logger

from .models import StockData, HistoricalData, HistoricalDataPoint
from ..utils.helpers import clean_numeric_value

class DataProcessor:
    """
    Process and analyze financial data
    """
    
    def __init__(self):
        """Initialize data processor"""
        self.cache = {}
        logger.info("Data processor initialized")
    
    def get_historical_data(self, symbol: str, period: str = "1y", 
                          interval: str = "1d") -> Optional[HistoricalData]:
        """
        Fetch historical stock data using yfinance
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            HistoricalData object or None if failed
        """
        try:
            logger.info(f"Fetching historical data for {symbol} (period: {period}, interval: {interval})")
            
            # Create yfinance ticker
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            hist_data = ticker.history(period=period, interval=interval)
            
            if hist_data.empty:
                logger.warning(f"No historical data found for {symbol}")
                return None
            
            # Convert to our data model
            data_points = []
            for date, row in hist_data.iterrows():
                data_point = HistoricalDataPoint(
                    date=date.to_pydatetime(),
                    open=float(row['Open']) if pd.notna(row['Open']) else None,
                    high=float(row['High']) if pd.notna(row['High']) else None,
                    low=float(row['Low']) if pd.notna(row['Low']) else None,
                    close=float(row['Close']) if pd.notna(row['Close']) else None,
                    adj_close=float(row['Adj Close']) if pd.notna(row['Adj Close']) else None,
                    volume=int(row['Volume']) if pd.notna(row['Volume']) else None
                )
                data_points.append(data_point)
            
            historical_data = HistoricalData(
                symbol=symbol,
                data_points=data_points,
                period=period,
                interval=interval
            )
            
            logger.success(f"Successfully fetched {len(data_points)} historical data points for {symbol}")
            return historical_data
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {symbol}: {str(e)}")
            return None
    
    def calculate_technical_indicators(self, historical_data: HistoricalData) -> Dict[str, Any]:
        """
        Calculate technical indicators from historical data
        
        Args:
            historical_data: Historical stock data
            
        Returns:
            Dictionary with technical indicators
        """
        try:
            if not historical_data.data_points:
                return {}
            
            # Convert to pandas DataFrame for easier calculation
            df = self._to_dataframe(historical_data)
            
            indicators = {}
            
            # Simple Moving Averages
            indicators['sma_20'] = df['close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else None
            indicators['sma_50'] = df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else None
            indicators['sma_200'] = df['close'].rolling(window=200).mean().iloc[-1] if len(df) >= 200 else None
            
            # Exponential Moving Averages
            indicators['ema_12'] = df['close'].ewm(span=12).mean().iloc[-1] if len(df) >= 12 else None
            indicators['ema_26'] = df['close'].ewm(span=26).mean().iloc[-1] if len(df) >= 26 else None
            
            # MACD
            if indicators['ema_12'] and indicators['ema_26']:
                ema_12_series = df['close'].ewm(span=12).mean()
                ema_26_series = df['close'].ewm(span=26).mean()
                macd_line = ema_12_series - ema_26_series
                signal_line = macd_line.ewm(span=9).mean()
                
                indicators['macd'] = macd_line.iloc[-1]
                indicators['macd_signal'] = signal_line.iloc[-1]
                indicators['macd_histogram'] = (macd_line - signal_line).iloc[-1]
            
            # RSI (Relative Strength Index)
            indicators['rsi'] = self._calculate_rsi(df['close'])
            
            # Bollinger Bands
            bb_data = self._calculate_bollinger_bands(df['close'])
            indicators.update(bb_data)
            
            # Volume indicators
            indicators['avg_volume_20'] = df['volume'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else None
            indicators['volume_ratio'] = (df['volume'].iloc[-1] / indicators['avg_volume_20']) if indicators['avg_volume_20'] else None
            
            # Price performance
            indicators['price_change_1d'] = self._calculate_price_change(df, 1)
            indicators['price_change_5d'] = self._calculate_price_change(df, 5)
            indicators['price_change_20d'] = self._calculate_price_change(df, 20)
            
            # Volatility
            indicators['volatility_20d'] = df['close'].pct_change().rolling(window=20).std().iloc[-1] * np.sqrt(252) if len(df) >= 20 else None
            
            logger.success(f"Calculated technical indicators for {historical_data.symbol}")
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to calculate technical indicators: {str(e)}")
            return {}
    
    def analyze_price_patterns(self, historical_data: HistoricalData) -> Dict[str, Any]:
        """
        Analyze price patterns and trends
        
        Args:
            historical_data: Historical stock data
            
        Returns:
            Dictionary with pattern analysis
        """
        try:
            if not historical_data.data_points or len(historical_data.data_points) < 10:
                return {"error": "Insufficient data for pattern analysis"}
            
            df = self._to_dataframe(historical_data)
            
            patterns = {}
            
            # Trend analysis
            patterns['trend'] = self._analyze_trend(df)
            
            # Support and resistance levels
            patterns['support_resistance'] = self._find_support_resistance(df)
            
            # Price gaps
            patterns['gaps'] = self._find_price_gaps(df)
            
            # Candlestick patterns (basic)
            patterns['candlestick_patterns'] = self._identify_candlestick_patterns(df)
            
            # Chart patterns
            patterns['chart_patterns'] = self._identify_chart_patterns(df)
            
            logger.success(f"Analyzed price patterns for {historical_data.symbol}")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze price patterns: {str(e)}")
            return {"error": str(e)}
    
    def _to_dataframe(self, historical_data: HistoricalData) -> pd.DataFrame:
        """Convert HistoricalData to pandas DataFrame"""
        data = []
        for point in historical_data.data_points:
            data.append({
                'date': point.date,
                'open': point.open,
                'high': point.high,
                'low': point.low,
                'close': point.close,
                'adj_close': point.adj_close,
                'volume': point.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        return df.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return None
            
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1])
            
        except Exception:
            return None
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                return {}
            
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                'bb_upper': float(upper_band.iloc[-1]),
                'bb_middle': float(sma.iloc[-1]),
                'bb_lower': float(lower_band.iloc[-1]),
                'bb_width': float((upper_band - lower_band).iloc[-1])
            }
            
        except Exception:
            return {}
    
    def _calculate_price_change(self, df: pd.DataFrame, days: int) -> Optional[float]:
        """Calculate price change over specified days"""
        try:
            if len(df) < days + 1:
                return None
            
            current_price = df['close'].iloc[-1]
            past_price = df['close'].iloc[-(days + 1)]
            
            return ((current_price - past_price) / past_price) * 100
            
        except Exception:
            return None
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price trend"""
        try:
            # Simple trend analysis using linear regression
            prices = df['close'].values
            x = np.arange(len(prices))
            
            # Calculate slope
            slope = np.polyfit(x, prices, 1)[0]
            
            # Determine trend direction
            if slope > 0.1:
                trend_direction = "bullish"
            elif slope < -0.1:
                trend_direction = "bearish"
            else:
                trend_direction = "sideways"
            
            # Calculate trend strength
            correlation = np.corrcoef(x, prices)[0, 1]
            trend_strength = abs(correlation)
            
            return {
                "direction": trend_direction,
                "strength": trend_strength,
                "slope": slope
            }
            
        except Exception:
            return {"direction": "unknown", "strength": 0, "slope": 0}
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Find support and resistance levels"""
        try:
            highs = df['high'].values
            lows = df['low'].values
            
            # Simple approach: find local maxima and minima
            resistance_levels = []
            support_levels = []
            
            # Find peaks and troughs
            for i in range(1, len(highs) - 1):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    resistance_levels.append(highs[i])
                
                if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                    support_levels.append(lows[i])
            
            # Keep only significant levels
            resistance_levels = sorted(set(resistance_levels), reverse=True)[:5]
            support_levels = sorted(set(support_levels))[:5]
            
            return {
                "resistance": resistance_levels,
                "support": support_levels
            }
            
        except Exception:
            return {"resistance": [], "support": []}
    
    def _find_price_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find price gaps"""
        try:
            gaps = []
            
            for i in range(1, len(df)):
                prev_high = df['high'].iloc[i-1]
                prev_low = df['low'].iloc[i-1]
                curr_high = df['high'].iloc[i]
                curr_low = df['low'].iloc[i]
                
                # Gap up
                if curr_low > prev_high:
                    gaps.append({
                        "type": "gap_up",
                        "date": df.index[i],
                        "gap_size": curr_low - prev_high,
                        "gap_percentage": ((curr_low - prev_high) / prev_high) * 100
                    })
                
                # Gap down
                elif curr_high < prev_low:
                    gaps.append({
                        "type": "gap_down",
                        "date": df.index[i],
                        "gap_size": prev_low - curr_high,
                        "gap_percentage": ((prev_low - curr_high) / prev_low) * 100
                    })
            
            return gaps[-10:]  # Return last 10 gaps
            
        except Exception:
            return []
    
    def _identify_candlestick_patterns(self, df: pd.DataFrame) -> List[str]:
        """Identify basic candlestick patterns"""
        try:
            patterns = []
            
            if len(df) < 3:
                return patterns
            
            # Get last few candles
            last_3 = df.tail(3)
            
            for i, (date, candle) in enumerate(last_3.iterrows()):
                open_price = candle['open']
                close_price = candle['close']
                high_price = candle['high']
                low_price = candle['low']
                
                body_size = abs(close_price - open_price)
                candle_range = high_price - low_price
                
                # Doji
                if body_size < (candle_range * 0.1):
                    patterns.append("doji")
                
                # Hammer/Hanging Man
                elif body_size < (candle_range * 0.3):
                    if close_price > open_price:
                        patterns.append("hammer")
                    else:
                        patterns.append("hanging_man")
            
            return list(set(patterns))
            
        except Exception:
            return []
    
    def _identify_chart_patterns(self, df: pd.DataFrame) -> List[str]:
        """Identify basic chart patterns"""
        try:
            patterns = []
            
            if len(df) < 20:
                return patterns
            
            # Simple pattern recognition
            recent_data = df.tail(20)
            highs = recent_data['high']
            lows = recent_data['low']
            
            # Double top/bottom (simplified)
            high_peaks = highs.nlargest(3)
            low_troughs = lows.nsmallest(3)
            
            if len(high_peaks) >= 2:
                if abs(high_peaks.iloc[0] - high_peaks.iloc[1]) < (high_peaks.iloc[0] * 0.02):
                    patterns.append("double_top")
            
            if len(low_troughs) >= 2:
                if abs(low_troughs.iloc[0] - low_troughs.iloc[1]) < (low_troughs.iloc[0] * 0.02):
                    patterns.append("double_bottom")
            
            return patterns
            
        except Exception:
            return []
