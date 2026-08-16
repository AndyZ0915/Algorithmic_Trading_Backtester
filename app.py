"""Quant Research Platform v3.0: analysis, calculations and visual research only."""
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import config
from data import DataFetcher, NewsFetcher
from backtester import Backtester, historical_forward_returns, technical_condition_table
from strategies import MovingAverageCrossover, RSIStrategy, MACDStrategy, BollingerBandsStrategy, MeanReversionStrategy
from visualization import charts
from portfolio_analysis import build_portfolio, portfolio_stats

st.set_page_config(page_title=config.APP_TITLE,page_icon=config.APP_ICON,layout="wide")
st.title(f"{config.APP_ICON} {config.APP_TITLE}")
st.caption("Quantitative market research, backtesting, risk analysis and interactive visuals. No AI and no live trading.")

with st.sidebar:
    st.header("Research Setup")
    symbol=st.text_input("Symbol","AAPL").strip().upper()
    start=st.date_input("Start",pd.Timestamp(config.DEFAULT_START_DATE).date())
    end=st.date_input("End",pd.Timestamp(config.DEFAULT_END_DATE).date())
    capital=st.number_input("Initial capital",1000.0,10_000_000.0,float(config.DEFAULT_INITIAL_CAPITAL),step=1000.0)
    commission=st.number_input("Commission",0.0,0.05,config.DEFAULT_COMMISSION,step=0.0001,format="%.4f")
    slippage=st.number_input("Slippage",0.0,0.05,config.DEFAULT_SLIPPAGE,step=0.0001,format="%.4f")
    position_size=st.slider("Position size (% equity)",1,100,100)/100
    execution=st.selectbox("Execution",["next_open","next_close","same_close"],format_func=lambda x:{"next_open":"Next Open (recommended)","next_close":"Next Close","same_close":"Same Close (idealized)"}[x])
    benchmark=st.text_input("Benchmark",config.DEFAULT_BENCHMARK).strip().upper()
    strategy_name=st.selectbox("Strategy",["MA Crossover","RSI Strategy","MACD Strategy","Bollinger Bands","Mean Reversion"])
    if strategy_name=="MA Crossover":
        a=st.slider("Fast MA",2,150,50); b=st.slider("Slow MA",10,400,200); strategy=MovingAverageCrossover(a,b)
    elif strategy_name=="RSI Strategy":
        p=st.slider("RSI period",5,50,14); ob=st.slider("Overbought",55,95,70); os_=st.slider("Oversold",5,45,30); strategy=RSIStrategy(p,ob,os_)
    elif strategy_name=="MACD Strategy":
        f=st.slider("Fast",2,30,12); s=st.slider("Slow",5,60,26); sig=st.slider("Signal",2,30,9); strategy=MACDStrategy(f,s,sig)
    elif strategy_name=="Bollinger Bands":
        p=st.slider("Period",5,100,20); ns=st.slider("Std dev",0.5,4.0,2.0,0.1); strategy=BollingerBandsStrategy(p,ns)
    else:
        lb=st.slider("Lookback",5,100,20); ent=st.slider("Entry z-score",0.5,4.0,2.0,0.1); ex=st.slider("Exit z-score",0.0,2.0,0.5,0.1); strategy=MeanReversionStrategy(lb,ent,ex)
    force=st.checkbox("Force refresh market data")
    run=st.button("Run Research",type="primary",use_container_width=True)

if "result" not in st.session_state: st.session_state.result=None
if run:
    try:
        fetcher=DataFetcher(); data=fetcher.fetch_data(symbol,str(start),str(end),force_refresh=force)
        bt=Backtester(symbol,str(start),str(end),capital,commission,slippage,execution,position_size,benchmark,data,fetcher.last_source)
        result=bt.run(strategy); st.session_state.result=(result,data,fetcher.last_quality,fetcher.last_source)
    except Exception as e:
        st.error(str(e)); st.stop()

if st.session_state.result is None:
    st.info("Configure a research run in the sidebar and click Run Research.")
    st.markdown("### Current focus")
    st.write("Reliable data, explicit execution assumptions, realistic costs, technical indicators, historical signal analysis, portfolio calculations, risk statistics, news context and interactive visualizations. There is no AI layer in this version.")
    st.stop()

result,data,report,source=st.session_state.result
m=result.metrics
enriched=result.signals

tabs=st.tabs(["Overview","Technical","Historical Signals","Risk","Trades","Portfolio","News","Data Quality"])
with tabs[0]:
    c=st.columns(6)
    for col,label,value in zip(c,["Return","CAGR","Sharpe","Sortino","Max Drawdown","Trades"],[f"{m.total_return:.2f}%",f"{m.annualized_return:.2f}%",f"{m.sharpe_ratio:.2f}",f"{m.sortino_ratio:.2f}",f"{m.max_drawdown:.2f}%",str(m.num_trades)]): col.metric(label,value)
    st.plotly_chart(charts.equity_chart(result.equity_curve,data.Close,f"{strategy.name}: Strategy vs {benchmark}"),use_container_width=True)
    st.plotly_chart(charts.drawdown_chart(result.equity_curve),use_container_width=True)
    st.plotly_chart(charts.monthly_heatmap(result.equity_curve),use_container_width=True)
    st.subheader("Research assumptions")
    st.json({"symbol":symbol,"strategy":strategy.name,"parameters":strategy.params,"execution":execution,"initial_capital":capital,"commission":commission,"slippage":slippage,"position_size":position_size,"benchmark":benchmark,"data_source":source})
with tabs[1]:
    st.plotly_chart(charts.price_chart(enriched),use_container_width=True)
    st.dataframe(enriched.tail(150),use_container_width=True)
with tabs[2]:
    st.info("Historical signal analysis describes what happened after similar conditions in this dataset. It is not a forecast or investment recommendation.")
    condition=technical_condition_table(enriched,strategy.name)
    stats=historical_forward_returns(enriched,condition)
    st.metric("Matching historical observations",int(condition.sum()))
    st.dataframe(stats,use_container_width=True)
    st.bar_chart(stats.set_index("horizon_days")["average_return_pct"])
with tabs[3]:
    a,b,c,d=st.columns(4); a.metric("Volatility",f"{m.volatility:.2f}%"); b.metric("Calmar",f"{m.calmar_ratio:.2f}"); c.metric("DD duration",f"{m.max_drawdown_duration} days"); d.metric("Worst trade",f"${m.worst_trade:,.2f}")
    st.plotly_chart(charts.rolling_chart(result.equity_curve),use_container_width=True)
with tabs[4]:
    a,b,c=st.columns(3); a.metric("Win rate",f"{m.win_rate:.1f}%"); b.metric("Profit factor",("∞" if m.profit_factor==float("inf") else f"{m.profit_factor:.2f}")); c.metric("Avg holding",f"{m.avg_holding_days:.1f} days")
    st.plotly_chart(charts.trade_distribution(result.trades),use_container_width=True)
    st.dataframe(result.trades,use_container_width=True)
    st.download_button("Download trade CSV",result.trades.to_csv(index=False),f"{symbol}_trades.csv","text/csv")
with tabs[5]:
    st.subheader("Simple fixed-weight portfolio analysis")
    tickers=st.text_input("Tickers",f"{symbol},MSFT,SPY").upper().replace(" ","").split(",")
    weights_text=st.text_input("Weights (%)", "50,25,25")
    if st.button("Analyze Portfolio"):
        try:
            weights=[float(x)/100 for x in weights_text.split(",")]
            if len(weights)!=len(tickers) or abs(sum(weights)-1)>0.001: raise ValueError("Weights must match tickers and sum to 100%.")
            pf=DataFetcher(); price_map={t:pf.fetch_data(t,str(start),str(end))["Close"] for t in tickers}; aligned,norm,equity=build_portfolio(price_map,dict(zip(tickers,weights))); ps=portfolio_stats(equity)
            cols=st.columns(4); cols[0].metric("Return",f"{ps['total_return_pct']:.2f}%"); cols[1].metric("Volatility",f"{ps['annualized_volatility_pct']:.2f}%"); cols[2].metric("Sharpe",f"{ps['sharpe']:.2f}"); cols[3].metric("Drawdown",f"{ps['max_drawdown_pct']:.2f}%")
            st.line_chart(equity)
            st.dataframe(norm.tail(100),use_container_width=True)
        except Exception as e: st.error(str(e))
with tabs[6]:
    st.caption("News is contextual market information. No AI-generated summaries or recommendations are used.")
    try:
        news=NewsFetcher().search(symbol,20)
        if news.empty: st.info("No public RSS results returned.")
        for _,row in news.iterrows():
            st.markdown(f"**{row.title}**  \n{row.published}  \n{row.summary[:500]}  \n[Source]({row.link})")
    except Exception as e: st.warning(f"News unavailable: {e}")
with tabs[7]:
    st.metric("Status",report.status)
    st.write({"rows":report.rows,"coverage":f"{report.start} to {report.end}","missing_values":report.missing_values,"duplicate_dates":report.duplicate_dates,"suspicious_returns":report.suspicious_returns,"source":source})
    for x in report.errors: st.error(x)
    for x in report.warnings: st.warning(x)
