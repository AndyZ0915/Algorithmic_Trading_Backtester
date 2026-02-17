"""
Data fetcher with demo data fallback - PRODUCTION VERSION
Handles Yahoo Finance with graceful degradation to simulated data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List
import logging

import config
from .database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches stock data with automatic fallback to demo data"""
    
    def __init__(self, cache_enabled: bool = True, force_demo: bool = False):
        """
        Initialize data fetcher.
        
        Args:
            cache_enabled: Enable SQLite caching
            force_demo: Force use of demo data (skip Yahoo Finance)
        """
        self.cache_enabled = cache_enabled
        self.force_demo = force_demo
        self.db_manager = DatabaseManager() if cache_enabled else None
    
    def fetch_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Fetch historical data with automatic fallback.
        
        Args:
            symbol: Stock ticker
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            force_refresh: Skip cache
            
        Returns:
            DataFrame with OHLCV data
        """
        start_date = start_date or config.DEFAULT_START_DATE
        end_date = end_date or config.DEFAULT_END_DATE
        
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        # Check cache
        if self.cache_enabled and not force_refresh:
            cached = self._get_from_cache(symbol, start_date, end_date)
            if cached is not None:
                logger.info(f"✅ Using cached data for {symbol}")
                return cached
        
        # Try Yahoo Finance unless forced to demo
        if not self.force_demo:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, auto_adjust=True, actions=False)
                
                if not df.empty:
                    df = self._prepare_dataframe(df)
                    if self.cache_enabled:
                        self.db_manager.save_data(symbol, df)
                    logger.info(f"✅ Got REAL data for {symbol}")
                    return df
            except Exception as e:
                logger.warning(f"Yahoo Finance failed: {e}")
        
        # Fall back to demo data
        logger.warning(f"⚠️  Using DEMO DATA for {symbol}")
        df = self._generate_demo_data(symbol, start_date, end_date)
        
        if self.cache_enabled:
            try:
                self.db_manager.save_data(symbol, df)
            except:
                pass  # Don't fail if caching fails
        
        return df
    
    def _generate_demo_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate realistic demo stock data"""
        presets = {
            'AAPL': {'price': 150, 'vol': 0.020, 'trend': 0.0005},
            'MSFT': {'price': 350, 'vol': 0.018, 'trend': 0.0006},
            'GOOGL': {'price': 140, 'vol': 0.022, 'trend': 0.0004},
            'TSLA': {'price': 250, 'vol': 0.035, 'trend': 0.0008},
            'SPY': {'price': 450, 'vol': 0.012, 'trend': 0.0004},
            'AMZN': {'price': 170, 'vol': 0.025, 'trend': 0.0005},
            'META': {'price': 350, 'vol': 0.028, 'trend': 0.0006},
            'NVDA': {'price': 500, 'vol': 0.030, 'trend': 0.0010},
            'JPM': {'price': 160, 'vol': 0.018, 'trend': 0.0003},
            'V': {'price': 250, 'vol': 0.015, 'trend': 0.0004},
            'QQQ': {'price': 380, 'vol': 0.015, 'trend': 0.0005},
        }
        
        preset = presets.get(symbol, {'price': 100, 'vol': 0.02, 'trend': 0.0004})
        
        dates = pd.bdate_range(start=start_date, end=end_date)
        np.random.seed(hash(symbol) % 2**32)
        
        returns = np.random.normal(preset['trend'], preset['vol'], len(dates))
        prices = preset['price'] * np.exp(np.cumsum(returns))
        
        data = []
        for date, close in zip(dates, prices):
            rng = close * preset['vol'] * np.random.uniform(0.5, 1.5)
            high = close + rng * np.random.uniform(0, 1)
            low = close - rng * np.random.uniform(0, 1)
            open_p = close + rng * np.random.uniform(-0.5, 0.5)
            
            data.append({
                'Open': round(max(open_p, low), 2),
                'High': round(max(high, close, open_p), 2),
                'Low': round(min(low, close, open_p), 2),
                'Close': round(close, 2),
                'Volume': int(10000000 * np.random.uniform(0.7, 1.3))
            })
        
        df = pd.DataFrame(data, index=dates)
        logger.info(f"Generated {len(df)} days: ${df['Low'].min():.2f}-${df['High'].max():.2f}")
        return df
    
    def _get_from_cache(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Retrieve from cache if available"""
        if not self.db_manager:
            return None
        
        try:
            cached_df = self.db_manager.load_data(symbol)
            if cached_df is None or cached_df.empty:
                return None
            
            # Check if stale
            cache_age = (datetime.now() - pd.to_datetime(cached_df.index.max())).days
            if cache_age > config.CACHE_EXPIRY_DAYS:
                return None
            
            return cached_df.loc[start_date:end_date]
        except:
            return None
    
    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean dataframe"""
        columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        
        df = df[columns].copy()
        
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        df = df.ffill().dropna()
        
        for col in columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def fetch_multiple(self, symbols: List[str], start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> dict:
        """Fetch multiple symbols"""
        data = {}
        for symbol in symbols:
            try:
                data[symbol] = self.fetch_data(symbol, start_date, end_date)
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
        return data
