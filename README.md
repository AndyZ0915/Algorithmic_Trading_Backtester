# Quant Research Platform

A research-first market analysis and backtesting application built in Python and Streamlit.

The project has deliberately moved away from being a simple "pick a ticker and run a strategy" demo. The focus is now on **correct historical execution, transparent assumptions, data quality, quantitative calculations, and interactive visuals**.

## Current capabilities

- Historical OHLCV data through Yahoo Finance
- Optional free Alpha Vantage provider through `.env`
- SQLite caching
- Explicit data source reporting
- OHLCV validation and data-quality diagnostics
- Next Open, Next Close, and Same Close execution models
- Commission and slippage
- Configurable position sizing
- Moving-average crossover
- RSI
- MACD
- Bollinger Bands
- Stateful z-score mean reversion
- Equity curves and benchmark comparison
- Drawdown analysis
- Monthly return heatmap
- Rolling volatility and Sharpe analysis
- Trade distribution
- Sharpe, Sortino, Calmar, CAGR, volatility, drawdown, win rate, profit factor, expectancy-related trade statistics
- Trade CSV export
- Market-news context through public RSS search

## Important methodology choice

Signals are generated from information available on a bar and are normally executed on the **next bar**. Same-close execution is available only as an explicitly labeled idealized assumption.

The application does **not** silently replace unavailable market data with synthetic prices. If live providers fail, it reports the problem so the research result is not accidentally mistaken for a real market-data backtest.

## Free setup

Python 3.11+ is recommended.

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

An Alpha Vantage key is optional. If you have one, put it in `.env`:

```text
ALPHA_VANTAGE_API_KEY=your_key_here
```

Never commit `.env`.

## Design direction

The eventual product can grow toward a clean retail-investing-style research experience with dashboards, watchlists, company pages, portfolio analytics, richer news analysis, and strategy comparison. The current version intentionally avoids AI assistants, LLMs, live trading, and paid data dependencies. The goal is to make the calculations and research foundation correct first.

## Project structure

```text
app.py
config.py
data/
  data_fetcher.py
  data_quality.py
  database.py
  news.py
strategies/
  base_strategy.py
  ma_crossover.py
  rsi_strategy.py
  macd_strategy.py
  bollinger_bands.py
  mean_reversion.py
backtester/
  engine.py
  portfolio.py
  metrics.py
visualization/
  charts.py
tests/
  test_engine.py
```
