import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from src.indicators import *
from src.signals.signal_generator import SignalGenerator

class ConfluenceAnalyzer:
    """
    Multi-timeframe confluence analyzer
    Combines signals from 5m, 15m, 1h, and 4h timeframes
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.signal_generator = SignalGenerator(config)
        
    def analyze_confluence(self, data_5m: pd.DataFrame, data_15m: pd.DataFrame, 
                           data_1h: pd.DataFrame, data_4h: pd.DataFrame) -> Dict:
        """
        Analyze confluence across multiple timeframes
        
        Returns:
            Dict: Contains 'overall_direction', 'confidence', 'timeframe_alignment'
        """
        signals = {}
        timeframes = ['5m', '15m', '1h', '4h']
        data_dict = {
            '5m': data_5m,
            '15m': data_15m,
            '1h': data_1h,
            '4h': data_4h
        }
        
        # Generate signals for each timeframe
        for tf in timeframes:
            signal = self.signal_generator.generate_signal(data_dict[tf])
            signals[tf] = signal['direction']
        
        # Check alignment
        long_alignment = sum(1 for v in signals.values() if v == 1)
        short_alignment = sum(1 for v in signals.values() if v == -1)
        
        # Determine overall direction
        if long_alignment >= 3:
            overall_direction = 1  # Strong long
            confidence = long_alignment / 4
        elif short_alignment >= 3:
            overall_direction = -1  # Strong short
            confidence = short_alignment / 4
        elif long_alignment == 2 and short_alignment == 0:
            overall_direction = 1  # Moderate long
            confidence = 0.5
        elif short_alignment == 2 and long_alignment == 0:
            overall_direction = -1  # Moderate short
            confidence = 0.5
        else:
            overall_direction = 0  # No clear direction
            confidence = 0
        
        return {
            'overall_direction': overall_direction,
            'confidence': confidence,
            'timeframe_alignment': signals,
            'num_aligned': max(long_alignment, short_alignment)
        }
    
    def get_entry_zone(self, data: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate optimal entry zone using multiple techniques
        """
        # VWAP-based support/resistance
        vwap = calculate_vwap(data)
        
        # EMA-based levels
        ema_fast = calculate_ema(data, self.config['indicators']['ema']['fast'])
        ema_slow = calculate_ema(data, self.config['indicators']['ema']['slow'])
        
        # Volume profile
        vol_profile = calculate_volume_profile(data)
        
        # ATR-based buffer
        atr = calculate_atr(data, self.config['indicators']['atr']['period'])
        buffer = atr.iloc[-1] * 0.25
        
        # Long entry zone: near support levels
        long_zone_low = min(vwap.iloc[-1], ema_fast.iloc[-1], ema_slow.iloc[-1], vol_profile['value_area_low']) - buffer
        long_zone_high = max(vwap.iloc[-1], ema_fast.iloc[-1], ema_slow.iloc[-1], vol_profile['value_area_low']) + buffer
        
        # Short entry zone: near resistance levels
        short_zone_low = min(vwap.iloc[-1], ema_fast.iloc[-1], ema_slow.iloc[-1], vol_profile['value_area_high']) - buffer
        short_zone_high = max(vwap.iloc[-1], ema_fast.iloc[-1], ema_slow.iloc[-1], vol_profile['value_area_high']) + buffer
        
        return {
            'long_zone': (long_zone_low, long_zone_high),
            'short_zone': (short_zone_low, short_zone_high),
            'point_of_control': vol_profile['point_of_control']
        }
