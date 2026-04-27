import pandas as pd
import numpy as np

def calculate_volume_profile(data: pd.DataFrame, num_levels: int = 50) -> dict:
    """
    Calculate Volume Profile (Volume by Price Level)
    
    Args:
        data: DataFrame with 'high', 'low', 'close', 'volume' columns
        num_levels: Number of price levels to analyze
    
    Returns:
        dict: Contains 'value_area_high', 'value_area_low', 'point_of_control'
    """
    # Create price bins
    price_min = data['low'].min()
    price_max = data['high'].max()
    price_bins = np.linspace(price_min, price_max, num_levels)
    
    # Assign each candle to a price level based on its typical price
    typical_price = (data['high'] + data['low'] + data['close']) / 3
    price_levels = pd.cut(typical_price, bins=price_bins, labels=False)
    
    # Calculate volume by price level
    volume_by_price = data.groupby(price_levels)['volume'].sum()
    
    # Find point of control (highest volume level)
    poc = price_bins[volume_by_price.idxmax()]
    
    # Calculate value area (70% of total volume)
    volume_sorted = volume_by_price.sort_values(ascending=False)
    cumulative_volume = volume_sorted.cumsum()
    value_area_levels = volume_sorted[cumulative_volume <= cumulative_volume.sum() * 0.7].index
    value_area_high = price_bins[value_area_levels.max()]
    value_area_low = price_bins[value_area_levels.min()]
    
    return {
        'point_of_control': poc,
        'value_area_high': value_area_high,
        'value_area_low': value_area_low
    }

def volume_profile_signal(data: pd.DataFrame, profile: dict) -> pd.Series:
    """
    Generate Volume Profile-based signals
    
    Returns:
        pd.Series: 1 for bullish, -1 for bearish, 0 otherwise
    """
    signal = pd.Series(0, index=data.index)
    
    # Bullish: Price above point of control with increasing volume
    bullish = (data['close'] > profile['point_of_control']) & \
              (data['volume'] > data['volume'].rolling(20).mean())
    signal[bullish] = 1
    
    # Bearish: Price below point of control with increasing volume
    bearish = (data['close'] < profile['point_of_control']) & \
              (data['volume'] > data['volume'].rolling(20).mean())
    signal[bearish] = -1
    
    return signal
