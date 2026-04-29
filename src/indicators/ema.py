import pandas as pd

def calculate_ema(data: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
    """Exponential Moving Average"""
    return data[column].ewm(span=period, adjust=False).mean()

def ema_crossover(ema_fast: pd.Series, ema_slow: pd.Series) -> pd.Series:
    """1 = golden cross (buy), -1 = death cross (sell), 0 = no cross"""
    cross = pd.Series(0, index=ema_fast.index)
    cross[ema_fast > ema_slow] = 1
    cross[ema_fast <= ema_slow] = -1
    return cross.diff().fillna(0)
