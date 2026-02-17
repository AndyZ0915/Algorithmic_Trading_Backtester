"""
Utility helper functions.
"""

import pandas as pd
from typing import Union


def format_currency(value: float) -> str:
    """Format value as currency."""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.2f}%"


def calculate_cagr(
    start_value: float,
    end_value: float,
    years: float
) -> float:
    """
    Calculate Compound Annual Growth Rate.
    
    Args:
        start_value: Initial value
        end_value: Final value
        years: Number of years
    
    Returns:
        CAGR as percentage
    """
    if years <= 0 or start_value <= 0:
        return 0.0
    
    return ((end_value / start_value) ** (1 / years) - 1) * 100


def resample_data(
    data: pd.DataFrame,
    freq: str = 'W'
) -> pd.DataFrame:
    """
    Resample OHLCV data to different frequency.
    
    Args:
        data: DataFrame with OHLCV data
        freq: Pandas frequency string ('D', 'W', 'M', etc.)
    
    Returns:
        Resampled DataFrame
    """
    resampled = pd.DataFrame()
    resampled['Open'] = data['Open'].resample(freq).first()
    resampled['High'] = data['High'].resample(freq).max()
    resampled['Low'] = data['Low'].resample(freq).min()
    resampled['Close'] = data['Close'].resample(freq).last()
    resampled['Volume'] = data['Volume'].resample(freq).sum()
    
    return resampled.dropna()
