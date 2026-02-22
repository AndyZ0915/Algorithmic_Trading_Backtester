"""
Charts module - all visualizations using Plotly (no matplotlib).
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import config


def create_equity_chart(equity_curve: pd.DataFrame, benchmark_data: pd.Series = None,
                        initial_capital: float = 10000, title: str = "Portfolio Equity") -> go.Figure:
    """
    Create interactive equity curve chart comparing strategy vs buy & hold.

    Args:
        equity_curve: DataFrame with 'equity' column indexed by date
        benchmark_data: Series of benchmark prices (normalized to capital)
        initial_capital: Starting capital for normalization
        title: Chart title

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Strategy equity line
    fig.add_trace(go.Scatter(
        x=equity_curve.index,
        y=equity_curve['equity'],
        name='Strategy',
        line=dict(color=config.COLOR_SCHEME['equity'], width=2),
        hovertemplate='<b>Strategy</b><br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
    ))

    # Buy & hold benchmark
    if benchmark_data is not None:
        normalized = (benchmark_data / benchmark_data.iloc[0]) * initial_capital
        fig.add_trace(go.Scatter(
            x=normalized.index,
            y=normalized.values,
            name='Buy & Hold',
            line=dict(color=config.COLOR_SCHEME['benchmark'], width=2, dash='dash'),
            hovertemplate='<b>Buy & Hold</b><br>Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        height=500,
        hovermode='x unified',
        template=config.CHART_TEMPLATE,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        yaxis=dict(tickprefix='$', tickformat=',.0f')
    )

    return fig


def create_drawdown_chart(equity_curve: pd.DataFrame, title: str = "Drawdown Analysis") -> go.Figure:
    """
    Create drawdown underwater chart.

    Args:
        equity_curve: DataFrame with 'equity' column
        title: Chart title

    Returns:
        Plotly Figure object
    """
    equity = equity_curve['equity']
    cummax = equity.expanding().max()
    drawdown = (equity - cummax) / cummax * 100

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown.values,
        fill='tozeroy',
        name='Drawdown',
        line=dict(color=config.COLOR_SCHEME['negative'], width=1),
        fillcolor='rgba(239, 71, 111, 0.3)',
        hovertemplate='<b>Drawdown</b><br>Date: %{x}<br>DD: %{y:.2f}%<extra></extra>'
    ))

    # Add max drawdown line
    max_dd = drawdown.min()
    fig.add_hline(
        y=max_dd,
        line_dash='dot',
        line_color='red',
        annotation_text=f'Max DD: {max_dd:.1f}%',
        annotation_position='bottom right'
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title='Date',
        yaxis_title='Drawdown (%)',
        height=400,
        template=config.CHART_TEMPLATE,
        yaxis=dict(ticksuffix='%')
    )

    return fig


def create_monthly_returns_heatmap(equity_curve: pd.DataFrame, title: str = "Monthly Returns (%)") -> go.Figure:
    """
    Create monthly returns heatmap.

    Args:
        equity_curve: DataFrame with 'equity' column
        title: Chart title

    Returns:
        Plotly Figure object
    """
    equity = equity_curve['equity']
    monthly = equity.resample('ME').last().pct_change() * 100

    monthly_df = pd.DataFrame({
        'year': monthly.index.year,
        'month': monthly.index.month,
        'return': monthly.values
    }).dropna()

    if monthly_df.empty:
        fig = go.Figure()
        fig.update_layout(title=title, height=300)
        return fig

    # Pivot to year x month grid
    pivot = monthly_df.pivot(index='year', columns='month', values='return')
    pivot.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][:len(pivot.columns)]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0, '#EF476F'],
            [0.5, '#FFFFFF'],
            [1.0, '#06D6A0']
        ],
        zmid=0,
        text=np.round(pivot.values, 1),
        texttemplate='%{text}%',
        textfont=dict(size=11),
        hovertemplate='<b>%{y} %{x}</b><br>Return: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        height=max(300, len(pivot) * 40 + 100),
        template=config.CHART_TEMPLATE
    )

    return fig


def create_rolling_sharpe_chart(equity_curve: pd.DataFrame, risk_free_rate: float = 0.04,
                                window: int = 126, title: str = "Rolling Sharpe Ratio (6-Month)") -> go.Figure:
    """
    Create rolling Sharpe ratio chart.

    Args:
        equity_curve: DataFrame with 'equity' column
        risk_free_rate: Annual risk-free rate
        window: Rolling window in days
        title: Chart title

    Returns:
        Plotly Figure object
    """
    equity = equity_curve['equity']
    daily_returns = equity.pct_change().dropna()
    daily_rf = risk_free_rate / 252

    rolling_sharpe = (
        (daily_returns - daily_rf).rolling(window).mean() /
        daily_returns.rolling(window).std()
    ) * np.sqrt(252)

    fig = go.Figure()

    # Color based on positive/negative
    fig.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe.values,
        name='Rolling Sharpe',
        line=dict(color=config.COLOR_SCHEME['neutral'], width=2),
        hovertemplate='<b>Rolling Sharpe</b><br>Date: %{x}<br>Sharpe: %{y:.2f}<extra></extra>'
    ))

    # Reference lines
    fig.add_hline(y=1.0, line_dash='dash', line_color='green',
                  annotation_text='Good (1.0)', annotation_position='right')
    fig.add_hline(y=0.0, line_dash='dash', line_color='grey', line_width=1)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title='Date',
        yaxis_title='Sharpe Ratio',
        height=400,
        template=config.CHART_TEMPLATE
    )

    return fig


def create_trade_distribution_chart(trades: pd.DataFrame, title: str = "Trade Returns Distribution") -> go.Figure:
    """
    Create trade returns histogram.

    Args:
        trades: DataFrame with trade data including 'return_pct'
        title: Chart title

    Returns:
        Plotly Figure object
    """
    if trades.empty or 'return_pct' not in trades.columns:
        fig = go.Figure()
        fig.update_layout(title=title, height=400)
        return fig

    returns = trades['return_pct']
    winners = returns[returns > 0]
    losers = returns[returns <= 0]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=winners,
        name='Winning Trades',
        marker_color=config.COLOR_SCHEME['positive'],
        opacity=0.7,
        hovertemplate='Return: %{x:.2f}%<br>Count: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Histogram(
        x=losers,
        name='Losing Trades',
        marker_color=config.COLOR_SCHEME['negative'],
        opacity=0.7,
        hovertemplate='Return: %{x:.2f}%<br>Count: %{y}<extra></extra>'
    ))

    fig.add_vline(x=returns.mean(), line_dash='dash', line_color='blue',
                  annotation_text=f'Mean: {returns.mean():.1f}%')
    fig.add_vline(x=0, line_dash='solid', line_color='black', line_width=1)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title='Return (%)',
        yaxis_title='Number of Trades',
        height=400,
        barmode='overlay',
        template=config.CHART_TEMPLATE,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )

    return fig


def create_signals_chart(data: pd.DataFrame, signals: pd.Series = None,
                         title: str = "Price with Buy/Sell Signals") -> go.Figure:
    """
    Create price chart with buy/sell signal markers.

    Args:
        data: OHLCV DataFrame
        signals: Series of signals (1=buy, -1=sell, 0=hold)
        title: Chart title

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Candlestick chart
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data['Close'],
        name='Price',
        line=dict(color=config.COLOR_SCHEME['neutral'], width=1.5),
        hovertemplate='<b>Price</b><br>Date: %{x}<br>Close: $%{y:.2f}<extra></extra>'
    ))

    # Buy signals
    if signals is not None:
        buy_signals = data[signals == 1]
        sell_signals = data[signals == -1]

        if not buy_signals.empty:
            fig.add_trace(go.Scatter(
                x=buy_signals.index,
                y=buy_signals['Close'],
                mode='markers',
                name='Buy',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color=config.COLOR_SCHEME['buy_signal'],
                    line=dict(width=1, color='darkgreen')
                ),
                hovertemplate='<b>BUY</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ))

        if not sell_signals.empty:
            fig.add_trace(go.Scatter(
                x=sell_signals.index,
                y=sell_signals['Close'],
                mode='markers',
                name='Sell',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color=config.COLOR_SCHEME['sell_signal'],
                    line=dict(width=1, color='darkred')
                ),
                hovertemplate='<b>SELL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
            ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title='Date',
        yaxis_title='Price ($)',
        height=500,
        hovermode='x unified',
        template=config.CHART_TEMPLATE,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )

    return fig


def create_comparison_chart(results_dict: dict, initial_capital: float = 10000,
                            title: str = "Strategy Comparison") -> go.Figure:
    """
    Create multi-strategy equity comparison chart.

    Args:
        results_dict: Dict mapping strategy name to results object
        initial_capital: Starting capital
        title: Chart title

    Returns:
        Plotly Figure object
    """
    colors = ['#667eea', '#06D6A0', '#EF476F', '#FFD166', '#118AB2', '#073B4C']

    fig = go.Figure()

    for i, (name, results) in enumerate(results_dict.items()):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=results.equity_curve.index,
            y=results.equity_curve['equity'],
            name=name,
            line=dict(color=color, width=2),
            hovertemplate=f'<b>{name}</b><br>Date: %{{x}}<br>Value: $%{{y:,.2f}}<extra></extra>'
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        height=500,
        hovermode='x unified',
        template=config.CHART_TEMPLATE,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        yaxis=dict(tickprefix='$', tickformat=',.0f')
    )

    return fig
