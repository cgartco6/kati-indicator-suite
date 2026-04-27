import pandas as pd

def calculate_vwap(data: pd.DataFrame) -> pd.Series:
    """Volume Weighted Average Price (intraday VWAP)"""
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    cum_price_volume = (typical_price * data['volume']).cumsum()
    cum_volume = data['volume'].cumsum()
    return cum_price_volume / cum_volume

def vwap_signal(data: pd.DataFrame, vwap: pd.Series, threshold_pct: float = 0.01) -> pd.Series:
    """1 = bullish (price > VWAP), -1 = bearish (price < VWAP)"""
    signal = pd.Series(0, index=data.index)
    signal[data['close'] > vwap * (1 + threshold_pct)] = 1
    signal[data['close'] < vwap * (1 - threshold_pct)] = -1
    return signal
