"""
MACD (Moving Average Convergence Divergence) Strategy - FIXED VERSION
"""

import pandas as pd
from .base_strategy import BaseStrategy


class MACDStrategy(BaseStrategy):
    """
    MACD Strategy.
    Buy when MACD line crosses above signal line.
    Sell when MACD line crosses below signal line.
    """

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        Args:
            fast_period: Fast EMA period (default: 12)
            slow_period: Slow EMA period (default: 26)
            signal_period: Signal line EMA period (default: 9)
        """
        # Set attributes FIRST
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

        super().__init__(
            name="MACD Strategy",
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period
        )

        self._validate_params()

    def _validate_params(self):
        if self.fast_period <= 0 or self.slow_period <= 0 or self.signal_period <= 0:
            raise ValueError("All periods must be positive")
        if self.fast_period >= self.slow_period:
            raise ValueError("Fast period must be less than slow period")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        ema_fast = df['Close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=self.slow_period, adjust=False).mean()

        df['MACD'] = ema_fast - ema_slow
        df['MACD_signal'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        df['signal'] = 0

        # MACD above signal line
        df['position'] = (df['MACD'] > df['MACD_signal']).astype(int)

        # Signal on crossovers
        df['signal'] = df['position'].diff().fillna(0).astype(int)

        return df