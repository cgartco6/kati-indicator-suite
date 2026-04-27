import pandas as pd
import numpy as np
from typing import Dict

class SignalFilter:
    """
    Advanced signal filter to reduce false positives
    Uses volatility filters, market regime detection, and timeframe confluence
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.consecutive_signals = 0
        self.last_signal_time = None
        
    def should_trade(self, signal: Dict, data: pd.DataFrame, market_regime: str = 'trending') -> bool:
        """
        Determine if a signal should be executed
        
        Filters applied:
        1. Minimum confluence threshold
        2. Volatility filter
        3. Volume validation
        4. Market regime filter
        5. Signal cooldown
        """
        # Filter 1: Confluence threshold
        if signal['indicators_aligned'] < self.config['signal_filter']['min_confluence']:
            return False
        
        # Filter 2: Volatility filter
        atr = data['atr'].iloc[-1] if 'atr' in data.columns else self._calculate_atr(data)
        price = data['close'].iloc[-1]
        volatility_ratio = atr / price
        
        if volatility_ratio < self.config['signal_filter']['volatility_threshold']:
            return False
        
        # Filter 3: Volume validation
        avg_volume = data['volume'].rolling(20).mean().iloc[-1]
        current_volume = data['volume'].iloc[-1]
        
        if current_volume < avg_volume * self.config['signal_filter']['min_volume_ratio']:
            return False
        
        # Filter 4: Market regime filter
        if not self._is_valid_regime(signal, market_regime):
            return False
        
        # Filter 5: Signal cooldown
        if not self._validate_cooldown():
            return False
        
        # Filter 6: Spread filter
        if data['high'].iloc[-1] - data['low'].iloc[-1] > atr * 1.5:
            return False
        
        # All filters passed
        return True
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR if not present"""
        high = data['high']
        low = data['low']
        close = data['close'].shift(1)
        
        tr1 = high - low
        tr2 = (high - close).abs()
        tr3 = (low - close).abs()
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
    
    def _is_valid_regime(self, signal: Dict, market_regime: str) -> bool:
        """Validate signal based on market regime"""
        if market_regime == 'choppy':
            # In choppy markets, only take high-confidence signals
            return signal['strength'] > 0.7
        elif market_regime == 'trending':
            return True
        elif market_regime == 'high_volatility':
            # In high volatility, only take ultra-conservative signals
            return signal['strength'] > 0.8 and signal['indicators_aligned'] >= 4
        return True
    
    def _validate_cooldown(self) -> bool:
        """Enforce signal cooldown period"""
        import datetime
        
        now = datetime.datetime.now()
        minutes_since_last = 5  # Default cooldown
        
        if self.last_signal_time:
            minutes_since_last = (now - self.last_signal_time).seconds / 60
        
        if minutes_since_last < self.config['telegram']['signal_cooldown_minutes']:
            return False
        
        self.last_signal_time = now
        return True
