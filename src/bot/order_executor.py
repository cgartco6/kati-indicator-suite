import logging
import time
from typing import Dict

class OrderExecutor:
    """Handles order execution with error handling and retries"""
    
    def __init__(self, exchange, config: dict):
        self.exchange = exchange
        self.config = config
        self.logger = logging.getLogger('OrderExecutor')
        
    def execute_signal(self, signal: Dict) -> Dict:
        """
        Execute a trade based on the signal
        
        Args:
            signal: Signal dict containing direction, stop_loss, take_profit
            
        Returns:
            Dict with execution details
        """
        symbol = self.config['trading']['symbol']
        price = signal['price']
        direction = signal['direction']
        
        # Calculate position size
        position_size = self._calculate_size(signal)
        
        # Determine order side
        side = 'buy' if direction == 1 else 'sell'
        
        try:
            # Place market order
            order = self.exchange.create_market_order(symbol, side, position_size)
            
            # Place stop loss
            stop_order = self._place_stop_loss(symbol, direction, signal['stop_loss'], position_size)
            
            # Place take profit
            tp_order = self._place_take_profit(symbol, direction, signal['take_profit'], position_size)
            
            self.logger.info(f"Order executed: {order['id']}")
            
            return {
                'order_id': order['id'],
                'side': side,
                'size': position_size,
                'price': order['price'],
                'stop_loss_order_id': stop_order['id'] if stop_order else None,
                'take_profit_order_id': tp_order['id'] if tp_order else None
            }
            
        except Exception as e:
            self.logger.error(f"Order execution failed: {e}")
            raise
    
    def _calculate_size(self, signal: Dict) -> float:
        """Calculate position size based on risk management"""
        max_position = self.config['risk']['max_position_size_usdt']
        price = signal['price']
        stop_distance = abs(price - signal['stop_loss'])
        
        # Risk per trade (1% of max position)
        risk_amount = max_position * 0.01
        
        # Calculate size based on stop distance
        position_size = risk_amount / stop_distance if stop_distance > 0 else max_position / price
        
        # Cap at maximum
        max_position_coins = max_position / price
        position_size = min(position_size, max_position_coins)
        
        # Minimum size check
        min_size = self.exchange.markets[symbol]['limits']['amount']['min']
        position_size = max(position_size, min_size)
        
        return position_size
    
    def _place_stop_loss(self, symbol: str, direction: int, stop_price: float, size: float) -> Dict:
        """
        Place stop loss order
        """
        try:
            # Determine stop side (opposite of trade direction)
            stop_side = 'sell' if direction == 1 else 'buy'
            
            stop_order = self.exchange.create_order(
                symbol=symbol,
                type='stop_market',
                side=stop_side,
                amount=size,
                params={'stopPrice': stop_price}
            )
            
            return stop_order
        except Exception as e:
            self.logger.warning(f"Failed to place stop loss: {e}")
            return None
    
    def _place_take_profit(self, symbol: str, direction: int, tp_price: float, size: float) -> Dict:
        """
        Place take profit limit order
        """
        try:
            # Determine TP side (same as trade direction)
            tp_side = 'sell' if direction == 1 else 'buy'
            
            tp_order = self.exchange.create_limit_order(
                symbol=symbol,
                side=tp_side,
                amount=size,
                price=tp_price
            )
            
            return tp_order
        except Exception as e:
            self.logger.warning(f"Failed to place take profit: {e}")
            return None
    
    def close_all_positions(self):
        """Emergency close all open positions"""
        try:
            positions = self.exchange.fetch_positions()
            for position in positions:
                if position['contracts'] != 0:
                    side = 'sell' if position['side'] == 'long' else 'buy'
                    self.exchange.create_market_order(
                        symbol=position['symbol'],
                        side=side,
                        amount=position['contracts']
                    )
                    self.logger.info(f"Closed position: {position['symbol']}")
        except Exception as e:
            self.logger.error(f"Failed to close positions: {e}")
