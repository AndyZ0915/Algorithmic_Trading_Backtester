"""Historical conditional analysis. This is descriptive research, not a future forecast."""
import numpy as np
import pandas as pd

def historical_forward_returns(data, condition, horizons=(1,5,20)):
    """Return forward-return statistics for rows where condition is true.

    The condition is evaluated using the current row. Forward returns use future
    closes only for the historical outcome calculation, never for the condition.
    """
    close=data["Close"].astype(float)
    mask=pd.Series(condition,index=data.index).fillna(False).astype(bool)
    rows=[]
    for horizon in horizons:
        forward=close.shift(-horizon)/close-1
        sample=forward[mask].dropna()
        if sample.empty:
            rows.append({"horizon_days":horizon,"observations":0,"positive_pct":np.nan,"negative_pct":np.nan,"average_return_pct":np.nan,"median_return_pct":np.nan})
        else:
            rows.append({"horizon_days":horizon,"observations":len(sample),"positive_pct":float((sample>0).mean()*100),"negative_pct":float((sample<0).mean()*100),"average_return_pct":float(sample.mean()*100),"median_return_pct":float(sample.median()*100)})
    return pd.DataFrame(rows)

def technical_condition_table(data, strategy_name):
    """Build a simple interpretable condition from the selected strategy."""
    x=data.copy()
    if strategy_name=="MA Crossover" and {"MA_short","MA_long"}.issubset(x.columns):
        condition=x["MA_short"]>x["MA_long"]
    elif strategy_name=="RSI Strategy" and "RSI" in x:
        condition=x["RSI"]<30
    elif strategy_name=="MACD Strategy" and {"MACD","MACD_signal"}.issubset(x.columns):
        condition=x["MACD"]>x["MACD_signal"]
    elif strategy_name=="Bollinger Bands" and "BB_lower" in x:
        condition=x["Close"]<x["BB_lower"]
    elif strategy_name=="Mean Reversion" and "zscore" in x:
        condition=x["zscore"]<-2
    else:
        condition=pd.Series(False,index=x.index)
    return condition
