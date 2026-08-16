import pandas as pd
from .base_strategy import BaseStrategy
class BollingerBandsStrategy(BaseStrategy):
    name="Bollinger Bands"
    def __init__(self, period=20, num_std=2.0):
        if period<=0 or num_std<=0: raise ValueError("Period and standard deviation must be positive.")
        super().__init__(period=period,num_std=num_std); self.period=period; self.num_std=num_std
    def calculate_indicators(self,data):
        df=data.copy(); df["BB_mid"]=df.Close.rolling(self.period).mean(); s=df.Close.rolling(self.period).std(); df["BB_upper"]=df.BB_mid+self.num_std*s; df["BB_lower"]=df.BB_mid-self.num_std*s; df["BB_pct"]=(df.Close-df.BB_lower)/(df.BB_upper-df.BB_lower); return df
    def generate_signals(self,data):
        self.validate_data(data); df=self.calculate_indicators(data); state=0; sig=[]; pos=[]
        for _,r in df.iterrows():
            if pd.notna(r.BB_lower) and state==0 and r.Close<r.BB_lower: state=1; s=1
            elif pd.notna(r.BB_upper) and state==1 and r.Close>r.BB_upper: state=0; s=-1
            else: s=0
            sig.append(s); pos.append(state)
        df["position"]=pos; df["signal"]=sig; return df
