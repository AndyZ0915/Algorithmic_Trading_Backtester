"""Simple SQLite caching for stock data."""

import sqlite3
import pandas as pd
import logging
from datetime import datetime

import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles SQLite caching."""
    
    def __init__(self, db_path=config.DATABASE_PATH):
        self.db_path = db_path
        self._setup_tables()
    
    def _setup_tables(self):
        """Create tables if needed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS stock_data (
                        symbol TEXT,
                        date TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        PRIMARY KEY (symbol, date)
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS metadata (
                        symbol TEXT PRIMARY KEY,
                        last_updated TEXT,
                        start_date TEXT,
                        end_date TEXT
                    )
                """)
                
                conn.commit()
                logger.info(f"Database ready at {self.db_path}")
        except Exception as e:
            logger.error(f"DB setup failed: {e}")
    
    def save_data(self, symbol, df):
        """Save data to cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare data
                data = df.copy()
                data['symbol'] = symbol
                data['date'] = data.index.astype(str)
                data = data.rename(columns={
                    'Open': 'open', 'High': 'high', 'Low': 'low',
                    'Close': 'close', 'Volume': 'volume'
                })
                
                # Clear old data for this symbol
                conn.execute("DELETE FROM stock_data WHERE symbol = ?", (symbol,))
                
                # Insert new data
                data[['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']].to_sql(
                    'stock_data', conn, if_exists='append', index=False
                )
                
                # Update metadata
                conn.execute("""
                    INSERT OR REPLACE INTO metadata (symbol, last_updated, start_date, end_date)
                    VALUES (?, ?, ?, ?)
                """, (symbol, str(datetime.now()), str(df.index.min()), str(df.index.max())))
                
                conn.commit()
                logger.info(f"Cached {len(df)} rows for {symbol}")
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
    
    def load_data(self, symbol):
        """Load data from cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT date, open, high, low, close, volume
                    FROM stock_data
                    WHERE symbol = ?
                    ORDER BY date
                """
                df = pd.read_sql_query(query, conn, params=(symbol,), parse_dates=['date'], index_col='date')
                
                if df.empty:
                    return None
                
                df = df.rename(columns={
                    'open': 'Open', 'high': 'High', 'low': 'Low',
                    'close': 'Close', 'volume': 'Volume'
                })
                
                logger.info(f"Loaded {len(df)} rows for {symbol} from cache")
                return df
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")
            return None
