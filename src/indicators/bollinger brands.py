import pandas as pd
import numpy as np

def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> dict:
    """
    Calculate Bollinger Bands
    
    Args:
        data: DataFrame with 'close' column
        period: Moving average period
        std_dev: Number of standard deviations
    
    Returns:
        dict: Contains 'upper', 'middle', 'lower' bands
    """
    middle = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()
    
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }

def bollinger_squeeze(bands: dict, threshold: float = 0.05) -> pd.Series:
    """
    Detect Bollinger Band squeeze (low volatility) conditions
    
    Args:
        bands: Dictionary with 'upper' and 'lower' bands
        threshold: Band width threshold for squeeze detection
    
    Returns:
        pd.Series: True if squeeze detected, False otherwise
    """
    bandwidth = (bands['upper'] - bands['lower']) / bands['middle']
    return bandwidth < threshold
