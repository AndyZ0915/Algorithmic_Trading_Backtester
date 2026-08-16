import pandas as pd
from .base_strategy import BaseStrategy
class MACDStrategy(BaseStrategy):
    name="MACD Strategy"
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        if not (0<fast_period<slow_period) or signal_period<=0: raise ValueError("Require 0 < fast < slow and positive signal period.")
        super().__init__(fast_period=fast_period,slow_period=slow_period,signal_period=signal_period); self.fast_period=fast_period; self.slow_period=slow_period; self.signal_period=signal_period
    def calculate_indicators(self,data):
        df=data.copy(); fast=df.Close.ewm(span=self.fast_period,adjust=False).mean(); slow=df.Close.ewm(span=self.slow_period,adjust=False).mean(); df["MACD"]=fast-slow; df["MACD_signal"]=df.MACD.ewm(span=self.signal_period,adjust=False).mean(); df["MACD_hist"]=df.MACD-df.MACD_signal; return df
    def generate_signals(self,data):
        self.validate_data(data); df=self.calculate_indicators(data); pos=(df.MACD>df.MACD_signal).astype(int); df["position"]=pos; df["signal"]=pos.diff().fillna(0).astype(int); return df
