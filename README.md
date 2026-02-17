# 📈 Algorithmic Trading Backtester - Production Application

A professional-grade, web-based backtesting platform for algorithmic trading strategies.

## 🎯 Features

### Core Functionality
- ✅ **5+ Trading Strategies**: MA Crossover, RSI, MACD, Bollinger Bands, Mean Reversion
- ✅ **Real-time Data**: Yahoo Finance integration with intelligent demo fallback
- ✅ **Professional Metrics**: Sharpe, Sortino, Calmar ratios, Alpha, Beta, and more
- ✅ **Interactive Visualizations**: 7 chart types with Plotly
- ✅ **Strategy Comparison**: Side-by-side performance analysis
- ✅ **Trade Analytics**: Detailed trade log with profit/loss tracking

### Advanced Features
- 🎨 **Modern UI**: Clean Streamlit dashboard with dark mode
- 💾 **Smart Caching**: SQLite database to minimize API calls
- 📊 **Multi-tab Interface**: Organized workflow across 4 main views
- 📈 **Parameter Sensitivity**: Optimize strategy parameters
- 💰 **Realistic Costs**: Configurable commission and slippage
- 📥 **Export Results**: CSV/PDF downloads

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd trading_backtester_PRODUCTION

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

Application opens at: **http://localhost:8501**

## 📁 Project Structure

```
trading_backtester_PRODUCTION/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration parameters
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
├── Dockerfile                  # Container configuration
│
├── data/                       # Data layer
│   ├── __init__.py
│   ├── data_fetcher.py        # Yahoo Finance + demo fallback
│   └── database.py            # SQLite caching
│
├── strategies/                 # Trading strategies
│   ├── __init__.py
│   ├── base_strategy.py       # Abstract base class
│   ├── ma_crossover.py        # Moving Average strategy
│   ├── rsi_strategy.py        # RSI strategy
│   ├── macd_strategy.py       # MACD strategy
│   ├── bollinger_bands.py     # Bollinger Bands strategy
│   └── mean_reversion.py      # Mean Reversion strategy
│
├── backtester/                 # Backtesting engine
│   ├── __init__.py
│   ├── engine.py              # Main backtesting logic
│   ├── portfolio.py           # Portfolio management
│   └── metrics.py             # Performance calculations
│
├── visualization/              # Charts and plots
│   ├── __init__.py
│   └── charts.py              # Plotly visualizations
│
├── utils/                      # Utilities
│   ├── __init__.py
│   └── helpers.py             # Helper functions
│
├── ui/                         # UI components
│   ├── __init__.py
│   ├── sidebar.py             # Sidebar configuration
│   └── pages/                 # Multi-page components
│       ├── 01_Backtest.py
│       ├── 02_Metrics.py
│       ├── 03_Trade_Log.py
│       └── 04_Compare.py
│
└── tests/                      # Test suite
    ├── __init__.py
    ├── test_strategies.py
    └── test_engine.py
```

## 📊 Usage Guide

### 1. Configure Backtest
- Select stock symbol (AAPL, MSFT, SPY, etc.)
- Choose date range (default: 2020-2024)
- Set initial capital

### 2. Select Strategy
- Moving Average Crossover
- RSI Strategy
- MACD Strategy
- Bollinger Bands
- Mean Reversion

### 3. Adjust Parameters
- Each strategy has configurable parameters
- Use sliders in sidebar

### 4. Run Backtest
- Click "Run Backtest" button
- View results in tabs:
  - **Backtest**: Overview and equity curve
  - **Metrics**: Detailed performance statistics
  - **Trade Log**: All trades with P&L
  - **Compare**: Side-by-side strategy comparison

### 5. Analyze Results
- Interactive charts (zoom, pan, hover)
- Download trade history as CSV
- Compare against buy-and-hold benchmark

## 🎓 Educational Value

This project demonstrates:
- **Clean Architecture**: Separation of concerns with modular design
- **Design Patterns**: Strategy pattern, Template method
- **Error Handling**: Graceful degradation with demo data
- **Testing**: Unit tests for critical components
- **Documentation**: Comprehensive docstrings
- **Type Safety**: Type hints throughout
- **Best Practices**: PEP 8, SOLID principles

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type check
mypy .
```

### Docker Deployment
```bash
docker build -t trading-backtester .
docker run -p 8501:8501 trading-backtester
```

## 📈 Performance Metrics

The backtester calculates 15+ professional metrics:
- Total Return & Annualized Return
- Sharpe Ratio & Sortino Ratio
- Maximum Drawdown & Calmar Ratio
- Win Rate & Profit Factor
- Alpha & Beta (vs benchmark)
- Average Win/Loss
- And more...

## 🔧 Configuration

Edit `config.py` to customize:
- Default parameters
- Commission rates
- Slippage assumptions
- Risk-free rate
- Color schemes

## 🚨 Troubleshooting

### Yahoo Finance Blocked
- Application automatically uses demo data
- Demo data is realistic and suitable for testing

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Dependencies Issues
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📝 License

MIT License - Free to use for personal and educational purposes

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📧 Support

For issues or questions, please open a GitHub issue.

---

Built with ❤️ for algorithmic trading education
