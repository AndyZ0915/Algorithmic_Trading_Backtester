import pandas as pd
from .base_strategy import BaseStrategy
class MovingAverageCrossover(BaseStrategy):
    name = "MA Crossover"
    def __init__(self, short_window=50, long_window=200):
        if short_window <= 0 or long_window <= 0 or short_window >= long_window: raise ValueError("Require 0 < short_window < long_window.")
        super().__init__(short_window=short_window, long_window=long_window); self.short_window=short_window; self.long_window=long_window
    def calculate_indicators(self, data):
        df=data.copy(); df["MA_short"]=df.Close.rolling(self.short_window).mean(); df["MA_long"]=df.Close.rolling(self.long_window).mean(); return df
    def generate_signals(self,data):
        self.validate_data(data); df=self.calculate_indicators(data); pos=(df.MA_short>df.MA_long).astype(int); pos[df.MA_short.isna()|df.MA_long.isna()]=0; df["position"]=pos; df["signal"]=pos.diff().fillna(pos).astype(int); return df
