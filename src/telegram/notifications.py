import requests
import logging
from typing import Dict

class TelegramNotifier:
    """Simple Telegram notification sender"""
    
    def __init__(self, config_file: str = 'config/settings.yaml'):
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.bot_token = config['telegram']['bot_token']
        self.chat_id = config['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.logger = logging.getLogger('TelegramNotifier')
    
    def send_message(self, message: str) -> bool:
        """Send plain text message"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def send_trade_signal(self, signal: Dict) -> bool:
        """Send formatted trade signal"""
        if signal['direction'] == 1:
            emoji = "🟢"
            action = "**BUY / LONG**"
        elif signal['direction'] == -1:
            emoji = "🔴"
            action = "**SELL / SHORT**"
        else:
            return False
        
        message = f"{emoji} {action}\n\n"
        message += f"**Price:** ${signal['price']:.2f}\n"
        message += f"**Strength:** {signal['strength']:.2%}\n"
        message += f"**Confidence:** {signal['indicators_aligned']}/5\n\n"
        message += f"**Stop Loss:** ${signal['stop_loss']:.2f}\n"
        message += f"**Take Profit:** ${signal['take_profit']:.2f}\n"
        
        return self.send_message(message)
    
    def send_alert(self, title: str, content: str, alert_type: str = 'info') -> bool:
        """Send alert notification"""
        if alert_type == 'error':
            emoji = "❌"
        elif alert_type == 'warning':
            emoji = "⚠️"
        elif alert_type == 'success':
            emoji = "✅"
        else:
            emoji = "ℹ️"
        
        message = f"{emoji} **{title}**\n\n{content}"
        return self.send_message(message)
    
    def send_chart(self, chart_path: str, caption: str = None) -> bool:
        """Send chart image"""
        try:
            url = f"{self.base_url}/sendPhoto"
            with open(chart_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': self.chat_id}
                if caption:
                    data['caption'] = caption
                response = requests.post(url, files=files, data=data)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send chart: {e}")
            return False
