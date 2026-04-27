import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from src.indicators import (
    calculate_ema, calculate_rsi, calculate_vwap, 
    calculate_macd, calculate_atr, calculate_bollinger_bands,
    calculate_stochastic, calculate_ichimoku, calculate_volume_profile
)

class SignalGenerator:
    """Multi-indicator confluence signal generator"""
    
    def __init__(self, config: dict):
        self.config = config
        self.indicator_weights = {
            'trend': 0.3,
            'momentum': 0.25,
            'volume': 0.2,
            'volatility': 0.15,
            'pattern': 0.1
        }
    
    def generate_signal(self, data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive trading signal using all indicators
        
        Returns:
            Dict: Contains 'direction' (1=long, -1=short), 'strength', 'indicators_aligned', 'stop_loss', 'take_profit'
        """
        # Calculate all indicators
        indicators = self._calculate_all_indicators(data)
        
        # Get individual signal scores
        trend_score = self._trend_score(data, indicators)
        momentum_score = self._momentum_score(data, indicators)
        volume_score = self._volume_score(data, indicators)
        volatility_score = self._volatility_score(data, indicators)
        pattern_score = self._pattern_score(data, indicators)
        
        # Weighted final score
        total_score = (
            trend_score * self.indicator_weights['trend'] +
            momentum_score * self.indicator_weights['momentum'] +
            volume_score * self.indicator_weights['volume'] +
            volatility_score * self.indicator_weights['volatility'] +
            pattern_score * self.indicator_weights['pattern']
        )
        
        # Determine signal direction
        direction = 0
        if total_score > 0.4:
            direction = 1  # Long
        elif total_score < -0.4:
            direction = -1  # Short
        
        # Calculate risk levels
        atr = indicators['atr'].iloc[-1]
        stop_loss = data['close'].iloc[-1] - (atr * self.config['risk']['stop_loss_atr_multiplier']) if direction == 1 else data['close'].iloc[-1] + (atr * self.config['risk']['stop_loss_atr_multiplier'])
        take_profit = data['close'].iloc[-1] + (atr * self.config['risk']['take_profit_ratio']) if direction == 1 else data['close'].iloc[-1] - (atr * self.config['risk']['take_profit_ratio'])
        
        return {
            'direction': direction,
            'strength': abs(total_score),
            'indicators_aligned': self._count_aligned_indicators(indicators),
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'timestamp': data.index[-1],
            'price': data['close'].iloc[-1]
        }
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate all technical indicators"""
        indicators = {}
        
        # Trend indicators
        indicators['ema_fast'] = calculate_ema(data, self.config['indicators']['ema']['fast'])
        indicators['ema_slow'] = calculate_ema(data, self.config['indicators']['ema']['slow'])
        
        # Momentum indicators
        indicators['rsi'] = calculate_rsi(data['close'], self.config['indicators']['rsi']['period'])
        macd = calculate_macd(
            data['close'],
            self.config['indicators']['macd']['fast'],
            self.config['indicators']['macd']['slow'],
            self.config['indicators']['macd']['signal']
        )
        indicators['macd_histogram'] = macd['histogram']
        
        # Volume indicators
        indicators['vwap'] = calculate_vwap(data)
        
        # Volatility indicators
        indicators['atr'] = calculate_atr(data, self.config['indicators']['atr']['period'])
        bands = calculate_bollinger_bands(data, self.config['indicators']['bollinger']['period'], self.config['indicators']['bollinger']['std_dev'])
        indicators['bb_position'] = (data['close'] - bands['lower']) / (bands['upper'] - bands['lower'])
        
        # Pattern indicators
        stoch = calculate_stochastic(data, self.config['indicators']['stochastic']['k_period'], self.config['indicators']['stochastic']['d_period'])
        indicators['stoch_k'] = stoch['k']
        
        return indicators
    
    def _trend_score(self, data: pd.DataFrame, indicators: Dict) -> float:
        """
        Calculate trend direction score
        Returns: -1 to 1 (negative = bearish, positive = bullish)
        """
        score = 0
        
        # EMA alignment
        if indicators['ema_fast'].iloc[-1] > indicators['ema_slow'].iloc[-1]:
            score += 0.5
        else:
            score -= 0.5
        
        # Price vs VWAP
        if data['close'].iloc[-1] > indicators['vwap'].iloc[-1]:
            score += 0.3
        else:
            score -= 0.3
        
        # Bollinger Band position
        if indicators['bb_position'].iloc[-1] > 0.5:
            score += 0.2
        else:
            score -= 0.2
        
        return np.clip(score, -1, 1)
    
    def _momentum_score(self, data: pd.DataFrame, indicators: Dict) -> float:
        """Calculate momentum direction score"""
        score = 0
        
        # RSI
        rsi = indicators['rsi'].iloc[-1]
        if 40 <= rsi <= 60:
            score += 0.2
        elif rsi > 70:
            score -= 0.3
        elif rsi < 30:
            score += 0.3
        
        # MACD histogram
        if indicators['macd_histogram'].iloc[-1] > 0:
            score += 0.4
        else:
            score -= 0.4
        
        # Stochastic
        if indicators['stoch_k'].iloc[-1] < 20:
            score += 0.3
        elif indicators['stoch_k'].iloc[-1] > 80:
            score -= 0.3
        
        return np.clip(score, -1, 1)
    
    def _volume_score(self, data: pd.DataFrame, indicators: Dict) -> float:
        """Calculate volume analysis score"""
        score = 0
        
        # Volume trend
        avg_volume = data['volume'].rolling(20).mean()
        if data['volume'].iloc[-1] > avg_volume.iloc[-1]:
            score += 0.5
        else:
            score -= 0.3
        
        # Volume price confirmation
        if (data['close'].iloc[-1] > data['close'].iloc[-2]) and (data['volume'].iloc[-1] > data['volume'].iloc[-2]):
            score += 0.5
        elif (data['close'].iloc[-1] < data['close'].iloc[-2]) and (data['volume'].iloc[-1] > data['volume'].iloc[-2]):
            score -= 0.5
        
        return np.clip(score, -1, 1)
    
    def _volatility_score(self, data: pd.DataFrame, indicators: Dict) -> float:
        """Calculate volatility condition score"""
        score = 0
        
        # ATR expansion
        atr_ma = indicators['atr'].rolling(20).mean()
        if indicators['atr'].iloc[-1] > atr_ma.iloc[-1]:
            score += 0.4
        else:
            score -= 0.2
        
        # Bollinger Band width (volatility compression/expansion)
        # Wider bands = more volatile, good for trend following
        if indicators['bb_position'].iloc[-1] > 0.8 or indicators['bb_position'].iloc[-1] < 0.2:
            score += 0.6
        
        return np.clip(score, -1, 1)
    
    def _pattern_score(self, data: pd.DataFrame, indicators: Dict) -> float:
        """Calculate chart pattern recognition score"""
        score = 0
        
        # Check for potential reversal patterns
        # Engulfing pattern detection
        if (data['close'].iloc[-1] > data['open'].iloc[-1] and 
            data['close'].iloc[-1] > data['high'].iloc[-2] and
            data['open'].iloc[-1] < data['low'].iloc[-2]):
            score += 0.5  # Bullish engulfing
        elif (data['close'].iloc[-1] < data['open'].iloc[-1] and 
              data['close'].iloc[-1] < data['low'].iloc[-2] and
              data['open'].iloc[-1] > data['high'].iloc[-2]):
            score -= 0.5  # Bearish engulfing
        
        # Doji detection
        body = abs(data['close'].iloc[-1] - data['open'].iloc[-1])
        range_high_low = data['high'].iloc[-1] - data['low'].iloc[-1]
        if range_high_low > 0 and body / range_high_low < 0.1:
            # Doji with momentum confirmation
            if indicators['rsi'].iloc[-1] < 30:
                score += 0.3
            elif indicators['rsi'].iloc[-1] > 70:
                score -= 0.3
        
        return np.clip(score, -1, 1)
    
    def _count_aligned_indicators(self, indicators: Dict) -> int:
        """Count number of indicators aligned with the dominant direction"""
        aligned = 0
        
        if indicators['ema_fast'].iloc[-1] > indicators['ema_slow'].iloc[-1]:
            aligned += 1
        if indicators['macd_histogram'].iloc[-1] > 0:
            aligned += 1
        if indicators['rsi'].iloc[-1] < 70 and indicators['rsi'].iloc[-1] > 30:
            aligned += 1
        if indicators['stoch_k'].iloc[-1] < 80 and indicators['stoch_k'].iloc[-1] > 20:
            aligned += 1
        
        return aligned
