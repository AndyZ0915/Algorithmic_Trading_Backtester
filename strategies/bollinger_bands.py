"""
Bollinger Bands Strategy - FIXED VERSION
"""

import pandas as pd
from .base_strategy import BaseStrategy


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands mean reversion strategy.
    Buy when price touches lower band (oversold).
    Sell when price touches upper band (overbought).
    """

    def __init__(self, period: int = 20, num_std: float = 2.0):
        """
        Args:
            period: Moving average period (default: 20)
            num_std: Number of standard deviations for bands (default: 2.0)
        """
        # Set attributes FIRST
        self.period = period
        self.num_std = num_std

        super().__init__(
            name="Bollinger Bands",
            period=period,
            num_std=num_std
        )

        self._validate_params()

    def _validate_params(self):
        if self.period <= 0:
            raise ValueError("Period must be positive")
        if self.num_std <= 0:
            raise ValueError("Number of standard deviations must be positive")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        df['BB_mid'] = df['Close'].rolling(window=self.period).mean()
        rolling_std = df['Close'].rolling(window=self.period).std()

        df['BB_upper'] = df['BB_mid'] + (self.num_std * rolling_std)
        df['BB_lower'] = df['BB_mid'] - (self.num_std * rolling_std)

        # Bandwidth and %B
        df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_mid']
        df['BB_pct'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = self.calculate_indicators(data)
        df['signal'] = 0

        # Buy when price crosses below lower band
        df.loc[df['Close'] < df['BB_lower'], 'signal'] = 1

        # Sell when price crosses above upper band
        df.loc[df['Close'] > df['BB_upper'], 'signal'] = -1

        return df
