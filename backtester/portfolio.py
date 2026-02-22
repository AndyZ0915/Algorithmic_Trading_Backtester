"""
Portfolio tracking for the backtester.
Handles position management, cash, and trade recording.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """A completed trade."""
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
        
        cost = self.entry_price * self.shares
        if cost > 0:
            self.return_pct = (self.pnl / cost) * 100


class Portfolio:
    """Tracks positions, cash, and equity over time."""
    
    def __init__(self, initial_capital=10000.0, commission=0.001, slippage=0.0005):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission
        self.slippage_rate = slippage
        
        # Current position
        self.shares = 0.0
        self.entry_price = 0.0
        self.entry_date = None
        
        # History
        self.equity_curve = []
        self.dates = []
        self.trades = []
        
        self.total_commission = 0.0
    
    def get_equity(self, price):
        """Total value = cash + position value."""
        return self.cash + (self.shares * price)
    
    def update_equity_curve(self, date, price):
        """Record equity at this timestamp."""
        self.dates.append(date)
        self.equity_curve.append(self.get_equity(price))
    
    def execute_trade(self, date, price, signal):
        """Execute buy/sell based on signal."""
        if signal == 0:
            return False
        
        # Apply slippage
        effective_price = price * (1 + self.slippage_rate * np.sign(signal))
        
        if signal == 1 and self.shares == 0:
            return self._buy(date, effective_price)
        elif signal == -1 and self.shares > 0:
            return self._sell(date, effective_price)
        
        return False
    
    def _buy(self, date, price):
        """Open a position."""
        if self.cash <= 0:
            return False
        
        commission = self.cash * self.commission_rate
        available = self.cash - commission
        
        if available <= 0:
            return False
        
        self.shares = available / price
        self.entry_price = price
        self.entry_date = date
        self.cash = 0.0
        self.total_commission += commission
        
        return True
    
    def _sell(self, date, price):
        """Close the position."""
        if self.shares == 0:
            return False
        
        proceeds = self.shares * price
        commission = proceeds * self.commission_rate
        net = proceeds - commission
        
        # Record trade
        trade = Trade(
            entry_date=self.entry_date,
            exit_date=date,
            entry_price=self.entry_price,
            exit_price=price,
            shares=self.shares,
            direction='long',
            commission=commission
        )
        self.trades.append(trade)
        
        self.cash = net
        self.total_commission += commission
        self.shares = 0.0
        self.entry_price = 0.0
        self.entry_date = None
        
        return True
    
    def get_equity_curve_df(self):
        """Return equity as a DataFrame."""
        if not self.dates:
            return pd.DataFrame({'equity': [self.initial_capital]})
        
        df = pd.DataFrame(
            {'equity': self.equity_curve},
            index=pd.DatetimeIndex(self.dates)
        )
        df.index.name = 'date'
        return df
    
    def get_trades_df(self):
        """Return all trades as a DataFrame."""
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
