import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
from typing import Optional, Dict
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, config: dict):
        self.config = config
        self.exchange = None
        if config.get('exchange', {}).get('name'):
            exchange_class = getattr(ccxt, config['exchange']['name'])
            self.exchange = exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
    
    def fetch_historical_data(self, symbol: str, interval: str, period: str = "3mo") -> pd.DataFrame:
        """Fetch historical OHLCV data"""
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        data.columns = [col.lower() for col in data.columns]
        return data
    
    def fetch_live_data(self, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Fetch recent live data from exchange or fallback to yfinance"""
        if self.exchange:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='15m', limit=limit)
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('timestamp', inplace=True)
            return data
        else:
            # Fallback to yfinance with short period
            return self.fetch_historical_data(symbol, '15m', '1d')
    
    def add_all_indicators(self, data: pd.DataFrame, config: dict) -> pd.DataFrame:
        """Add all technical indicators to DataFrame"""
        from src.indicators import calculate_ema, calculate_rsi, calculate_vwap, calculate_macd, calculate_atr
        
        data['ema_fast'] = calculate_ema(data, config['indicators']['ema']['fast'])
        data['ema_slow'] = calculate_ema(data, config['indicators']['ema']['slow'])
        data['rsi'] = calculate_rsi(data['close'], config['indicators']['rsi']['period'])
        data['vwap'] = calculate_vwap(data)
        macd = calculate_macd(data['close'], 
                              config['indicators']['macd']['fast'],
                              config['indicators']['macd']['slow'],
                              config['indicators']['macd']['signal'])
        data['macd_line'] = macd['macd_line']
        data['macd_signal'] = macd['signal_line']
        data['macd_histogram'] = macd['histogram']
        data['atr'] = calculate_atr(data, config['indicators']['atr']['period'])
        return data
