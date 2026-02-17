"""
FIXED visualization/plotter.py
Replace your current plotter.py with this
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import config

# Use config values that actually exist
sns.set_style("whitegrid")

class BacktestPlotter:
    """Plotting functions for backtest results"""

    @staticmethod
    def plot_equity_curve(equity_curve, benchmark=None, title="Equity Curve"):
        """Plot equity curve"""
        fig, ax = plt.subplots(figsize=(14, 7))

        ax.plot(equity_curve.index, equity_curve['equity'],
                label='Strategy', color=config.COLOR_SCHEME['equity'], linewidth=2)

        if benchmark is not None:
            ax.plot(benchmark.index, benchmark.values,
                   label='Buy & Hold', color=config.COLOR_SCHEME['benchmark'],
                   linewidth=2, linestyle='--')

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_drawdown(equity_curve, title="Drawdown"):
        """Plot drawdown"""
        equity = equity_curve['equity']
        cummax = equity.expanding().max()
        drawdown = (equity - cummax) / cummax * 100

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.fill_between(drawdown.index, drawdown.values, 0,
                        color=config.COLOR_SCHEME['negative'], alpha=0.3)
        ax.plot(drawdown.index, drawdown.values,
               color=config.COLOR_SCHEME['negative'], linewidth=2)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    @staticmethod
    def plot_returns_distribution(trades, title="Trade Returns Distribution"):
        """Plot distribution of trade returns"""
        if trades.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        returns = trades['return_pct']
        ax.hist(returns, bins=30, color=config.COLOR_SCHEME['neutral'], alpha=0.7, edgecolor='black')
        ax.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.2f}%')
        ax.axvline(0, color='black', linestyle='-', linewidth=1)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Return (%)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig