import pandas as pd, numpy as np
from .base_strategy import BaseStrategy
class MeanReversionStrategy(BaseStrategy):
    name="Mean Reversion"
    def __init__(self, lookback_period=20, entry_threshold=2.0, exit_threshold=0.5):
        if lookback_period<=1 or entry_threshold<=0 or not 0<=exit_threshold<entry_threshold: raise ValueError("Require lookback > 1, positive entry threshold, and 0 <= exit < entry.")
        super().__init__(lookback_period=lookback_period,entry_threshold=entry_threshold,exit_threshold=exit_threshold); self.lookback_period=lookback_period; self.entry_threshold=entry_threshold; self.exit_threshold=exit_threshold
    def calculate_indicators(self,data):
        df=data.copy(); mean=df.Close.rolling(self.lookback_period).mean(); std=df.Close.rolling(self.lookback_period).std(); df["rolling_mean"]=mean; df["zscore"]=(df.Close-mean)/std.replace(0,np.nan); return df
    def generate_signals(self,data):
        self.validate_data(data); df=self.calculate_indicators(data); state=0; sig=[]; pos=[]
        for z in df.zscore:
            if pd.isna(z): s=0
            elif state==0 and z < -self.entry_threshold: state=1; s=1
            elif state==1 and z >= -self.exit_threshold: state=0; s=-1
            else: s=0
            sig.append(s); pos.append(state)
        df["position"]=pos; df["signal"]=sig; return df
