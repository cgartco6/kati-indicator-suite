import pandas as pd

def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    high = data['high']
    low = data['low']
    close = data['close'].shift(1)
    tr1 = high - low
    tr2 = (high - close).abs()
    tr3 = (low - close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()

def atr_trailing_stop(data: pd.DataFrame, atr: pd.Series, multiplier: float = 2.0) -> pd.Series:
    return data['close'] - (atr * multiplier)
