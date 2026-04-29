#!/usr/bin/env python3
import asyncio
import sys
from dotenv import load_dotenv
load_dotenv()

# Fix for Windows asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from src.telegram.signal_bot import SignalBot

if __name__ == "__main__":
    bot = SignalBot()
    bot.run()
