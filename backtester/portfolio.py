"""Long-only portfolio accounting with explicit costs and execution records."""
from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class Trade:
    entry_date: object; exit_date: object; entry_price: float; exit_price: float; shares: float
    direction: str; entry_commission: float; exit_commission: float; pnl: float; return_pct: float; holding_days: int

class Portfolio:
    def __init__(self, initial_capital=10000.0, commission=0.001, slippage=0.0005, position_size=1.0):
        if initial_capital<=0: raise ValueError("Initial capital must be positive.")
        if not 0<=commission<1 or not 0<=slippage<1: raise ValueError("Commission/slippage must be between 0 and 1.")
        if not 0<position_size<=1: raise ValueError("Position size must be in (0, 1].")
        self.initial_capital=initial_capital; self.cash=initial_capital; self.commission_rate=commission; self.slippage_rate=slippage; self.position_size=position_size
        self.shares=0.0; self.entry_price=0.0; self.entry_date=None; self.entry_commission=0.0; self.equity_curve=[]; self.dates=[]; self.trades=[]; self.total_commission=0.0; self.total_slippage=0.0
    def get_equity(self, price): return self.cash+self.shares*price
    def update_equity_curve(self,date,price): self.dates.append(date); self.equity_curve.append(self.get_equity(price))
    def execute_trade(self,date,price,signal):
        if signal==1 and self.shares==0: return self._buy(date,price)
        if signal==-1 and self.shares>0: return self._sell(date,price)
        return False
    def _buy(self,date,market_price):
        target_cash=self.cash*self.position_size
        effective=market_price*(1+self.slippage_rate); shares=target_cash/(effective*(1+self.commission_rate))
        if shares<=0: return False
        gross=shares*effective; commission=gross*self.commission_rate; total=gross+commission
        if total>self.cash: shares=(self.cash)/(effective*(1+self.commission_rate)); gross=shares*effective; commission=gross*self.commission_rate; total=gross+commission
        self.cash-=total; self.shares=shares; self.entry_price=effective; self.entry_date=date; self.entry_commission=commission; self.total_commission+=commission; self.total_slippage+=shares*(effective-market_price); return True
    def _sell(self,date,market_price):
        if self.shares<=0: return False
        effective=market_price*(1-self.slippage_rate); gross=self.shares*effective; commission=gross*self.commission_rate; proceeds=gross-commission
        pnl=proceeds-(self.shares*self.entry_price)-self.entry_commission
        cost=self.shares*self.entry_price+self.entry_commission
        ret=pnl/cost*100 if cost else 0.0
        holding=(pd.Timestamp(date)-pd.Timestamp(self.entry_date)).days
        self.trades.append(Trade(self.entry_date,date,self.entry_price,effective,self.shares,"long",self.entry_commission,commission,pnl,ret,holding))
        self.cash+=proceeds; self.total_commission+=commission; self.total_slippage+=self.shares*(market_price-effective); self.shares=0.0; self.entry_price=0.0; self.entry_date=None; self.entry_commission=0.0; return True
    def get_equity_curve_df(self):
        if not self.dates: return pd.DataFrame({"equity":[self.initial_capital]},index=pd.DatetimeIndex([pd.Timestamp("1970-01-01")]))
        return pd.DataFrame({"equity":self.equity_curve},index=pd.DatetimeIndex(self.dates)).sort_index()
    def get_trades_df(self):
        cols=["entry_date","exit_date","entry_price","exit_price","shares","direction","entry_commission","exit_commission","pnl","return_pct","holding_days"]
        if not self.trades: return pd.DataFrame(columns=cols)
        return pd.DataFrame([{k:getattr(t,k) for k in cols} for t in self.trades])
