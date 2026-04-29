import pandas as pd
import numpy as np
from src.indicators import calculate_ema, calculate_rsi, calculate_vwap, calculate_macd, calculate_atr

class CombinedStrategy:
    """Multi‑indicator trading strategy combining EMA, RSI, VWAP, MACD, and ATR."""
    
    def __init__(self, config: dict):
        self.config = config
        self.position = None
        self.entry_price = None
        self.stop_price = None
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on combined indicator logic.
        Returns DataFrame with a 'signal' column: 1 (buy), -1 (sell), 0 (hold).
        """
        data = data.copy()
        
        # Calculate all required indicators
        ema_fast = calculate_ema(data, self.config['indicators']['ema']['fast'])
        ema_slow = calculate_ema(data, self.config['indicators']['ema']['slow'])
        rsi = calculate_rsi(data['close'], self.config['indicators']['rsi']['period'])
        vwap = calculate_vwap(data)
        macd = calculate_macd(
            data['close'],
            self.config['indicators']['macd']['fast'],
            self.config['indicators']['macd']['slow'],
            self.config['indicators']['macd']['signal']
        )
        atr = calculate_atr(data, self.config['indicators']['atr']['period'])
        
        # Long entry conditions
        long_condition = (
            (data['close'] > vwap) &
            (rsi >= 30) & (rsi <= 70) &
            (macd['histogram'] > 0) &
            (ema_fast > ema_slow)
        )
        
        # Short entry conditions
        short_condition = (
            (data['close'] < vwap) &
            (rsi >= 30) & (rsi <= 70) &
            (macd['histogram'] < 0) &
            (ema_fast < ema_slow)
        )
        
        # Exit logic (simplified trailing stop)
        if self.position == 'long':
            stop = self.entry_price - (atr.iloc[-1] * self.config['indicators']['atr']['multiplier'])
            if data['close'].iloc[-1] <= stop:
                long_condition = False  # exit signal would be handled elsewhere
        elif self.position == 'short':
            stop = self.entry_price + (atr.iloc[-1] * self.config['indicators']['atr']['multiplier'])
            if data['close'].iloc[-1] >= stop:
                short_condition = False
        
        signals = pd.Series(0, index=data.index)
        signals[long_condition] = 1
        signals[short_condition] = -1
        
        # Update position tracking
        if signals.iloc[-1] == 1:
            self.position = 'long'
            self.entry_price = data['close'].iloc[-1]
        elif signals.iloc[-1] == -1:
            self.position = 'short'
            self.entry_price = data['close'].iloc[-1]
        
        data['signal'] = signals
        return data
