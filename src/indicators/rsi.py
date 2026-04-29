import pandas as pd

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def rsi_signal(rsi: pd.Series, oversold: int = 30, overbought: int = 70) -> pd.Series:
    signal = pd.Series(0, index=rsi.index)
    signal[rsi < oversold] = 1   # bullish
    signal[rsi > overbought] = -1  # bearish
    return signal
