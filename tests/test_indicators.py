import unittest
import pandas as pd
import numpy as np
from src.indicators import calculate_ema, calculate_rsi

class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({'close': np.random.randn(100).cumsum() + 100})
    
    def test_ema(self):
        ema = calculate_ema(self.data, 14)
        self.assertEqual(len(ema), len(self.data))
        self.assertFalse(ema.isnull().all())
    
    def test_rsi(self):
        rsi = calculate_rsi(self.data['close'], 14)
        self.assertTrue((rsi >= 0).all() and (rsi <= 100).all())

if __name__ == '__main__':
    unittest.main()
