import pandas as pd
from backtester import Backtester
from strategies.base_strategy import BaseStrategy
class OneShot(BaseStrategy):
    name="One Shot"
    def generate_signals(self,data):
        x=data.copy(); x["signal"]=0; x.iloc[0,x.columns.get_loc("signal")]=1; x.iloc[-2,x.columns.get_loc("signal")]=-1; return x

def data():
    idx=pd.bdate_range("2025-01-02",periods=4); return pd.DataFrame({"Open":[10,20,30,40],"High":[11,21,31,41],"Low":[9,19,29,39],"Close":[10,20,30,40],"Volume":[100]*4},index=idx)

def test_next_open_does_not_execute_on_signal_bar():
    r=Backtester("TEST","2025-01-02","2025-01-10",1000,0,0,"next_open",1,data=data()).run(OneShot())
    assert not r.trades.empty
    assert r.trades.iloc[0].entry_price == 20

def test_metrics_are_finite_for_simple_run():
    r=Backtester("TEST","2025-01-02","2025-01-10",1000,0,0,"next_open",1,data=data()).run(OneShot())
    assert r.total_return != float("inf")
    assert r.max_drawdown <= 0
