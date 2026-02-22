"""
Global configuration
"""

from datetime import datetime, timedelta

# App info
APP_TITLE = "Trading Backtester"
APP_ICON = "📈"
VERSION = "1.0.0"

# Database
DATABASE_PATH = "trading_data.db"
CACHE_EXPIRY_DAYS = 7

# Default date range (last 4 years)
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365*4)).strftime('%Y-%m-%d')
DEFAULT_END_DATE = datetime.now().strftime('%Y-%m-%d')

# Common symbols
POPULAR_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'SPY', 'QQQ'
]

# Trading defaults
DEFAULT_INITIAL_CAPITAL = 10000.0
DEFAULT_COMMISSION = 0.001  # 0.1%
DEFAULT_SLIPPAGE = 0.0005   # 0.05%
DEFAULT_POSITION_SIZE = 1.0

# For Sharpe ratio calculation
RISK_FREE_RATE = 0.04  # 4% annual

# Strategy defaults
STRATEGY_PARAMS = {
    'ma_crossover': {'short_window': 50, 'long_window': 200},
    'rsi': {'period': 14, 'overbought': 70, 'oversold': 30},
    'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
    'bollinger_bands': {'period': 20, 'num_std': 2.0},
    'mean_reversion': {'lookback_period': 20, 'entry_threshold': 2.0, 'exit_threshold': 0.5}
}

# UI colors
COLOR_SCHEME = {
    'positive': '#06D6A0',
    'negative': '#EF476F',
    'neutral': '#2E86AB',
    'buy_signal': '#06D6A0',
    'sell_signal': '#EF476F',
    'equity': '#667eea',
    'benchmark': '#764ba2',
}

# Chart settings
CHART_HEIGHT = 500
CHART_TEMPLATE = "plotly_white"

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
