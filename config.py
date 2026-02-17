"""
config.py — settings for the trading backtester
tweak stuff here so you don't have to dig through the source
"""

from datetime import datetime, timedelta

# ── app meta ─────────────────────────────────────────────────────────────────

APP_TITLE = "Algorithmic Trading Backtester"
APP_ICON = "📈"
VERSION = "1.0.0"

# ── data / caching ────────────────────────────────────────────────────────────

DATABASE_PATH = "trading_data.db"
CACHE_EXPIRY_DAYS = 7  # bump this if you're hammering the API too much

# default date range shown on load (roughly 4 years back)
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365 * 4)).strftime("%Y-%m-%d")
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")

# symbols in the quick-pick dropdown
POPULAR_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "META", "NVDA", "JPM", "V", "SPY", "QQQ",
]

# ── trading defaults ──────────────────────────────────────────────────────────

DEFAULT_INITIAL_CAPITAL = 10_000.0
DEFAULT_COMMISSION  = 0.001   # 0.1% per trade
DEFAULT_SLIPPAGE    = 0.0005  # 0.05% — keeps things realistic
DEFAULT_POSITION_SIZE = 1.0   # fraction of capital; 1.0 = go all in

# ── risk ──────────────────────────────────────────────────────────────────────

RISK_FREE_RATE = 0.04  # 4% annualised, used for Sharpe calculation

# ── strategy parameters ───────────────────────────────────────────────────────
# these are just the defaults; the UI lets you override everything

STRATEGY_PARAMS = {
    "ma_crossover": {
        "short_window": 50,
        "long_window": 200,   # classic golden / death cross
    },
    "rsi": {
        "period": 14,
        "overbought": 70,
        "oversold": 30,
    },
    "macd": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9,
    },
    "bollinger_bands": {
        "period": 20,
        "num_std": 2.0,
    },
    "mean_reversion": {
        "lookback_period": 20,
        "entry_threshold": 2.0,  # z-score to enter
        "exit_threshold": 0.5,   # z-score to exit (back toward mean)
    },
}

# ── colours ───────────────────────────────────────────────────────────────────

COLOR_SCHEME = {
    "positive":   "#06D6A0",
    "negative":   "#EF476F",
    "neutral":    "#2E86AB",
    "buy_signal": "#06D6A0",
    "sell_signal":"#EF476F",
    "equity":     "#667eea",
    "benchmark":  "#764ba2",
}

# ── charts ────────────────────────────────────────────────────────────────────

CHART_HEIGHT   = 500
CHART_TEMPLATE = "plotly_white"

# ── logging ───────────────────────────────────────────────────────────────────

LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s  %(name)s  %(levelname)s  %(message)s"