# Kati Indicator Suite — Professional Trading Bot & Telegram Signal System
A high-accuracy automated trading system based on proven multi-indicator confluence strategies.

## 🚀 Features
- **15+ Technical Indicators**: EMA, RSI, MACD, VWAP, ATR, Bollinger Bands, Stochastic, Ichimoku, Volume Profile
- **Multi-Timeframe Confluence**: Combines signals from 5m, 15m, 1h, and 4h timeframes
- **Advanced Signal Filtering**: Reduces false signals using volatility filters and market regime detection
- **Automated Trading Bot**: Full-featured trading bot with risk management and order execution
- **Telegram Signal Bot**: Real-time buy/sell alerts with detailed analysis and charts
- **Comprehensive Backtesting**: Evaluate strategy performance with detailed metrics
- **Live Dashboard**: Streamlit dashboard for monitoring signals and performance

## 📦 Installation
```bash
git clone https://github.com/yourusername/kati-indicator-suite.git
cd kati-indicator-suite
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys and Telegram bot token
