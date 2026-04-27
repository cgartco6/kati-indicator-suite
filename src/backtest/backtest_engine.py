import pandas as pd
import numpy as np
from typing import Dict, Any, List

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001, slippage: float = 0.0005):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
    def run(self, data: pd.DataFrame, strategy) -> Dict[str, Any]:
        data_with_signals = strategy.generate_signals(data)
        capital = self.initial_capital
        position = 0
        trades = []
        portfolio_values = [capital]
        
        for i in range(1, len(data_with_signals)):
            price = data_with_signals['close'].iloc[i]
            signal = data_with_signals['signal'].iloc[i]
            
            if signal == 1 and position <= 0:  # Buy
                if position < 0:
                    capital += abs(position) * price * (1 - self.slippage)
                trade_price = price * (1 + self.slippage)
                position = capital / trade_price
                capital = 0
                trades.append({'type': 'buy', 'price': trade_price, 'time': data_with_signals.index[i]})
                
            elif signal == -1 and position >= 0:  # Sell
                if position > 0:
                    capital = position * price * (1 - self.slippage)
                    position = 0
                    trades.append({'type': 'sell', 'price': price * (1 - self.slippage), 'time': data_with_signals.index[i]})
            
            value = capital + (position * price) if position > 0 else capital
            portfolio_values.append(value)
        
        data_with_signals['portfolio_value'] = portfolio_values
        returns = pd.Series(portfolio_values).pct_change().dropna()
        total_return = (portfolio_values[-1] - self.initial_capital) / self.initial_capital * 100
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        max_dd = self._max_drawdown(portfolio_values)
        win_rate = self._win_rate(trades)
        
        return {
            'final_value': portfolio_values[-1],
            'total_return_pct': total_return,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd,
            'win_rate_pct': win_rate,
            'num_trades': len(trades),
            'portfolio_history': portfolio_values,
            'trades': trades
        }
    
    def _max_drawdown(self, values: List[float]) -> float:
        peak = values[0]
        max_dd = 0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak * 100
            if dd > max_dd:
                max_dd = dd
        return max_dd
    
    def _win_rate(self, trades: List[dict]) -> float:
        if len(trades) < 2:
            return 0.0
        profitable = 0
        for i in range(1, len(trades), 2):
            if i < len(trades) and trades[i]['price'] > trades[i-1]['price']:
                profitable += 1
        return (profitable / (len(trades) // 2)) * 100 if len(trades)//2 > 0 else 0
