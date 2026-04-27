import pandas as pd
import numpy as np

def calculate_ichimoku(data: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou: int = 52) -> dict:
    """
    Calculate Ichimoku Cloud components
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        tenkan: Conversion line period
        kijun: Base line period
        senkou: Leading span period
    
    Returns:
        dict: Contains 'tenkan', 'kijun', 'senkou_a', 'senkou_b', 'chikou'
    """
    # Tenkan-sen (Conversion Line)
    tenkan_high = data['high'].rolling(window=tenkan).max()
    tenkan_low = data['low'].rolling(window=tenkan).min()
    tenkan_line = (tenkan_high + tenkan_low) / 2
    
    # Kijun-sen (Base Line)
    kijun_high = data['high'].rolling(window=kijun).max()
    kijun_low = data['low'].rolling(window=kijun).min()
    kijun_line = (kijun_high + kijun_low) / 2
    
    # Senkou Span A (Leading Span A)
    senkou_a = ((tenkan_line + kijun_line) / 2).shift(kijun)
    
    # Senkou Span B (Leading Span B)
    senkou_high = data['high'].rolling(window=senkou).max()
    senkou_low = data['low'].rolling(window=senkou).min()
    senkou_b = ((senkou_high + senkou_low) / 2).shift(kijun)
    
    # Chikou Span (Lagging Span)
    chikou_span = data['close'].shift(-kijun)
    
    return {
        'tenkan': tenkan_line,
        'kijun': kijun_line,
        'senkou_a': senkou_a,
        'senkou_b': senkou_b,
        'chikou': chikou_span
    }

def ichimoku_signal(ichimoku: dict, data: pd.DataFrame) -> pd.Series:
    """
    Generate Ichimoku-based signals
    
    Returns:
        pd.Series: 1 for bullish, -1 for bearish, 0 otherwise
    """
    signal = pd.Series(0, index=data.index)
    
    # Bullish: Price above cloud, Tenkan above Kijun, Chikou above price
    bullish = (data['close'] > ichimoku['senkou_a']) & \
              (data['close'] > ichimoku['senkou_b']) & \
              (ichimoku['tenkan'] > ichimoku['kijun']) & \
              (ichimoku['chikou'] > data['close'])
    signal[bullish] = 1
    
    # Bearish: Price below cloud, Tenkan below Kijun, Chikou below price
    bearish = (data['close'] < ichimoku['senkou_a']) & \
              (data['close'] < ichimoku['senkou_b']) & \
              (ichimoku['tenkan'] < ichimoku['kijun']) & \
              (ichimoku['chikou'] < data['close'])
    signal[bearish] = -1
    
    return signal
