"""
Performance metrics - FIXED to accept initial_capital parameter.
"""

import pandas as pd
import numpy as np
from typing import Optional
import config


class PerformanceMetrics:
    """Calculates all performance metrics for a backtest."""

    def __init__(
        self,
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame,
        benchmark: Optional[pd.Series] = None,
        initial_capital: float = config.DEFAULT_INITIAL_CAPITAL,
        risk_free_rate: float = config.RISK_FREE_RATE
    ):
        self.equity_curve = equity_curve
        self.trades = trades
        self.benchmark = benchmark
        self.initial_capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self._calculate_metrics()

    def _calculate_metrics(self):
        self.total_return = self._total_return()
        self.annualized_return = self._annualized_return()
        self.volatility = self._volatility()
        self.sharpe_ratio = self._sharpe()
        self.max_drawdown = self._max_drawdown()
        self.max_drawdown_duration = self._max_dd_duration()
        self.num_trades = len(self.trades) if not self.trades.empty else 0
        self.win_rate = self._win_rate()
        self.profit_factor = self._profit_factor()
        self.avg_trade_return = self._avg_trade_return()

    def _total_return(self) -> float:
        if self.equity_curve.empty or len(self.equity_curve) < 2:
            return 0.0
        initial = self.equity_curve['equity'].iloc[0]
        final = self.equity_curve['equity'].iloc[-1]
        return ((final - initial) / initial) * 100 if initial > 0 else 0.0

    def _annualized_return(self) -> float:
        if self.equity_curve.empty or len(self.equity_curve) < 2:
            return 0.0
        days = (self.equity_curve.index[-1] - self.equity_curve.index[0]).days
        years = days / 365.25
        if years <= 0:
            return 0.0
        initial = self.equity_curve['equity'].iloc[0]
        final = self.equity_curve['equity'].iloc[-1]
        if initial <= 0:
            return 0.0
        return ((final / initial) ** (1 / years) - 1) * 100

    def _volatility(self) -> float:
        if self.equity_curve.empty or len(self.equity_curve) < 2:
            return 0.0
        returns = self.equity_curve['equity'].pct_change().dropna()
        return float(returns.std() * np.sqrt(252) * 100)

    def _sharpe(self) -> float:
        if self.equity_curve.empty or len(self.equity_curve) < 2:
            return 0.0
        returns = self.equity_curve['equity'].pct_change().dropna()
        if returns.std() == 0:
            return 0.0
        daily_rf = (1 + self.risk_free_rate) ** (1 / 252) - 1
        excess = returns - daily_rf
        return float((excess.mean() / returns.std()) * np.sqrt(252))

    def _max_drawdown(self) -> float:
        if self.equity_curve.empty:
            return 0.0
        equity = self.equity_curve['equity']
        cummax = equity.expanding().max()
        dd = (equity - cummax) / cummax * 100
        return float(dd.min())

    def _max_dd_duration(self) -> int:
        if self.equity_curve.empty:
            return 0
        equity = self.equity_curve['equity']
        cummax = equity.expanding().max()
        in_dd = equity < cummax
        if not in_dd.any():
            return 0
        periods = []
        start = None
        for i, v in enumerate(in_dd):
            if v and start is None:
                start = i
            elif not v and start is not None:
                periods.append(i - start)
                start = None
        if start is not None:
            periods.append(len(in_dd) - start)
        return max(periods) if periods else 0

    def _win_rate(self) -> float:
        if self.trades.empty:
            return 0.0
        return float((self.trades['pnl'] > 0).sum() / len(self.trades) * 100)

    def _profit_factor(self) -> float:
        if self.trades.empty:
            return 0.0
        gross_profit = self.trades[self.trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(self.trades[self.trades['pnl'] < 0]['pnl'].sum())
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return float(gross_profit / gross_loss)

    def _avg_trade_return(self) -> float:
        if self.trades.empty or 'return_pct' not in self.trades.columns:
            return 0.0
        return float(self.trades['return_pct'].mean())

    def summary(self) -> dict:
        return {
            'Total Return (%)': round(self.total_return, 2),
            'Annualized Return (%)': round(self.annualized_return, 2),
            'Volatility (%)': round(self.volatility, 2),
            'Sharpe Ratio': round(self.sharpe_ratio, 2),
            'Max Drawdown (%)': round(self.max_drawdown, 2),
            'Max DD Duration (days)': self.max_drawdown_duration,
            'Number of Trades': self.num_trades,
            'Win Rate (%)': round(self.win_rate, 2),
            'Profit Factor': round(self.profit_factor, 2),
            'Avg Trade Return (%)': round(self.avg_trade_return, 2),
        }
