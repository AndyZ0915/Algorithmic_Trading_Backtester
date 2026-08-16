"""Free-first market data providers with caching and explicit source reporting."""
import os
import logging
from datetime import datetime
import pandas as pd
from .database import DatabaseManager
from .data_quality import validate_ohlcv
import config

logger = logging.getLogger(__name__)

class DataFetchError(RuntimeError):
    pass

class DataFetcher:
    def __init__(self, cache_enabled=True):
        self.cache_enabled = cache_enabled
        self.db = DatabaseManager() if cache_enabled else None
        self.last_source = None
        self.last_quality = None

    def fetch_data(self, symbol, start_date=None, end_date=None, force_refresh=False, provider="auto"):
        symbol = symbol.strip().upper()
        start_date = start_date or config.DEFAULT_START_DATE
        end_date = end_date or config.DEFAULT_END_DATE
        if pd.Timestamp(start_date) >= pd.Timestamp(end_date):
            raise ValueError("Start date must be before end date.")
        if self.cache_enabled and not force_refresh:
            cached, source = self.db.load_data(symbol)
            if cached is not None and not cached.empty:
                subset = cached.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
                if len(subset) >= 30:
                    report = validate_ohlcv(subset)
                    if report.passed:
                        self.last_source, self.last_quality = f"Cached {source}", report
                        return subset
        providers = [provider] if provider != "auto" else ["yahoo", "alpha_vantage"]
        errors = []
        for name in providers:
            try:
                if name == "yahoo":
                    df = self._fetch_yahoo(symbol, start_date, end_date)
                elif name == "alpha_vantage":
                    df = self._fetch_alpha_vantage(symbol, start_date, end_date)
                else:
                    raise ValueError(f"Unknown provider: {name}")
                report = validate_ohlcv(df)
                if not report.passed:
                    raise DataFetchError("; ".join(report.errors))
                self.last_source, self.last_quality = name, report
                if self.cache_enabled:
                    self.db.save_data(symbol, df, source=name)
                return df
            except Exception as exc:
                errors.append(f"{name}: {exc}")
                logger.warning("%s failed: %s", name, exc)
        raise DataFetchError("No real market-data provider succeeded. " + " | ".join(errors) + " Configure a provider/API key or try again later. The application does not silently substitute simulated prices.")

    def _fetch_yahoo(self, symbol, start, end):
        import yfinance as yf
        df = yf.Ticker(symbol).history(start=start, end=end, auto_adjust=True, actions=False)
        if df.empty:
            raise DataFetchError("Yahoo returned no rows.")
        return self._clean(df)

    def _fetch_alpha_vantage(self, symbol, start, end):
        key = os.getenv(config.ALPHA_VANTAGE_API_KEY_ENV)
        if not key:
            raise DataFetchError("ALPHA_VANTAGE_API_KEY is not configured.")
        import requests
        params = {"function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": symbol, "outputsize": "full", "apikey": key}
        r = requests.get("https://www.alphavantage.co/query", params=params, timeout=20)
        r.raise_for_status()
        payload = r.json()
        series = payload.get("Time Series (Daily)")
        if not series:
            raise DataFetchError(payload.get("Note") or payload.get("Information") or "Alpha Vantage returned no daily series.")
        rows = []
        for date, values in series.items():
            rows.append({"Date": date, "Open": values.get("1. open"), "High": values.get("2. high"), "Low": values.get("3. low"), "Close": values.get("5. adjusted close", values.get("4. close")), "Volume": values.get("6. volume", values.get("5. volume", 0))})
        df = pd.DataFrame(rows).set_index("Date")
        df.index = pd.to_datetime(df.index)
        df = df.loc[pd.Timestamp(start):pd.Timestamp(end)]
        if df.empty:
            raise DataFetchError("Alpha Vantage returned no rows in the requested range.")
        return self._clean(df)

    @staticmethod
    def _clean(df):
        x = df.copy()
        if isinstance(x.columns, pd.MultiIndex):
            x.columns = x.columns.get_level_values(0)
        x.index = pd.to_datetime(x.index).tz_localize(None) if getattr(x.index, "tz", None) is not None else pd.to_datetime(x.index)
        x = x[["Open", "High", "Low", "Close", "Volume"]].apply(pd.to_numeric, errors="coerce").sort_index()
        return x.dropna()
