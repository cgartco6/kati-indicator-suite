import logging
from datetime import datetime, date

class RiskManager:
    """Manages risk limits and position sizing"""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger('RiskManager')
        
        # Daily tracking
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.daily_losses = 0
        self.last_reset_date = date.today()
        
    def can_trade(self, direction: int) -> bool:
        """
        Check if a trade is allowed based on risk limits
        """
        # Check daily reset
        self._check_daily_reset()
        
        # Check daily loss limit
        if abs(self.daily_pnl) > self.config['risk']['max_daily_loss_usdt']:
            self.logger.warning(f"Daily loss limit reached: {self.daily_pnl}")
            return False
        
        # Check max positions
        if self.daily_trades >= self.config['trading']['max_positions']:
            self.logger.warning("Max daily positions reached")
            return False
        
        # Check drawdown from peak
        if self._current_drawdown() > self.config['risk']['max_drawdown_percent']:
            self.logger.warning("Max drawdown exceeded")
            return False
        
        return True
    
    def update_pnl(self, pnl: float):
        """Update PnL tracking"""
        self.daily_pnl += pnl
        self.daily_trades += 1
        
        if pnl < 0:
            self.daily_losses += 1
            
        self.logger.info(f"Updated daily P&L: {self.daily_pnl}")
    
    def calculate_position_size(self, signal_strength: float, price: float, stop_loss: float) -> float:
        """
        Calculate optimal position size based on:
        1. Signal strength
        2. Account risk limits
        3. Stop loss distance
        """
        max_risk_amount = self.config['risk']['max_position_size_usdt']
        risk_per_trade = max_risk_amount * signal_strength
        
        # Risk per unit based on stop distance
        risk_per_unit = abs(price - stop_loss)
        if risk_per_unit <= 0:
            risk_per_unit = price * 0.01  # Default 1% risk
        
        position_size = risk_per_trade / risk_per_unit
        
        # Apply signal strength scaling
        position_size *= (0.5 + signal_strength * 0.5)
        
        # Cap at maximum position size
        max_position = max_risk_amount / price
        position_size = min(position_size, max_position)
        
        # Minimum position size check
        min_position = 10 / price  # Minimum $10 trade
        position_size = max(position_size, min_position)
        
        return position_size
    
    def _check_daily_reset(self):
        """Reset daily limits if new day"""
        today = date.today()
        if today != self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.daily_losses = 0
            self.last_reset_date = today
            self.logger.info("Daily limits reset")
    
    def _current_drawdown(self) -> float:
        """Calculate current drawdown from peak"""
        # Simplified version - in production, fetch from account history
        return 0.0
    
    def reset_daily_limits(self):
        """Manual reset of daily limits"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.daily_losses = 0
        self.logger.info("Manual reset of daily limits")
