"""SQLite cache and saved research runs."""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd
import config

class DatabaseManager:
    def __init__(self, db_path=config.DATABASE_PATH):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._setup()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _setup(self):
        with self._connect() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS stock_data (
                symbol TEXT NOT NULL, date TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, volume REAL,
                source TEXT, fetched_at TEXT, PRIMARY KEY(symbol, date)
            )""")
            conn.execute("""CREATE TABLE IF NOT EXISTS research_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, symbol TEXT NOT NULL,
                strategy TEXT NOT NULL, parameters TEXT NOT NULL, start_date TEXT, end_date TEXT,
                initial_capital REAL, commission REAL, slippage REAL, execution TEXT, position_size REAL,
                benchmark TEXT, data_source TEXT, metrics TEXT NOT NULL
            )""")
            conn.commit()

    def save_data(self, symbol, df, source="unknown"):
        rows = []
        fetched_at = datetime.utcnow().isoformat()
        for idx, row in df.iterrows():
            rows.append((symbol, pd.Timestamp(idx).isoformat(), float(row.Open), float(row.High), float(row.Low), float(row.Close), float(row.Volume), source, fetched_at))
        with self._connect() as conn:
            conn.executemany("""INSERT OR REPLACE INTO stock_data
                (symbol,date,open,high,low,close,volume,source,fetched_at) VALUES (?,?,?,?,?,?,?,?,?)""", rows)
            conn.commit()

    def load_data(self, symbol):
        with self._connect() as conn:
            df = pd.read_sql_query("SELECT date,open,high,low,close,volume,source FROM stock_data WHERE symbol=? ORDER BY date", conn, params=(symbol,), parse_dates=["date"])
        if df.empty:
            return None, None
        source = str(df["source"].dropna().iloc[-1]) if df["source"].notna().any() else "unknown"
        df = df.drop(columns=["source"]).set_index("date")
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        return df, source

    def save_run(self, metadata, metrics):
        with self._connect() as conn:
            cur = conn.execute("""INSERT INTO research_runs
                (created_at,symbol,strategy,parameters,start_date,end_date,initial_capital,commission,slippage,execution,position_size,benchmark,data_source,metrics)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                    datetime.utcnow().isoformat(), metadata["symbol"], metadata["strategy"], json.dumps(metadata.get("parameters", {})),
                    metadata.get("start_date"), metadata.get("end_date"), metadata.get("initial_capital"), metadata.get("commission"),
                    metadata.get("slippage"), metadata.get("execution"), metadata.get("position_size"), metadata.get("benchmark"),
                    metadata.get("data_source"), json.dumps(metrics, default=str)))
            conn.commit()
            return cur.lastrowid

    def list_runs(self, limit=50):
        with self._connect() as conn:
            return pd.read_sql_query("SELECT * FROM research_runs ORDER BY run_id DESC LIMIT ?", conn, params=(limit,))
