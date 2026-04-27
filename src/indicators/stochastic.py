import pandas as pd
import numpy as np

def calculate_stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> dict:
    """
    Calculate Stochastic Oscillator
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        k_period: %K period
        d_period: %D period (moving average of %K)
    
    Returns:
        dict: Contains '%K' and '%D' values
    """
    low_min = data['low'].rolling(window=k_period).min()
    high_max = data['high'].rolling(window=k_period).max()
    
    k_line = 100 * (data['close'] - low_min) / (high_max - low_min)
    d_line = k_line.rolling(window=d_period).mean()
    
    return {
        'k': k_line,
        'd': d_line
    }

def stochastic_signal(stoch: dict, oversold: int = 20, overbought: int = 80) -> pd.Series:
    """
    Generate Stochastic-based signals
    
    Returns:
        pd.Series: 1 for bullish (oversold crossover), -1 for bearish (overbought crossover), 0 otherwise
    """
    signal = pd.Series(0, index=stoch['k'].index)
    
    # Bullish signal: %K crosses above %D in oversold territory
    bullish = (stoch['k'] > stoch['d']) & (stoch['k'].shift(1) <= stoch['d'].shift(1)) & (stoch['k'] < oversold)
    signal[bullish] = 1
    
    # Bearish signal: %K crosses below %D in overbought territory
    bearish = (stoch['k'] < stoch['d']) & (stoch['k'].shift(1) >= stoch['d'].shift(1)) & (stoch['k'] > overbought)
    signal[bearish] = -1
    
    return signal
