#!/usr/bin/env python3
import yaml
from src.bot.trading_bot import TradingBot

if __name__ == "__main__":
    with open('config/settings.yaml', 'r') as f:
        config = yaml.safe_load(f)
    bot = TradingBot(config)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()
