"""
Portfolio - FIXED VERSION
Root cause fix: equity_curve started with [initial_capital] but dates started empty [].
Now both start empty and are always appended together in update_equity_curve().
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """Represents a completed trade."""
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    shares: float
    direction: str
    pnl: float = 0.0
    return_pct: float = 0.0
    commission: float = 0.0

    def __post_init__(self):
        if self.direction == 'long':
            self.pnl = (self.exit_price - self.entry_price) * self.shares - self.commission
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.shares - self.commission
        cost_basis = self.entry_price * self.shares
        if cost_basis > 0:
            self.return_pct = (self.pnl / cost_basis) * 100


class Portfolio:
    """Manages portfolio positions, cash, and equity tracking."""

    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.commission_rate = commission
        self.slippage_rate = slippage

        self.position: float = 0.0
        self.position_entry_price: float = 0.0
        self.position_entry_date: Optional[datetime] = None

        # FIX: both lists start EMPTY, appended TOGETHER every bar
        self.equity_curve: List[float] = []
        self.dates: List[datetime] = []
        self.trades: List[Trade] = []

        self.total_commission_paid: float = 0.0
        self.total_slippage_cost: float = 0.0

    def get_equity(self, current_price: float) -> float:
        return self.current_capital + (self.position * current_price)

    def update_equity_curve(self, date: datetime, price: float):
        """Call once per bar - always keeps dates and equity_curve same length."""
        self.dates.append(date)
        self.equity_curve.append(self.get_equity(price))

    def execute_trade(self, date: datetime, price: float, signal: int) -> bool:
        if signal == 0:
            return False
        effective_price = price * (1 + self.slippage_rate * np.sign(signal))
        if signal == 1 and self.position == 0:
            return self._open_long(date, effective_price)
        elif signal == -1 and self.position > 0:
            return self._close_long(date, effective_price)
        return False

    def _open_long(self, date: datetime, price: float) -> bool:
        if self.current_capital <= 0:
            return False
        commission = self.current_capital * self.commission_rate
        available = self.current_capital - commission
        if available <= 0:
            return False
        self.position = available / price
        self.position_entry_price = price
        self.position_entry_date = date
        self.current_capital = 0.0
        self.total_commission_paid += commission
        return True

    def _close_long(self, date: datetime, price: float) -> bool:
        if self.position == 0:
            return False
        proceeds = self.position * price
        commission = proceeds * self.commission_rate
        net_proceeds = proceeds - commission
        trade = Trade(
            entry_date=self.position_entry_date,
            exit_date=date,
            entry_price=self.position_entry_price,
            exit_price=price,
            shares=self.position,
            direction='long',
            commission=commission
        )
        self.trades.append(trade)
        self.current_capital = net_proceeds
        self.total_commission_paid += commission
        self.position = 0.0
        self.position_entry_price = 0.0
        self.position_entry_date = None
        return True

    def get_equity_curve_df(self) -> pd.DataFrame:
        """Return equity curve DataFrame - lists always same length so no crash."""
        if not self.dates:
            return pd.DataFrame({'equity': [self.initial_capital]})
        df = pd.DataFrame(
            {'equity': self.equity_curve},
            index=pd.DatetimeIndex(self.dates)
        )
        df.index.name = 'date'
        return df

    def get_trades_df(self) -> pd.DataFrame:
        if not self.trades:
            return pd.DataFrame(columns=[
                'entry_date', 'exit_date', 'entry_price', 'exit_price',
                'shares', 'direction', 'pnl', 'return_pct', 'commission'
            ])
        rows = [{
            'entry_date': t.entry_date,
            'exit_date': t.exit_date,
            'entry_price': round(t.entry_price, 2),
            'exit_price': round(t.exit_price, 2),
            'shares': round(t.shares, 4),
            'direction': t.direction,
            'pnl': round(t.pnl, 2),
            'return_pct': round(t.return_pct, 2),
            'commission': round(t.commission, 2),
        } for t in self.trades]
        return pd.DataFrame(rows)

    def get_summary(self) -> Dict:
        final_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        trades_df = self.get_trades_df()
        num_trades = len(trades_df)
        if num_trades > 0:
            winning = trades_df[trades_df['pnl'] > 0]
            losing = trades_df[trades_df['pnl'] < 0]
            win_rate = len(winning) / num_trades * 100
            avg_win = winning['pnl'].mean() if len(winning) > 0 else 0.0
            avg_loss = losing['pnl'].mean() if len(losing) > 0 else 0.0
            gross_profit = winning['pnl'].sum() if len(winning) > 0 else 0.0
            gross_loss = abs(losing['pnl'].sum()) if len(losing) > 0 else 0.0
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        else:
            win_rate = avg_win = avg_loss = profit_factor = 0.0
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': (final_equity - self.initial_capital) / self.initial_capital * 100,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_commission': self.total_commission_paid,
        }