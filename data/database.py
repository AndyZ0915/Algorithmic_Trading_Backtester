"""
SQLite database manager for caching stock data - PRODUCTION VERSION
Handles timestamp conversion properly for Windows compatibility
"""

import sqlite3
import pandas as pd
import logging
from typing import Optional
from datetime import datetime

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for caching"""
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stock_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        date TEXT NOT NULL,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol, date)
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_symbol_date 
                    ON stock_data(symbol, date)
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metadata (
                        symbol TEXT PRIMARY KEY,
                        last_updated TEXT,
                        data_start_date TEXT,
                        data_end_date TEXT
                    )
                """)
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
    
    def save_data(self, symbol: str, df: pd.DataFrame):
        """Save data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df_to_save = df.copy()
                df_to_save['symbol'] = symbol
                df_to_save['date'] = df_to_save.index.astype(str)
                
                df_to_save = df_to_save[[
                    'symbol', 'date', 'Open', 'High', 'Low', 'Close', 'Volume'
                ]].rename(columns={
                    'Open': 'open', 'High': 'high', 'Low': 'low',
                    'Close': 'close', 'Volume': 'volume'
                })
                
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stock_data WHERE symbol = ?", (symbol,))
                
                df_to_save.to_sql('stock_data', conn, if_exists='append', index=False)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO metadata 
                    (symbol, last_updated, data_start_date, data_end_date)
                    VALUES (?, ?, ?, ?)
                """, (
                    symbol,
                    str(datetime.now()),
                    str(df.index.min()),
                    str(df.index.max())
                ))
                
                conn.commit()
                logger.info(f"Saved {len(df)} rows for {symbol}")
        except Exception as e:
            logger.warning(f"Cache save failed (non-critical): {e}")
    
    def load_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Load data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT date, open, high, low, close, volume
                    FROM stock_data
                    WHERE symbol = ?
                    ORDER BY date
                """
                
                df = pd.read_sql_query(
                    query, conn, params=(symbol,),
                    parse_dates=['date'], index_col='date'
                )
                
                if df.empty:
                    return None
                
                df = df.rename(columns={
                    'open': 'Open', 'high': 'High', 'low': 'Low',
                    'close': 'Close', 'volume': 'Volume'
                })
                
                logger.info(f"Loaded {len(df)} rows for {symbol}")
                return df
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")
            return None
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM stock_data")
                cursor.execute("DELETE FROM metadata")
                conn.commit()
                logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
