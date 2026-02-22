"""
Trading Backtester - Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

import config
from data import DataFetcher
from strategies import (
    MovingAverageCrossover, RSIStrategy, MACDStrategy,
    BollingerBandsStrategy, MeanReversionStrategy
)
from backtester import Backtester
from visualization import charts

# Page setup
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide"
)

# Title
st.markdown(f'<h1 style="text-align: center;">{config.APP_ICON} {config.APP_TITLE}</h1>', 
            unsafe_allow_html=True)
st.markdown("### Test trading strategies on historical data")

# Sidebar config
st.sidebar.header("Configuration")

symbol = st.sidebar.text_input("Symbol", "AAPL").upper()

col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start", pd.to_datetime(config.DEFAULT_START_DATE))
end_date = col2.date_input("End", pd.to_datetime(config.DEFAULT_END_DATE))

capital = st.sidebar.number_input(
    "Initial Capital ($)",
    min_value=1000,
    max_value=1000000,
    value=int(config.DEFAULT_INITIAL_CAPITAL),
    step=1000
)

# Strategy selection
st.sidebar.header("Strategy")
strategy_type = st.sidebar.selectbox(
    "Choose Strategy",
    ["Moving Average Crossover", "RSI Strategy", "MACD Strategy", 
     "Bollinger Bands", "Mean Reversion"]
)

st.sidebar.subheader("Parameters")

# Build strategy based on selection
if strategy_type == "Moving Average Crossover":
    short = st.sidebar.slider("Short MA", 10, 100, 50)
    long = st.sidebar.slider("Long MA", 100, 300, 200)
    strategy = MovingAverageCrossover(short_window=short, long_window=long)

elif strategy_type == "RSI Strategy":
    period = st.sidebar.slider("Period", 5, 30, 14)
    overbought = st.sidebar.slider("Overbought", 60, 90, 70)
    oversold = st.sidebar.slider("Oversold", 10, 40, 30)
    strategy = RSIStrategy(period=period, overbought=overbought, oversold=oversold)

elif strategy_type == "MACD Strategy":
    fast = st.sidebar.slider("Fast", 5, 20, 12)
    slow = st.sidebar.slider("Slow", 20, 40, 26)
    signal = st.sidebar.slider("Signal", 5, 15, 9)
    strategy = MACDStrategy(fast_period=fast, slow_period=slow, signal_period=signal)

elif strategy_type == "Bollinger Bands":
    period = st.sidebar.slider("Period", 10, 50, 20)
    std = st.sidebar.slider("Std Dev", 1.0, 3.0, 2.0, 0.5)
    strategy = BollingerBandsStrategy(period=period, num_std=std)

else:  # Mean Reversion
    lookback = st.sidebar.slider("Lookback", 10, 50, 20)
    threshold = st.sidebar.slider("Threshold", 1.0, 3.0, 2.0, 0.1)
    strategy = MeanReversionStrategy(lookback_period=lookback, entry_threshold=threshold)

# Run button
run = st.sidebar.button("Run Backtest", type="primary", use_container_width=True)

st.sidebar.info("Using demo data (Yahoo Finance has been unreliable lately)")

# Main area
if run:
    with st.spinner(f"Running backtest for {symbol}..."):
        try:
            # Run backtest
            bt = Backtester(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                initial_capital=capital
            )
            
            results = bt.run(strategy)
            
            st.success(f"Backtest complete for {symbol}")
            
            # Top metrics
            st.header("Performance")
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Total Return", f"{results.total_return:.2f}%")
            col2.metric("Sharpe Ratio", f"{results.sharpe_ratio:.2f}")
            col3.metric("Max Drawdown", f"{results.max_drawdown:.2f}%")
            col4.metric("Win Rate", f"{results.win_rate:.1f}%")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Trades", results.num_trades)
            col2.metric("Annual Return", f"{results.annualized_return:.2f}%")
            col3.metric("Profit Factor", f"{results.profit_factor:.2f}")
            
            # Charts
            st.header("Charts")
            
            st.subheader("Equity Curve")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=results.equity_curve.index,
                y=results.equity_curve['equity'],
                name='Strategy',
                line=dict(color=config.COLOR_SCHEME['equity'], width=2)
            ))
            
            # Add buy & hold
            benchmark = bt.data['Close']
            norm = (benchmark / benchmark.iloc[0]) * capital
            fig.add_trace(go.Scatter(
                x=norm.index,
                y=norm.values,
                name='Buy & Hold',
                line=dict(color=config.COLOR_SCHEME['benchmark'], width=2, dash='dash')
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Value ($)",
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Drawdown
            st.subheader("Drawdown")
            equity = results.equity_curve['equity']
            cummax = equity.expanding().max()
            dd = (equity - cummax) / cummax * 100
            
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=dd.index,
                y=dd.values,
                fill='tozeroy',
                name='Drawdown',
                line=dict(color=config.COLOR_SCHEME['negative'])
            ))
            fig_dd.update_layout(
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                height=400
            )
            st.plotly_chart(fig_dd, use_container_width=True)
            
            # Trades table
            if not results.trades.empty:
                st.header("Trade Log")
                trades = results.trades.copy()
                trades['entry_date'] = pd.to_datetime(trades['entry_date']).dt.strftime('%Y-%m-%d')
                trades['exit_date'] = pd.to_datetime(trades['exit_date']).dt.strftime('%Y-%m-%d')
                st.dataframe(trades, use_container_width=True)
                
                csv = trades.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    f"{symbol}_trades.csv",
                    "text/csv"
                )
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.exception(e)

else:
    # Welcome
    st.info("Configure your backtest in the sidebar and click Run")
    
    st.markdown("""
    ### How to use
    
    1. Enter a stock symbol
    2. Set date range
    3. Choose a strategy
    4. Adjust parameters
    5. Run the backtest
    
    ### Strategies
    - **MA Crossover** - Golden cross/death cross
    - **RSI** - Overbought/oversold
    - **MACD** - Signal line crossovers  
    - **Bollinger Bands** - Mean reversion
    - **Mean Reversion** - Z-score based
    """)

st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>v1.0.0</div>", unsafe_allow_html=True)
