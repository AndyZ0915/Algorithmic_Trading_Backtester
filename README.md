# Algorithmic Trading Backtester

I built this because I wanted to actually understand whether trading strategies work — not just read about them, but test them myself with real data and see the numbers.

This is a full web app that lets you pick a stock, pick a strategy, and run a backtest to see how it would have performed historically. It tracks your portfolio value over time, calculates proper risk metrics, and shows everything in interactive charts. You can tweak the strategy parameters with sliders and see immediately how the results change.

It started as a script, turned into a mess, and then I rebuilt it properly with a modular architecture I'm actually proud of.

---

## What it does

You select a stock (AAPL, MSFT, SPY, whatever), a date range, and one of 5 strategies:

- **Moving Average Crossover** — buys on golden crosses, sells on death crosses
- **RSI** — trades overbought/oversold conditions
- **MACD** — signal line crossovers
- **Bollinger Bands** — mean reversion on band touches
- **Mean Reversion** — z-score based entries and exits

The backtester runs through every trading day, executes trades based on signals, and tracks your portfolio with realistic commission (0.1%) and slippage (0.05%) so the results aren't artificially inflated.

At the end you get:

- Equity curve vs buy-and-hold benchmark
- Drawdown analysis
- Sharpe ratio, max drawdown, win rate, profit factor, and more
- A full trade-by-trade log you can download as CSV

---

## Challenges I ran into

**Yahoo Finance blocking requests** — this was the most frustrating part. Yahoo Finance started blocking programmatic requests without warning, which broke the entire data layer. Rather than fight it, I built a demo data generator that creates realistic simulated price data using geometric Brownian motion. The app now tries Yahoo Finance first, and falls back to demo data automatically. You barely notice the difference for testing purposes.

**Python version compatibility** — newer versions of Python (3.13+) broke some dependencies. Documented the exact version requirements so this doesn't bite anyone else.

**Architecture creep** — the project started as a single main.py and grew unwieldy fast. I refactored into a proper layered architecture: data fetching, strategy logic, backtesting engine, and visualization are all completely separate. Adding a new strategy now takes about 20 lines of code.

**The off-by-one bug** — the equity curve and date tracking lists were initialized differently (one started with an initial value, one started empty), which caused a crash whenever you actually ran a backtest. Classic.

---

## Tech stack

- **Streamlit** for the web UI — great for this kind of data app
- **pandas / NumPy** for all the data processing and calculations
- **Plotly** for interactive charts
- **yfinance** for market data (with the demo fallback)
- **SQLite** to cache data so you're not hammering the API on every run
- **Python 3.11**

---

## How to run it

```bash
# Install dependencies
pip install streamlit pandas numpy plotly yfinance scipy sqlalchemy

# Run the app
streamlit run app.py
```

Opens at http://localhost:8501. Pick a symbol, pick a strategy, hit Run Backtest.

---

## Project structure

```
trading_backtester/
├── app.py                  # Streamlit entry point
├── config.py               # All parameters in one place
├── data/
│   ├── data_fetcher.py     # Yahoo Finance + demo data fallback
│   └── database.py         # SQLite caching
├── strategies/
│   ├── base_strategy.py    # Abstract base class
│   ├── ma_crossover.py
│   ├── rsi_strategy.py
│   ├── macd_strategy.py
│   ├── bollinger_bands.py
│   └── mean_reversion.py
├── backtester/
│   ├── engine.py           # Main loop
│   ├── portfolio.py        # Position and cash tracking
│   └── metrics.py          # Sharpe, drawdown, win rate, etc.
└── visualization/
    └── charts.py           # Plotly charts
```

---

## What I learned

Building this taught me more about quantitative finance than any tutorial I've read. A few things that stuck:

- Sharpe ratio matters more than raw return — a 30% return with huge volatility is worse than a 15% return you can actually sleep through
- Transaction costs destroy strategies that trade frequently — commission and slippage add up fast
- Most strategies underperform buy-and-hold most of the time, which is a humbling but important thing to see with your own data
- Good software architecture pays off immediately when you're iterating — swapping out strategies or adding new metrics is painless with clean separation of concerns

---

## What's next

- Walk-forward optimization (test on out-of-sample data to avoid overfitting)
- Multi-symbol portfolio backtesting
- Adding more strategies (momentum, pairs trading)
- Connecting a real data provider once the Yahoo Finance situation stabilizes

---

If you clone this and run into issues, open an issue. Happy to help.
