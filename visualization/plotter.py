"""
Visualization module for creating charts and plots.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional
from config import FIGURE_SIZE, COLOR_PALETTE

plt.style.use('seaborn-v0_8-darkgrid')


class BacktestPlotter:
    """
    Creates visualizations for backtest results.
    """
    
    @staticmethod
    def plot_equity_curve(
        equity_curve: pd.DataFrame,
        benchmark: Optional[pd.Series] = None,
        title: str = "Portfolio Equity Curve"
    ):
        """
        Plot equity curve with optional benchmark.
        
        Args:
            equity_curve: DataFrame with equity over time
            benchmark: Optional benchmark prices
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # Plot strategy equity
        ax.plot(
            equity_curve.index,
            equity_curve['equity'],
            label='Strategy',
            color=COLOR_PALETTE['strategy'],
            linewidth=2
        )
        
        # Plot benchmark if provided
        if benchmark is not None:
            # Normalize benchmark to start at same value
            initial_equity = equity_curve['equity'].iloc[0]
            normalized_benchmark = (
                benchmark / benchmark.iloc[0] * initial_equity
            )
            
            ax.plot(
                normalized_benchmark.index,
                normalized_benchmark,
                label='Buy & Hold',
                color=COLOR_PALETTE['buy_hold'],
                linewidth=2,
                linestyle='--'
            )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_returns_distribution(trades: pd.DataFrame):
        """
        Plot distribution of trade returns.
        
        Args:
            trades: DataFrame with trade information
        """
        if trades.empty:
            print("No trades to plot")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=FIGURE_SIZE)
        
        # Histogram of returns
        ax1.hist(
            trades['return_pct'],
            bins=30,
            color=COLOR_PALETTE['strategy'],
            alpha=0.7,
            edgecolor='black'
        )
        ax1.axvline(
            x=0,
            color='red',
            linestyle='--',
            label='Break-even'
        )
        ax1.set_title('Distribution of Trade Returns', fontweight='bold')
        ax1.set_xlabel('Return (%)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(
            trades['return_pct'],
            vert=True,
            patch_artist=True,
            boxprops=dict(facecolor=COLOR_PALETTE['strategy'], alpha=0.7)
        )
        ax2.set_title('Trade Returns Box Plot', fontweight='bold')
        ax2.set_ylabel('Return (%)')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_drawdown(equity_curve: pd.DataFrame):
        """
        Plot drawdown over time.
        
        Args:
            equity_curve: DataFrame with equity over time
        """
        fig, ax = plt.subplots(figsize=FIGURE_SIZE)
        
        # Calculate drawdown
        equity = equity_curve['equity']
        cumulative_max = equity.expanding().max()
        drawdown = (equity - cumulative_max) / cumulative_max * 100
        
        ax.fill_between(
            drawdown.index,
            drawdown,
            0,
            color=COLOR_PALETTE['sell_signal'],
            alpha=0.3,
            label='Drawdown'
        )
        ax.plot(
            drawdown.index,
            drawdown,
            color=COLOR_PALETTE['sell_signal'],
            linewidth=1.5
        )
        
        ax.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_monthly_returns(equity_curve: pd.DataFrame):
        """
        Plot monthly returns heatmap.
        
        Args:
            equity_curve: DataFrame with equity over time
        """
        # Calculate monthly returns
        monthly_equity = equity_curve['equity'].resample('M').last()
        monthly_returns = monthly_equity.pct_change() * 100
        
        # Create pivot table for heatmap
        monthly_returns_df = pd.DataFrame({
            'Year': monthly_returns.index.year,
            'Month': monthly_returns.index.month,
            'Return': monthly_returns.values
        })
        
        pivot = monthly_returns_df.pivot(
            index='Month',
            columns='Year',
            values='Return'
        )
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create heatmap
        im = ax.imshow(pivot, cmap='RdYlGn', aspect='auto', vmin=-10, vmax=10)
        
        # Set ticks
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_yticks(np.arange(len(pivot.index)))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticklabels([
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Return (%)', rotation=270, labelpad=20)
        
        # Add values to cells
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                value = pivot.iloc[i, j]
                if not np.isnan(value):
                    text = ax.text(
                        j, i, f'{value:.1f}',
                        ha='center', va='center',
                        color='black' if abs(value) < 5 else 'white',
                        fontsize=9
                    )
        
        ax.set_title('Monthly Returns Heatmap (%)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_all(
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame,
        benchmark: Optional[pd.Series] = None,
        save_path: Optional[str] = None
    ):
        """
        Create comprehensive visualization with multiple subplots.
        
        Args:
            equity_curve: DataFrame with equity over time
            trades: DataFrame with trade information
            benchmark: Optional benchmark prices
            save_path: Path to save the figure
        """
        # Create equity curve plot
        fig1 = BacktestPlotter.plot_equity_curve(
            equity_curve,
            benchmark,
            "Strategy Performance vs Buy & Hold"
        )
        
        # Create drawdown plot
        fig2 = BacktestPlotter.plot_drawdown(equity_curve)
        
        # Create returns distribution (if trades exist)
        if not trades.empty:
            fig3 = BacktestPlotter.plot_returns_distribution(trades)
        
        plt.show()
        
        if save_path:
            fig1.savefig(f"{save_path}_equity.png", dpi=300, bbox_inches='tight')
            fig2.savefig(f"{save_path}_drawdown.png", dpi=300, bbox_inches='tight')
            if not trades.empty:
                fig3.savefig(f"{save_path}_returns.png", dpi=300, bbox_inches='tight')
