import asyncio
import logging
from datetime import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import yaml
import pandas as pd
from src.signals.signal_generator import SignalGenerator
from src.signals.confluence import ConfluenceAnalyzer
from src.data.data_loader import DataLoader

class SignalBot:
    """Telegram bot for real-time trading signals"""
    
    def __init__(self, config_file: str = 'config/settings.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.bot_token = self.config['telegram']['bot_token']
        self.chat_id = self.config['telegram']['chat_id']
        
        self.signal_generator = SignalGenerator(self.config)
        self.confluence_analyzer = ConfluenceAnalyzer(self.config)
        self.data_loader = DataLoader(self.config)
        
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when /start is issued."""
        await update.message.reply_text(
            "🤖 **Kati Indicator Suite Signal Bot**\n\n"
            "I provide real-time trading signals based on advanced multi-indicator confluence analysis.\n\n"
            "**Available Commands:**\n"
            "/signal - Get current signal\n"
            "/analysis - Get detailed analysis\n"
            "/status - Bot status\n"
            "/help - Show this message\n\n"
            "**Need help?** Check the documentation for setup instructions.",
            parse_mode='Markdown'
        )
    
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send current trading signal"""
        try:
            # Fetch current data
            symbol = self.config['trading']['symbol']
            data = self.data_loader.fetch_live_data(symbol)
            
            # Generate signal
            signal = self.signal_generator.generate_signal(data)
            
            if signal['direction'] == 1:
                emoji = "🟢"
                action = "**BUY / LONG**"
            elif signal['direction'] == -1:
                emoji = "🔴"
                action = "**SELL / SHORT**"
            else:
                emoji = "⚪"
                action = "**NEUTRAL / NO SIGNAL**"
            
            message = f"{emoji} {action}\n\n"
            message += f"**Symbol:** {symbol}\n"
            message += f"**Price:** ${signal['price']:.2f}\n"
            message += f"**Strength:** {signal['strength']:.2%}\n"
            message += f"**Indicators Aligned:** {signal['indicators_aligned']}/5\n\n"
            
            if signal['direction'] != 0:
                message += f"**Stop Loss:** ${signal['stop_loss']:.2f}\n"
                message += f"**Take Profit:** ${signal['take_profit']:.2f}\n"
                message += f"**Risk/Reward:** {abs((signal['take_profit'] - signal['price']) / (signal['price'] - signal['stop_loss'])):.2f}\n"
            
            message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in signal_command: {e}")
            await update.message.reply_text(f"❌ Error generating signal: {str(e)}")
    
    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send detailed technical analysis"""
        try:
            symbol = self.config['trading']['symbol']
            data = self.data_loader.fetch_live_data(symbol)
            
            # Get indicator values
            from src.indicators import calculate_rsi, calculate_macd
            
            rsi = calculate_rsi(data['close'], 14).iloc[-1]
            macd = calculate_macd(data['close'], 12, 26, 9)
            
            message = f"📊 **Detailed Analysis for {symbol}**\n\n"
            message += f"**Current Price:** ${data['close'].iloc[-1]:.2f}\n"
            message += f"**24h Change:** {((data['close'].iloc[-1] - data['open'].iloc[-1]) / data['open'].iloc[-1] * 100):.2f}%\n"
            message += f"**Volume:** {data['volume'].iloc[-1]:,.0f}\n\n"
            message += f"**RSI (14):** {rsi:.1f}\n"
            message += f"**MACD Histogram:** {macd['histogram'].iloc[-1]:.4f}\n\n"
            
            rsi_status = "🟢 Oversold (Bullish)" if rsi < 30 else "🔴 Overbought (Bearish)" if rsi > 70 else "⚪ Neutral"
            macd_status = "🟢 Bullish" if macd['histogram'].iloc[-1] > 0 else "🔴 Bearish"
            
            message += f"**RSI Status:** {rsi_status}\n"
            message += f"**MACD Status:** {macd_status}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error in analysis_command: {e}")
            await update.message.reply_text(f"❌ Error generating analysis: {str(e)}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send bot status"""
        message = "✅ **Bot Status**\n\n"
        message += f"**Symbol:** {self.config['trading']['symbol']}\n"
        message += f"**Timeframe:** {self.config['trading']['timeframe']}\n"
        message += f"**Auto-trading:** {'✅ Enabled' if self.config.get('auto_trade_enabled', False) else '❌ Disabled'}\n"
        message += f"**Risk limit:** ${self.config['risk']['max_position_size_usdt']}\n"
        message += f"**Confluence required:** {self.config['signal_filter']['min_confluence']}/3\n\n"
        message += f"⏰ Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message"""
        await self.start(update, context)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        self.logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ An error occurred. Please try again later.")
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(self.bot_token).build()
        
        # Register commands
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("signal", self.signal_command))
        application.add_handler(CommandHandler("analysis", self.analysis_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Register error handler
        application.add_error_handler(self.error_handler)
        
        # Start the bot
        self.logger.info("Starting signal bot...")
        print("🤖 Kati Indicator Suite Signal Bot started!")
        print("Available commands: /signal, /analysis, /status, /help")
        application.run_polling()

if __name__ == "__main__":
    bot = SignalBot()
    bot.run()
