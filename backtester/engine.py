"""Backtest engine with explicit execution timing to avoid look-ahead bias."""
import pandas as pd
import config
from data import DataFetcher
from strategies.base_strategy import BaseStrategy
from .portfolio import Portfolio
from .metrics import PerformanceMetrics

class Backtester:
    def __init__(self,symbol,start_date,end_date,initial_capital=config.DEFAULT_INITIAL_CAPITAL,commission=config.DEFAULT_COMMISSION,slippage=config.DEFAULT_SLIPPAGE,execution="next_open",position_size=config.DEFAULT_POSITION_SIZE,benchmark=config.DEFAULT_BENCHMARK,data=None,data_source=None):
        self.symbol=symbol.upper(); self.start_date=start_date; self.end_date=end_date; self.initial_capital=initial_capital; self.commission=commission; self.slippage=slippage; self.execution=execution; self.position_size=position_size; self.benchmark_symbol=benchmark
        self.data_fetcher=DataFetcher(); self.data=data if data is not None else self.data_fetcher.fetch_data(self.symbol,start_date,end_date); self.data_source=data_source or self.data_fetcher.last_source; self.last_results=None
    def _execution_price(self,df,i,signal):
        if self.execution=="same_close": return float(df.Close.iloc[i]), i
        if i+1>=len(df): return None, None
        if self.execution=="next_open": return float(df.Open.iloc[i+1]), i+1
        if self.execution=="next_close": return float(df.Close.iloc[i+1]), i+1
        raise ValueError("Execution must be same_close, next_open, or next_close.")
    def run(self,strategy:BaseStrategy):
        signals=strategy.generate_signals(self.data); p=Portfolio(self.initial_capital,self.commission,self.slippage,self.position_size); pending=None
        for i,(date,row) in enumerate(signals.iterrows()):
            if pending is not None and pending["exec_index"]==i:
                p.execute_trade(date,pending["price"],pending["signal"]); pending=None
            p.update_equity_curve(date,float(row.Close))
            signal=int(row.get("signal",0))
            if signal in (-1,1) and pending is None:
                price,exec_idx=self._execution_price(signals,i,signal)
                if price is not None: pending={"signal":signal,"price":price,"exec_index":exec_idx}
        if p.shares>0:
            last_date=signals.index[-1]; last_close=float(signals.Close.iloc[-1]); p._sell(last_date,last_close); p.equity_curve[-1]=p.get_equity(last_close)
        eq=p.get_equity_curve_df(); trades=p.get_trades_df(); metrics=PerformanceMetrics(eq,trades,self.data.Close,self.initial_capital)
        self.last_results=BacktestResult(metrics,eq,trades,signals,self.data_source,self.execution,self.position_size)
        return self.last_results

class BacktestResult:
    def __init__(self,metrics,equity_curve,trades,signals,data_source,execution,position_size): self.metrics=metrics; self.equity_curve=equity_curve; self.trades=trades; self.signals=signals; self.data_source=data_source; self.execution=execution; self.position_size=position_size
    def __getattr__(self,name): return getattr(self.metrics,name)
