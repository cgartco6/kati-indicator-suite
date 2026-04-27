import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from src.data.data_loader import DataLoader
from src.signals.signal_generator import SignalGenerator

st.set_page_config(page_title="Kati Indicator Suite", layout="wide")

def run_dashboard():
    st.title("📊 Kati Indicator Suite – Live Dashboard")
    
    with open('config/settings.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    symbol = st.sidebar.text_input("Symbol", config['trading']['symbol'])
    interval = st.sidebar.selectbox("Interval", ["5m", "15m", "1h", "4h"], index=1)
    
    if st.sidebar.button("Refresh Data"):
        loader = DataLoader(config)
        data = loader.fetch_historical_data(symbol, interval, period="7d")
        data = loader.add_all_indicators(data, config)
        
        gen = SignalGenerator(config)
        signal = gen.generate_signal(data)
        
        # Create figure
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.5, 0.25, 0.25])
        fig.add_trace(go.Candlestick(x=data.index, open=data['open'], high=data['high'],
                                     low=data['low'], close=data['close'], name='Price'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['ema_fast'], name='EMA Fast'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['ema_slow'], name='EMA Slow'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['vwap'], name='VWAP'), row=1, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['rsi'], name='RSI'), row=2, col=1)
        fig.add_trace(go.Scatter(x=data.index, y=data['macd_histogram'], name='MACD Hist'), row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Latest Signal")
        st.write(f"Direction: {signal['direction']} | Strength: {signal['strength']:.2%} | Aligned: {signal['indicators_aligned']}")

if __name__ == "__main__":
    run_dashboard()
