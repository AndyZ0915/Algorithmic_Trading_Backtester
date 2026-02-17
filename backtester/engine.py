"""
Backtesting engine - FIXED VERSION
Uses _close_long() (not _close_long_position which was renamed)
"""

import pandas as pd
import logging
from typing import Optional

from data import DataFetcher
from strategies.base_strategy import BaseStrategy, BuyAndHoldStrategy
from .portfolio import Portfolio
from .metrics import PerformanceMetrics
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Backtester:
    """Main backtesting engine."""

    def __init__(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_capital: float = config.DEFAULT_INITIAL_CAPITAL,
        commission: float = config.DEFAULT_COMMISSION,
        slippage: float = config.DEFAULT_SLIPPAGE
    ):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

        self.data_fetcher = DataFetcher()
        self.data = self.data_fetcher.fetch_data(symbol, start_date, end_date)

        self.strategy_results: Optional[PerformanceMetrics] = None
        self.benchmark_results: Optional[PerformanceMetrics] = None

        logger.info(f"Backtester ready: {symbol} | {len(self.data)} bars")

    def run(self, strategy: BaseStrategy) -> PerformanceMetrics:
        logger.info(f"Running: {strategy.name}")

        # Fresh portfolio every run
        portfolio = Portfolio(
            initial_capital=self.initial_capital,
            commission=self.commission,
            slippage=self.slippage
        )

        df = strategy.generate_signals(self.data)

        for date, row in df.iterrows():
            price = float(row['Close'])
            signal = int(row.get('signal', 0))
            portfolio.execute_trade(date, price, signal)
            portfolio.update_equity_curve(date, price)

        # Close any open position at end
        if portfolio.position > 0:
            last_date = df.index[-1]
            last_price = float(df['Close'].iloc[-1])
            portfolio._close_long(last_date, last_price)

        equity_curve = portfolio.get_equity_curve_df()
        trades_df = portfolio.get_trades_df()

        metrics = PerformanceMetrics(
            equity_curve=equity_curve,
            trades=trades_df,
            benchmark=self.data['Close'],
            initial_capital=self.initial_capital
        )

        self.strategy_results = metrics
        logger.info(f"Done. Return: {metrics.total_return:.2f}% | Trades: {metrics.num_trades}")
        return metrics

    def run_benchmark(self) -> PerformanceMetrics:
        self.benchmark_results = self.run(BuyAndHoldStrategy())
        return self.benchmark_results

    def compare_to_benchmark(self) -> pd.DataFrame:
        if self.benchmark_results is None:
            self.run_benchmark()
        if self.strategy_results is None:
            raise ValueError("Run strategy backtest first.")
        s = self.strategy_results
        b = self.benchmark_results
        return pd.DataFrame({
            'Strategy': [f"{s.total_return:.2f}%", f"{s.annualized_return:.2f}%",
                         f"{s.sharpe_ratio:.2f}", f"{s.max_drawdown:.2f}%",
                         f"{s.win_rate:.1f}%", s.num_trades],
            'Buy & Hold': [f"{b.total_return:.2f}%", f"{b.annualized_return:.2f}%",
                           f"{b.sharpe_ratio:.2f}", f"{b.max_drawdown:.2f}%",
                           "100.0%", 1]
        }, index=['Total Return', 'Annualized Return', 'Sharpe Ratio',
                  'Max Drawdown', 'Win Rate', 'Num Trades'])