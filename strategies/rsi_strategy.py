import pandas as pd, numpy as np
from .base_strategy import BaseStrategy
class RSIStrategy(BaseStrategy):
    name="RSI Strategy"
    def __init__(self, period=14, overbought=70, oversold=30):
        if period<=0 or not 0<oversold<overbought<100: raise ValueError("Require positive period and 0 < oversold < overbought < 100.")
        super().__init__(period=period,overbought=overbought,oversold=oversold); self.period=period; self.overbought=overbought; self.oversold=oversold
    def calculate_indicators(self,data):
        df=data.copy(); delta=df.Close.diff(); gain=delta.clip(lower=0); loss=-delta.clip(upper=0); ag=gain.ewm(com=self.period-1,min_periods=self.period).mean(); al=loss.ewm(com=self.period-1,min_periods=self.period).mean(); rs=ag/al.replace(0,np.nan); df["RSI"]=100-100/(1+rs); return df
    def generate_signals(self,data):
        self.validate_data(data); df=self.calculate_indicators(data); state=0; signals=[]; positions=[]
        for rsi in df.RSI:
            if pd.isna(rsi): sig=0
            elif state==0 and rsi<self.oversold: state=1; sig=1
            elif state==1 and rsi>self.overbought: state=0; sig=-1
            else: sig=0
            positions.append(state); signals.append(sig)
        df["position"]=positions; df["signal"]=signals; return df
