"""RSI-based trading strategy."""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    Trades overbought/oversold conditions using RSI.
    Buy when RSI < oversold threshold.
    Sell when RSI > overbought threshold.
    """
    
    def __init__(self, period=14, overbought=70, oversold=30):
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
            raise ValueError("Period must be positive")
        if not (0 < self.oversold < self.overbought < 100):
            raise ValueError("Need: 0 < oversold < overbought < 100")
    
    def calculate_indicators(self, data):
        df = data.copy()
        delta = df['Close'].diff()
        
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        avg_gain = gain.ewm(com=self.period - 1, min_periods=self.period).mean()
        avg_loss = loss.ewm(com=self.period - 1, min_periods=self.period).mean()
        
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def generate_signals(self, data):
        df = self.calculate_indicators(data)
        df['signal'] = 0
        
        # Simple approach: buy below oversold, sell above overbought
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1
        
        return df
