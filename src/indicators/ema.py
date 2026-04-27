import pandas as pd

def calculate_ema(data: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """Calculate Exponential Moving Average"""
    return data[column].ewm(span=period, adjust=False).mean()

def ema_crossover(ema_fast: pd.Series, ema_slow: pd.Series) -> pd.Series:
    """Detect EMA crossover signals: 1 for golden cross, -1 for death cross"""
    cross = pd.Series(0, index=ema_fast.index)
    cross[ema_fast > ema_slow] = 1
    cross[ema_fast <= ema_slow] = -1
    return cross.diff()
