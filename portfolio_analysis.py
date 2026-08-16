"""Multi-asset portfolio calculations for research and visualization."""
import numpy as np
import pandas as pd

def build_portfolio(price_map, weights):
    """Combine normalized asset prices using fixed starting weights."""
    aligned=pd.concat(price_map,axis=1,join="inner").dropna()
    if aligned.empty: raise ValueError("Portfolio assets have no overlapping dates.")
    w=pd.Series(weights,dtype=float); w=w/w.sum()
    missing=[s for s in w.index if s not in aligned.columns]
    if missing: raise ValueError(f"Missing prices for: {missing}")
    normalized=aligned[w.index]/aligned[w.index].iloc[0]
    equity=(normalized*w).sum(axis=1)
    return aligned, normalized, equity

def portfolio_stats(equity):
    r=equity.pct_change().dropna()
    vol=float(r.std()*np.sqrt(252)*100) if len(r)>1 else 0
    sharpe=float((r.mean()-0.04/252)/r.std()*np.sqrt(252)) if len(r)>1 and r.std()>0 else 0
    dd=(equity/equity.cummax()-1)*100
    return {"total_return_pct":float((equity.iloc[-1]/equity.iloc[0]-1)*100),"annualized_volatility_pct":vol,"sharpe":sharpe,"max_drawdown_pct":float(dd.min())}
