"""Validation and diagnostics for OHLCV market data."""
from dataclasses import dataclass, field
from typing import List
import numpy as np
import pandas as pd

REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

@dataclass
class DataQualityReport:
    passed: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    rows: int = 0
    start: str = ""
    end: str = ""
    missing_values: int = 0
    duplicate_dates: int = 0
    suspicious_returns: int = 0

    @property
    def status(self) -> str:
        return "PASS" if self.passed and not self.warnings else ("WARNING" if self.passed else "FAIL")

def validate_ohlcv(df: pd.DataFrame, max_daily_return: float = 0.75) -> DataQualityReport:
    warnings, errors = [], []
    if df is None or df.empty:
        return DataQualityReport(False, errors=["No market data was returned."])
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        return DataQualityReport(False, errors=[f"Missing required columns: {', '.join(missing_cols)}"])
    x = df.copy()
    if not isinstance(x.index, pd.DatetimeIndex):
        errors.append("Index must be a DatetimeIndex.")
    else:
        if x.index.tz is not None:
            x.index = x.index.tz_localize(None)
        if not x.index.is_monotonic_increasing:
            errors.append("Dates are not sorted ascending.")
    duplicate_dates = int(x.index.duplicated().sum())
    if duplicate_dates:
        errors.append(f"Found {duplicate_dates} duplicate timestamps.")
    missing_values = int(x[REQUIRED_COLUMNS].isna().sum().sum())
    if missing_values:
        errors.append(f"Found {missing_values} missing OHLCV values.")
    for c in REQUIRED_COLUMNS:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    if (x[["Open", "High", "Low", "Close"]] <= 0).any().any():
        errors.append("Found non-positive price values.")
    if (x["High"] < x[["Open", "Close"]].max(axis=1)).any() or (x["Low"] > x[["Open", "Close"]].min(axis=1)).any():
        errors.append("Found OHLC relationships that are internally inconsistent.")
    if (x["High"] < x["Low"]).any():
        errors.append("Found rows where High is below Low.")
    if (x["Volume"] < 0).any():
        errors.append("Found negative volume.")
    daily_returns = x["Close"].pct_change().abs()
    suspicious = int((daily_returns > max_daily_return).sum())
    if suspicious:
        warnings.append(f"Found {suspicious} unusually large absolute daily returns (> {max_daily_return:.0%}). Review for splits or bad data.")
    if len(x) < 30:
        warnings.append("Less than 30 observations are available; some indicators and annualized statistics may be unstable.")
    return DataQualityReport(
        passed=not errors,
        warnings=warnings,
        errors=errors,
        rows=len(x),
        start=str(x.index.min().date()) if len(x) else "",
        end=str(x.index.max().date()) if len(x) else "",
        missing_values=missing_values,
        duplicate_dates=duplicate_dates,
        suspicious_returns=suspicious,
    )
