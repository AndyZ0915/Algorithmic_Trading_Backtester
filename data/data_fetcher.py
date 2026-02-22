"""
Handles fetching stock data from Yahoo Finance.
Falls back to simulated data if Yahoo is down/blocking.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List
import logging

import config
from .database import DatabaseManager

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches stock data with automatic fallback to demo data."""
    
    def __init__(self, cache_enabled=True, force_demo=False):
        self.cache_enabled = cache_enabled
        self.force_demo = force_demo
        self.db = DatabaseManager() if cache_enabled else None
    
    def fetch_data(self, symbol, start_date=None, end_date=None, force_refresh=False):
        """Fetch historical data for a symbol."""
        start_date = start_date or config.DEFAULT_START_DATE
        end_date = end_date or config.DEFAULT_END_DATE
        
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        # Try cache first
        if self.cache_enabled and not force_refresh:
            cached = self._get_cached(symbol, start_date, end_date)
            if cached is not None:
                logger.info(f"Using cached data for {symbol}")
                return cached
        
        # Try Yahoo Finance
        if not self.force_demo:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start_date, end=end_date, auto_adjust=True, actions=False)
                
                if not df.empty:
                    df = self._clean_dataframe(df)
                    if self.cache_enabled:
                        self.db.save_data(symbol, df)
                    logger.info(f"Got real data for {symbol}")
                    return df
            except Exception as e:
                logger.warning(f"Yahoo Finance failed: {e}")
        
        # Use demo data
        logger.warning(f"Using demo data for {symbol}")
        df = self._make_demo_data(symbol, start_date, end_date)
        
        if self.cache_enabled:
            try:
                self.db.save_data(symbol, df)
            except:
                pass
        
        return df
    
    def _make_demo_data(self, symbol, start_date, end_date):
        """Generate realistic-looking price data."""
        # Different stocks get different characteristics
        presets = {
            'AAPL': {'price': 150, 'vol': 0.020, 'trend': 0.0005},
            'MSFT': {'price': 350, 'vol': 0.018, 'trend': 0.0006},
            'GOOGL': {'price': 140, 'vol': 0.022, 'trend': 0.0004},
            'TSLA': {'price': 250, 'vol': 0.035, 'trend': 0.0008},
            'SPY': {'price': 450, 'vol': 0.012, 'trend': 0.0004},
        }
        
        preset = presets.get(symbol, {'price': 100, 'vol': 0.02, 'trend': 0.0004})
        
        dates = pd.bdate_range(start=start_date, end=end_date)
        np.random.seed(hash(symbol) % 2**32)  # consistent for same symbol
        
        # Generate price path
        returns = np.random.normal(preset['trend'], preset['vol'], len(dates))
        prices = preset['price'] * np.exp(np.cumsum(returns))
        
        # Build OHLCV
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
    
    def _get_cached(self, symbol, start_date, end_date):
        if not self.db:
            return None
        
        try:
            cached = self.db.load_data(symbol)
            if cached is None or cached.empty:
                return None
            
            # Check if stale
            age = (datetime.now() - pd.to_datetime(cached.index.max())).days
            if age > config.CACHE_EXPIRY_DAYS:
                return None
            
            return cached.loc[start_date:end_date]
        except:
            return None
    
    def _clean_dataframe(self, df):
        """Clean up Yahoo Finance response."""
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
    
    def fetch_multiple(self, symbols, start_date=None, end_date=None):
        """Fetch data for multiple symbols."""
        data = {}
        for symbol in symbols:
            try:
                data[symbol] = self.fetch_data(symbol, start_date, end_date)
            except Exception as e:
                logger.error(f"Failed {symbol}: {e}")
        return data
