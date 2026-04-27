#!/usr/bin/env python3
"""Entry point for the Telegram signal bot"""
from src.telegram.signal_bot import SignalBot

if __name__ == "__main__":
    bot = SignalBot()
    bot.run()
