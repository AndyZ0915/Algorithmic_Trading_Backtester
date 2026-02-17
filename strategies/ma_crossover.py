"""
Moving Average Crossover Strategy - FIXED VERSION
Attributes are set BEFORE _validate_params() is called.
"""

import pandas as pd
from .base_strategy import BaseStrategy


class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover strategy.
    Buy when short MA crosses above long MA (golden cross).
    Sell when short MA crosses below long MA (death cross).
    """

    def __init__(self, short_window: int = 50, long_window: int = 200):
        """
        Args:
            short_window: Short moving average period (default: 50)
            long_window: Long moving average period (default: 200)
        """
        # Set attributes FIRST before calling super().__init__
        self.short_window = short_window
        self.long_window = long_window

        super().__init__(
            name="Moving Average Crossover",
            short_window=short_window,
            long_window=long_window
        )

        # Validate AFTER attributes are set
        self._validate_params()

    def _validate_params(self):
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("Window periods must be positive integers")
        if self.short_window >= self.long_window:
            raise ValueError(f"Short window ({self.short_window}) must be less than long window ({self.long_window})")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['MA_short'] = df['Close'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['Close'].rolling(window=self.long_window).mean()
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        df['signal'] = 0

        # Create position: 1 when short > long
        df['position'] = 0
        valid = df['MA_long'].notna() & df['MA_short'].notna()
        df.loc[valid, 'position'] = (df.loc[valid, 'MA_short'] > df.loc[valid, 'MA_long']).astype(int)

        # Signal on position changes
        df['signal'] = df['position'].diff().fillna(0).astype(int)

        return df