"""Plotly charts used by the research UI."""
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import config

def _layout(fig,title,height=450): fig.update_layout(title=title,height=height,template=config.CHART_TEMPLATE,hovermode="x unified",legend=dict(orientation="h")); return fig

def price_chart(df,title="Price and Indicators"):
    fig=go.Figure(); fig.add_trace(go.Candlestick(x=df.index,open=df.Open,high=df.High,low=df.Low,close=df.Close,name="Price"))
    for col,name in [("MA_short","Fast MA"),("MA_long","Slow MA"),("BB_upper","Upper Band"),("BB_lower","Lower Band")]:
        if col in df: fig.add_trace(go.Scatter(x=df.index,y=df[col],name=name,mode="lines"))
    return _layout(fig,title,600)

def equity_chart(equity,benchmark=None,title="Strategy vs Benchmark"):
    fig=go.Figure(); fig.add_trace(go.Scatter(x=equity.index,y=equity.equity,name="Strategy"))
    if benchmark is not None and len(benchmark): fig.add_trace(go.Scatter(x=benchmark.index,y=benchmark/benchmark.iloc[0]*equity.equity.iloc[0],name="Benchmark",line=dict(dash="dash")))
    fig.update_yaxes(tickprefix="$",tickformat=",.0f"); return _layout(fig,title,500)

def drawdown_chart(equity,title="Drawdown"):
    dd=(equity.equity/equity.equity.cummax()-1)*100; fig=go.Figure(go.Scatter(x=dd.index,y=dd,fill="tozeroy",name="Drawdown")); fig.update_yaxes(ticksuffix="%"); return _layout(fig,title,350)

def monthly_heatmap(equity,title="Monthly Returns (%)"):
    monthly=equity.equity.resample("ME").last().pct_change()*100
    if monthly.empty: return _layout(go.Figure(),title,300)
    frame=pd.DataFrame({"year":monthly.index.year,"month":monthly.index.month,"ret":monthly.values}).dropna(); pivot=frame.pivot(index="year",columns="month",values="ret").reindex(columns=range(1,13)); fig=go.Figure(go.Heatmap(z=pivot.values,x=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],y=pivot.index,text=np.round(pivot.values,1),texttemplate="%{text}",zmid=0)); return _layout(fig,title,max(300,100+40*len(pivot)))

def rolling_chart(equity,title="Rolling Risk"):
    r=equity.equity.pct_change(); vol=r.rolling(63).std()*np.sqrt(252)*100; sharpe=(r-0.04/252).rolling(126).mean()/r.rolling(126).std()*np.sqrt(252); fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=.08,subplot_titles=("63-Day Annualized Volatility (%)","126-Day Rolling Sharpe")); fig.add_trace(go.Scatter(x=vol.index,y=vol,name="Volatility"),row=1,col=1); fig.add_trace(go.Scatter(x=sharpe.index,y=sharpe,name="Sharpe"),row=2,col=1); return _layout(fig,title,650)

def trade_distribution(trades,title="Trade Return Distribution"):
    fig=go.Figure();
    if not trades.empty: fig.add_trace(go.Histogram(x=trades.return_pct,name="Trade return"));
    return _layout(fig,title,350)
