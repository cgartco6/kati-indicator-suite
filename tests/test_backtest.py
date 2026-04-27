import unittest
import pandas as pd
import numpy as np
from src.backtest.backtest_engine import BacktestEngine
from src.strategy.combined_strategy import CombinedStrategy

class TestBacktest(unittest.TestCase):
    def setUp(self):
        # Create synthetic data
        dates = pd.date_range('2024-01-01', periods=500, freq='15min')
        prices = 100 + np.cumsum(np.random.randn(500) * 0.5)
        self.data = pd.DataFrame({
            'open': prices * (1 + np.random.randn(500) * 0.002),
            'high': prices * (1 + np.abs(np.random.randn(500) * 0.005)),
            'low': prices * (1 - np.abs(np.random.randn(500) * 0.005)),
            'close': prices,
            'volume': np.random.randint(1000, 10000, 500)
        }, index=dates)
        
        self.config = {
            'strategy': {
                'ema': {'fast_period': 20, 'slow_period': 50},
                'rsi': {'period': 14},
                'macd': {'fast': 12, 'slow': 26, 'signal': 9},
                'atr': {'period': 14, 'multiplier': 2.0}
            },
            'backtest': {'initial_capital': 10000, 'commission': 0.001, 'slippage': 0.0005}
        }
        
    def test_backtest_runs(self):
        strategy = CombinedStrategy(self.config)
        engine = BacktestEngine(initial_capital=10000, commission=0.001, slippage=0.0005)
        results = engine.run(self.data, strategy)
        
        self.assertIn('total_return_pct', results)
        self.assertIn('sharpe_ratio', results)
        self.assertIn('max_drawdown_pct', results)
        self.assertIsInstance(results['total_return_pct'], float)
        
    def test_backtest_returns_dict(self):
        strategy = CombinedStrategy(self.config)
        engine = BacktestEngine()
        results = engine.run(self.data, strategy)
        self.assertIsInstance(results, dict)

if __name__ == '__main__':
    unittest.main()
