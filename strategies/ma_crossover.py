"""Moving average crossover strategy."""

import pandas as pd
from .base_strategy import BaseStrategy


class MovingAverageCrossover(BaseStrategy):
    """
    Classic golden cross / death cross strategy.
    Buy when short MA crosses above long MA.
    Sell when short MA crosses below long MA.
    """
    
    def __init__(self, short_window=50, long_window=200):
        self.short_window = short_window
        self.long_window = long_window
        
        super().__init__(
            name="MA Crossover",
            short_window=short_window,
            long_window=long_window
        )
        
        self._validate_params()
    
    def _validate_params(self):
        if self.short_window <= 0 or self.long_window <= 0:
            raise ValueError("Windows must be positive")
        if self.short_window >= self.long_window:
            raise ValueError(f"Short window ({self.short_window}) must be less than long ({self.long_window})")
    
    def calculate_indicators(self, data):
        df = data.copy()
        df['MA_short'] = df['Close'].rolling(self.short_window).mean()
        df['MA_long'] = df['Close'].rolling(self.long_window).mean()
        return df
    
    def generate_signals(self, data):
        df = self.calculate_indicators(data)
        df['signal'] = 0
        
        # Position: 1 when short > long
        df['position'] = 0
        valid = df['MA_long'].notna() & df['MA_short'].notna()
        df.loc[valid, 'position'] = (df.loc[valid, 'MA_short'] > df.loc[valid, 'MA_long']).astype(int)
        
        # Signal when position changes
        df['signal'] = df['position'].diff().fillna(0).astype(int)
        
        return df
