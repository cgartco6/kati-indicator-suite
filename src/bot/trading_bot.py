import time
import threading
import schedule
import logging
from datetime import datetime
import ccxt
from src.data.data_loader import DataLoader
from src.signals.signal_generator import SignalGenerator
from src.signals.signal_filter import SignalFilter
from src.bot.risk_manager import RiskManager
from src.bot.order_executor import OrderExecutor
from src.telegram.notifications import TelegramNotifier

class TradingBot:
    """Automated trading bot with real-time signal generation and execution"""
    
    def __init__(self, config: dict, exchange_id: str = 'binance'):
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize components
        self.exchange = self._init_exchange(exchange_id)
        self.data_loader = DataLoader(config)
        self.signal_generator = SignalGenerator(config)
        self.signal_filter = SignalFilter(config)
        self.risk_manager = RiskManager(config)
        self.order_executor = OrderExecutor(self.exchange, config)
        self.notifier = TelegramNotifier()
        
        # State variables
        self.is_running = False
        self.current_position = None
        self.last_signal_time = None
        
    def _setup_logging(self):
        logger = logging.getLogger('TradingBot')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('trading_bot.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _init_exchange(self, exchange_id: str):
        """Initialize exchange connection"""
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'apiKey': self.config['exchange']['api_key'],
            'secret': self.config['exchange']['secret_key'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot' if not self.config['exchange'].get('futures', False) else 'future'
            }
        })
        
        # Set testnet/sandbox mode
        if self.config['exchange'].get('testnet', False):
            exchange.set_sandbox_mode(True)
        
        return exchange
    
    def run(self):
        """Main bot loop"""
        self.is_running = True
        self.logger.info("Trading bot started")
        
        # Schedule tasks
        schedule.every(5).minutes.do(self.analyze_and_trade)
        schedule.every().hour.do(self.update_market_state)
        schedule.every().day.at("00:00").do(self.reset_daily_limits)
        
        # Send startup notification
        self.notifier.send_message("🤖 Trading bot started successfully")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.notifier.send_message(f"❌ Bot error: {str(e)}")
        
    def analyze_and_trade(self):
        """Main trading logic"""
        try:
            # Fetch current data
            symbol = self.config['trading']['symbol']
            data = self.data_loader.fetch_live_data(symbol)
            
            # Generate signal
            signal = self.signal_generator.generate_signal(data)
            
            if signal['direction'] != 0:
                # Filter signal
                if self.signal_filter.should_trade(signal, data):
                    # Check risk limits
                    if self.risk_manager.can_trade(signal['direction']):
                        # Execute trade
                        self.order_executor.execute_signal(signal)
                        
                        # Send notification
                        self.notifier.send_trade_signal(signal)
                        self.logger.info(f"Trade executed: {signal}")
                    else:
                        self.logger.warning("Risk limits exceeded, trade rejected")
                        self.notifier.send_message("⚠️ Trade rejected: Risk limits exceeded")
                else:
                    self.logger.debug("Signal filtered out")
                    
        except Exception as e:
            self.logger.error(f"Error in trading logic: {e}")
    
    def update_market_state(self):
        """Update market regime detection"""
        # Calculate market volatility
        symbol = self.config['trading']['symbol']
        data = self.data_loader.fetch_live_data(symbol)
        
        # Simple market regime detection based on ATR
        atr_ratio = self._calculate_atr_ratio(data)
        if atr_ratio < 0.02:
            market_regime = 'choppy'
        elif atr_ratio > 0.05:
            market_regime = 'high_volatility'
        else:
            market_regime = 'trending'
        
        self.signal_filter.market_regime = market_regime
        self.logger.info(f"Market regime updated: {market_regime}")
    
    def _calculate_atr_ratio(self, data: pd.DataFrame) -> float:
        """Calculate ATR as percentage of price"""
        from src.indicators import calculate_atr
        atr = calculate_atr(data, self.config['indicators']['atr']['period'])
        return (atr.iloc[-1] / data['close'].iloc[-1])
    
    def reset_daily_limits(self):
        """Reset daily loss and position limits"""
        self.risk_manager.reset_daily_limits()
        self.logger.info("Daily risk limits reset")
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        self.order_executor.close_all_positions()
        self.notifier.send_message("🛑 Trading bot stopped")
        self.logger.info("Trading bot stopped")

if __name__ == "__main__":
    import yaml
    
    with open('config/settings.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    bot = TradingBot(config)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()
