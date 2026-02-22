"""
Mean Reversion Strategy - FIXED VERSION
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    Z-score based mean reversion strategy.
    Buy when price is significantly below its mean (oversold).
    Sell when price returns to mean or above (overbought).
    """

    def __init__(self, lookback_period: int = 20, entry_threshold: float = 2.0,
                 exit_threshold: float = 0.5):
        """
        Args:
            lookback_period: Rolling window for mean/std calculation (default: 20)
            entry_threshold: Z-score to trigger entry (default: 2.0)
            exit_threshold: Z-score to trigger exit (default: 0.5)
        """
        # Set attributes FIRST
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold

        super().__init__(
            name="Mean Reversion",
            lookback_period=lookback_period,
            entry_threshold=entry_threshold,
            exit_threshold=exit_threshold
        )

        self._validate_params()

    def _validate_params(self):
        if self.lookback_period <= 0:
            raise ValueError("Lookback period must be positive")
        if self.entry_threshold <= 0:
            raise ValueError("Entry threshold must be positive")
        if self.exit_threshold < 0:
            raise ValueError("Exit threshold must be non-negative")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        rolling_mean = df['Close'].rolling(window=self.lookback_period).mean()
        rolling_std = df['Close'].rolling(window=self.lookback_period).std()

        # Z-score: how many std devs from the mean
        df['zscore'] = (df['Close'] - rolling_mean) / rolling_std.replace(0, np.nan)
        df['rolling_mean'] = rolling_mean

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        df['signal'] = 0

        # Buy when price is significantly below mean (negative z-score)
        df.loc[df['zscore'] < -self.entry_threshold, 'signal'] = 1

        # Sell when price returns near mean or goes above
        df.loc[df['zscore'] > self.entry_threshold, 'signal'] = -1

        return df
