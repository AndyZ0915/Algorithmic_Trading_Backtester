"""
RSI (Relative Strength Index) Strategy - FIXED VERSION
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    RSI Strategy.
    Buy when RSI crosses below oversold level.
    Sell when RSI crosses above overbought level.
    """

    def __init__(self, period: int = 14, overbought: int = 70, oversold: int = 30):
        """
        Args:
            period: RSI calculation period (default: 14)
            overbought: Overbought threshold - sell signal (default: 70)
            oversold: Oversold threshold - buy signal (default: 30)
        """
        # Set attributes FIRST
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

        super().__init__(
            name="RSI Strategy",
            period=period,
            overbought=overbought,
            oversold=oversold
        )

        self._validate_params()

    def _validate_params(self):
        if self.period <= 0:
            raise ValueError("RSI period must be positive")
        if not (0 < self.oversold < self.overbought < 100):
            raise ValueError("Must satisfy: 0 < oversold < overbought < 100")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        delta = df['Close'].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(com=self.period - 1, min_periods=self.period).mean()
        avg_loss = loss.ewm(com=self.period - 1, min_periods=self.period).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        df['signal'] = 0

        # Buy when RSI crosses from below oversold upward
        df['in_oversold'] = df['RSI'] < self.oversold
        df['in_overbought'] = df['RSI'] > self.overbought

        # Signal on transitions
        df.loc[df['in_oversold'] & ~df['in_oversold'].shift(1).fillna(False), 'signal'] = 1
        df.loc[df['in_overbought'] & ~df['in_overbought'].shift(1).fillna(False), 'signal'] = -1

        df = df.drop(columns=['in_oversold', 'in_overbought'])
        return df