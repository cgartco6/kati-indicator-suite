def rsi_signal(rsi: pd.Series, oversold: int = 30, overbought: int = 70) -> pd.Series:
    signal = pd.Series(0, index=rsi.index)
    signal[rsi < oversold] = 1
    signal[rsi > overbought] = -1
    return signal
