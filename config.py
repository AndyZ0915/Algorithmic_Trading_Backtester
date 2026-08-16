"""Application defaults and user-configurable research assumptions."""
from datetime import datetime, timedelta

APP_TITLE = "Quant Research Platform"
APP_ICON = "QR"
VERSION = "3.0.0"
DATABASE_PATH = "quant_research.db"
CACHE_EXPIRY_DAYS = 7
DEFAULT_START_DATE = (datetime.now() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
DEFAULT_END_DATE = datetime.now().strftime("%Y-%m-%d")
DEFAULT_INITIAL_CAPITAL = 10_000.0
DEFAULT_COMMISSION = 0.001
DEFAULT_SLIPPAGE = 0.0005
DEFAULT_POSITION_SIZE = 1.0
RISK_FREE_RATE = 0.04
DEFAULT_BENCHMARK = "SPY"
ALPHA_VANTAGE_API_KEY_ENV = "ALPHA_VANTAGE_API_KEY"
POPULAR_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "SPY", "QQQ"]
CHART_TEMPLATE = "plotly_white"
