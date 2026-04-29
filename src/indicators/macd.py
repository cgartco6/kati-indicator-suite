import pandas as pd

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return {'macd_line': macd_line, 'signal_line': signal_line, 'histogram': histogram}

def macd_crossover(macd_line: pd.Series, signal_line: pd.Series) -> pd.Series:
    cross = pd.Series(0, index=macd_line.index)
    cross[macd_line > signal_line] = 1
    cross[macd_line <= signal_line] = -1
    return cross.diff().clip(lower=-1, upper=1)
