"""Main backtesting engine."""

import pandas as pd
import logging
from typing import Optional

from data import DataFetcher
from strategies.base_strategy import BaseStrategy, BuyAndHoldStrategy
from .portfolio import Portfolio
from .metrics import PerformanceMetrics
import config

logger = logging.getLogger(__name__)


class Backtester:
    """Runs backtests."""
    
    def __init__(self, symbol, start_date, end_date, 
                 initial_capital=config.DEFAULT_INITIAL_CAPITAL,
                 commission=config.DEFAULT_COMMISSION,
                 slippage=config.DEFAULT_SLIPPAGE):
        
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # Fetch data once
        self.data_fetcher = DataFetcher()
        self.data = self.data_fetcher.fetch_data(symbol, start_date, end_date)
        
        self.strategy_results = None
        self.benchmark_results = None
        
        logger.info(f"Ready: {symbol} | {len(self.data)} bars")
    
    def run(self, strategy):
        """Run a backtest with the given strategy."""
        logger.info(f"Running {strategy.name}")
        
        # Fresh portfolio
        portfolio = Portfolio(
            initial_capital=self.initial_capital,
            commission=self.commission,
            slippage=self.slippage
        )
        
        # Get signals
        df = strategy.generate_signals(self.data)
        
        # Main loop
        for date, row in df.iterrows():
            price = float(row['Close'])
            signal = int(row.get('signal', 0))
            
            portfolio.execute_trade(date, price, signal)
            portfolio.update_equity_curve(date, price)
        
        # Close any open position
        if portfolio.shares > 0:
            last_date = df.index[-1]
            last_price = float(df['Close'].iloc[-1])
            portfolio._sell(last_date, last_price)
        
        # Calculate metrics
        equity_curve = portfolio.get_equity_curve_df()
        trades = portfolio.get_trades_df()
        
        metrics = PerformanceMetrics(
            equity_curve=equity_curve,
            trades=trades,
            benchmark=self.data['Close'],
            initial_capital=self.initial_capital
        )
        
        self.strategy_results = metrics
        logger.info(f"Done. Return: {metrics.total_return:.2f}% | Trades: {metrics.num_trades}")
        
        return metrics
    
    def run_benchmark(self):
        """Run buy-and-hold for comparison."""
        self.benchmark_results = self.run(BuyAndHoldStrategy())
        return self.benchmark_results
