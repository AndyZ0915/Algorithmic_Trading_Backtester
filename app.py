"""
Algorithmic Trading Backtester - Main Streamlit Application
PRODUCTION VERSION - Complete with all features
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import sys

# Import project modules
import config
from data import DataFetcher
from strategies import (
    MovingAverageCrossover, RSIStrategy, MACDStrategy,
    BollingerBandsStrategy, MeanReversionStrategy
)
from backtester import Backtester
from visualization import charts

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #2E86AB; text-align: center; margin-bottom: 1rem;}
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white;}
    .stButton>button {width: 100%; background-color: #2E86AB; color: white;}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown(f'<h1 class="main-header">{config.APP_ICON} {config.APP_TITLE}</h1>', unsafe_allow_html=True)
st.markdown("### Professional backtesting platform for algorithmic trading strategies")

# Sidebar Configuration
st.sidebar.header("⚙️ Backtest Configuration")

# Symbol input
symbol = st.sidebar.text_input(
    "Stock Symbol",
    "AAPL",
    help="Enter ticker symbol (e.g., AAPL, MSFT, SPY)"
).upper()

# Date range
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", pd.to_datetime(config.DEFAULT_START_DATE))
end_date = col2.date_input("End Date", pd.to_datetime(config.DEFAULT_END_DATE))

# Capital
initial_capital = st.sidebar.number_input(
    "Initial Capital ($)",
    min_value=1000,
    max_value=1000000,
    value=int(config.DEFAULT_INITIAL_CAPITAL),
    step=1000
)

# Strategy Selection
st.sidebar.header("📊 Strategy")
strategy_type = st.sidebar.selectbox(
    "Select Strategy",
    ["Moving Average Crossover", "RSI Strategy", "MACD Strategy", 
     "Bollinger Bands", "Mean Reversion"]
)

# Strategy Parameters
st.sidebar.subheader("Parameters")

if strategy_type == "Moving Average Crossover":
    short_ma = st.sidebar.slider("Short MA", 10, 100, 50)
    long_ma = st.sidebar.slider("Long MA", 100, 300, 200)
    strategy = MovingAverageCrossover(short_window=short_ma, long_window=long_ma)

elif strategy_type == "RSI Strategy":
    rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
    overbought = st.sidebar.slider("Overbought", 60, 90, 70)
    oversold = st.sidebar.slider("Oversold", 10, 40, 30)
    strategy = RSIStrategy(period=rsi_period, overbought=overbought, oversold=oversold)

elif strategy_type == "MACD Strategy":
    fast = st.sidebar.slider("Fast Period", 5, 20, 12)
    slow = st.sidebar.slider("Slow Period", 20, 40, 26)
    signal = st.sidebar.slider("Signal Period", 5, 15, 9)
    strategy = MACDStrategy(fast_period=fast, slow_period=slow, signal_period=signal)

elif strategy_type == "Bollinger Bands":
    bb_period = st.sidebar.slider("Period", 10, 50, 20)
    num_std = st.sidebar.slider("Std Dev", 1.0, 3.0, 2.0, 0.5)
    strategy = BollingerBandsStrategy(period=bb_period, num_std=num_std)

else:  # Mean Reversion
    lookback = st.sidebar.slider("Lookback", 10, 50, 20)
    threshold = st.sidebar.slider("Entry Threshold", 1.0, 3.0, 2.0, 0.1)
    strategy = MeanReversionStrategy(lookback_period=lookback, entry_threshold=threshold)

# Run button
run_btn = st.sidebar.button("🚀 Run Backtest", type="primary", use_container_width=True)

# Info
st.sidebar.info("💡 Using demo data mode for reliability. Results are simulated but realistic.")

# Main content
if run_btn:
    with st.spinner(f"Running backtest for {symbol}..."):
        try:
            # Run backtest
            backtester = Backtester(
                symbol=symbol,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                initial_capital=initial_capital
            )
            
            results = backtester.run(strategy)
            
            st.success(f"✅ Backtest completed for {symbol}!")
            
            # Metrics
            st.header("📊 Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Total Return", f"{results.total_return:.2f}%", delta=f"{results.total_return:.2f}%")
            col2.metric("Sharpe Ratio", f"{results.sharpe_ratio:.2f}")
            col3.metric("Max Drawdown", f"{results.max_drawdown:.2f}%", delta=f"{results.max_drawdown:.2f}%", delta_color="inverse")
            col4.metric("Win Rate", f"{results.win_rate:.1f}%")
            
            # More metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Trades", results.num_trades)
            col2.metric("Annual Return", f"{results.annualized_return:.2f}%")
            col3.metric("Profit Factor", f"{results.profit_factor:.2f}")
            
            # Charts
            st.header("📈 Performance Charts")
            
            # Equity curve
            st.subheader("Equity Curve")
            fig_equity = go.Figure()
            fig_equity.add_trace(go.Scatter(
                x=results.equity_curve.index,
                y=results.equity_curve['equity'],
                name='Strategy',
                line=dict(color=config.COLOR_SCHEME['equity'], width=2)
            ))
            
            benchmark = backtester.data['Close']
            norm_benchmark = (benchmark / benchmark.iloc[0]) * initial_capital
            fig_equity.add_trace(go.Scatter(
                x=norm_benchmark.index,
                y=norm_benchmark.values,
                name='Buy & Hold',
                line=dict(color=config.COLOR_SCHEME['benchmark'], width=2, dash='dash')
            ))
            
            fig_equity.update_layout(
                title=f"{strategy_type} vs Buy & Hold",
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                height=500,
                hovermode='x unified',
                template=config.CHART_TEMPLATE
            )
            st.plotly_chart(fig_equity, use_container_width=True)
            
            # Drawdown
            st.subheader("Drawdown Analysis")
            equity = results.equity_curve['equity']
            cummax = equity.expanding().max()
            drawdown = (equity - cummax) / cummax * 100
            
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown.values,
                fill='tozeroy',
                name='Drawdown',
                line=dict(color=config.COLOR_SCHEME['negative']),
                fillcolor=f"rgba(239, 71, 111, 0.3)"
            ))
            fig_dd.update_layout(
                title="Drawdown Over Time",
                xaxis_title="Date",
                yaxis_title="Drawdown (%)",
                height=400,
                template=config.CHART_TEMPLATE
            )
            st.plotly_chart(fig_dd, use_container_width=True)
            
            # Trade Log
            if not results.trades.empty:
                st.header("💼 Trade History")
                trades_df = results.trades.copy()
                trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date']).dt.strftime('%Y-%m-%d')
                trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date']).dt.strftime('%Y-%m-%d')
                
                st.dataframe(trades_df, use_container_width=True)
                
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"{symbol}_{strategy_type}_trades.csv",
                    "text/csv"
                )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

else:
    # Welcome screen
    st.info("👈 Configure your backtest in the sidebar and click 'Run Backtest'!")
    
    st.markdown("""
    ### 🎯 How to Use
    
    1. **Enter Stock Symbol** - Any ticker (AAPL, MSFT, SPY, etc.)
    2. **Set Date Range** - Choose your backtest period
    3. **Select Strategy** - Pick from 5 professional strategies
    4. **Adjust Parameters** - Fine-tune using sliders
    5. **Run Backtest** - Click button and view results!
    
    ### 📊 Available Strategies
    - Moving Average Crossover
    - RSI Strategy
    - MACD Strategy
    - Bollinger Bands
    - Mean Reversion
    """)
    
    # Sample metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Example Return", "45.2%", "+45.2%")
    col2.metric("Example Sharpe", "1.85")
    col3.metric("Example Drawdown", "-12.3%", "-12.3%")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Built for algorithmic trading education | v1.0.0</div>", unsafe_allow_html=True)
