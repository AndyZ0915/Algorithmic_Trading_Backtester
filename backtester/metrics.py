"""Risk and return analytics with safe handling of small/degenerate samples."""
import numpy as np, pandas as pd
import config
class PerformanceMetrics:
    def __init__(self,equity_curve,trades,benchmark=None,initial_capital=config.DEFAULT_INITIAL_CAPITAL,risk_free_rate=config.RISK_FREE_RATE):
        self.equity_curve=equity_curve; self.trades=trades; self.benchmark=benchmark; self.initial_capital=initial_capital; self.risk_free_rate=risk_free_rate; self._calculate()
    def _calculate(self):
        e=self.equity_curve.equity.dropna(); r=e.pct_change().dropna(); self.total_return=((e.iloc[-1]/self.initial_capital)-1)*100 if len(e) else 0; days=(e.index[-1]-e.index[0]).days if len(e)>1 else 0; years=days/365.25; self.annualized_return=((e.iloc[-1]/self.initial_capital)**(1/years)-1)*100 if years>0 and e.iloc[-1]>0 else 0; self.volatility=float(r.std(ddof=1)*np.sqrt(252)*100) if len(r)>1 else 0; excess=r-self.risk_free_rate/252; self.sharpe_ratio=float(excess.mean()/r.std(ddof=1)*np.sqrt(252)) if len(r)>1 and r.std(ddof=1)>0 else 0; self.sortino_ratio=float(excess.mean()/r[r<0].std(ddof=1)*np.sqrt(252)) if len(r)>1 and len(r[r<0])>1 and r[r<0].std(ddof=1)>0 else 0; self.max_drawdown=float(((e/e.cummax())-1).min()*100) if len(e) else 0; self.max_drawdown_duration=self._dd_duration(e); self.num_trades=len(self.trades); self.win_rate=float((self.trades.pnl>0).mean()*100) if self.num_trades else 0; wins=self.trades.loc[self.trades.pnl>0,"pnl"].sum() if self.num_trades else 0; losses=-self.trades.loc[self.trades.pnl<0,"pnl"].sum() if self.num_trades else 0; self.profit_factor=float(wins/losses) if losses>0 else (float("inf") if wins>0 else 0); self.avg_trade_return=float(self.trades.return_pct.mean()) if self.num_trades else 0; self.avg_holding_days=float(self.trades.holding_days.mean()) if self.num_trades else 0; self.best_trade=float(self.trades.pnl.max()) if self.num_trades else 0; self.worst_trade=float(self.trades.pnl.min()) if self.num_trades else 0; self.calmar_ratio=float(self.annualized_return/abs(self.max_drawdown)) if self.max_drawdown<0 else 0
    def _dd_duration(self,e):
        if len(e)<2:return 0
        peak=e.iloc[0]; start=None; maxdur=0
        for d,v in e.items():
            if v>=peak: peak=v; start=None
            elif start is None: start=d
            if start is not None: maxdur=max(maxdur,(d-start).days)
        return int(maxdur)
    def as_dict(self): return {"total_return_pct":self.total_return,"annualized_return_pct":self.annualized_return,"volatility_pct":self.volatility,"sharpe":self.sharpe_ratio,"sortino":self.sortino_ratio,"max_drawdown_pct":self.max_drawdown,"max_drawdown_duration_days":self.max_drawdown_duration,"trades":self.num_trades,"win_rate_pct":self.win_rate,"profit_factor":self.profit_factor,"avg_trade_return_pct":self.avg_trade_return,"avg_holding_days":self.avg_holding_days,"best_trade":self.best_trade,"worst_trade":self.worst_trade,"calmar":self.calmar_ratio}
