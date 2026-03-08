#!/usr/bin/env python3
"""
Telegram Bot 集成 - 信号推送和日报通知
"""

import os
import requests
from datetime import datetime

class TelegramBot:
    """Telegram Bot 推送器"""
    
    def __init__(self, bot_token=None, chat_id=None):
        """
        初始化 Telegram Bot
        
        Args:
            bot_token: Bot Token (从 @BotFather 获取)
            chat_id: 目标聊天 ID
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text, parse_mode='Markdown', disable_notification=False):
        """
        发送文本消息
        
        Args:
            text: 消息文本
            parse_mode: 解析模式 (Markdown/HTML)
            disable_notification: 是否静默推送
        
        Returns:
            bool: 是否发送成功
        """
        if not self.bot_token or not self.chat_id:
            print("⚠️ Telegram Bot 未配置，跳过推送")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_notification': disable_notification
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Telegram 推送失败: {e}")
            return False
    
    def send_signal(self, symbol, signal_type, price, rsi, metadata=None):
        """
        发送交易信号
        
        Args:
            symbol: 交易对
            signal_type: 信号类型
            price: 价格
            rsi: RSI 值
            metadata: 额外元数据
        """
        # 信号图标
        if '买入' in signal_type:
            icon = "🟢"
            emoji = "📈"
        elif '卖出' in signal_type:
            icon = "🔴"
            emoji = "📉"
        else:
            icon = "⚪"
            emoji = "➡️"
        
        # 构建消息
        text = f"{icon} *{signal_type}*\n\n"
        text += f"*交易对*: `{symbol}`\n"
        text += f"*价格*: ${price:,.2f}\n"
        text += f"*RSI*: {rsi:.2f}\n"
        
        # 额外信息
        if metadata:
            if 'price_change_percent' in metadata:
                change = metadata['price_change_percent']
                change_emoji = "📈" if change > 0 else "📉"
                text += f"*24h 涨跌*: {change_emoji} {change:+.2f}%\n"
            
            if 'volume' in metadata:
                volume = metadata['volume'] / 1e6
                text += f"*成交额*: ${volume:.1f}M\n"
        
        text += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 只推送买入/卖出信号，观望不推送
        if '观望' not in signal_type:
            return self.send_message(text)
        return False
    
    def send_daily_report(self, report_file):
        """
        发送日报
        
        Args:
            report_file: 日报文件路径
        
        Returns:
            bool: 是否发送成功
        """
        if not os.path.exists(report_file):
            print(f"❌ 日报文件不存在: {report_file}")
            return False
        
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Telegram 消息长度限制 4096 字符
            if len(content) > 4000:
                # 分段发送
                parts = [content[i:i+4000] for i in range(0, len(content), 4000)]
                for i, part in enumerate(parts):
                    self.send_message(f"📊 *日报 ({i+1}/{len(parts)})*\n\n{part}")
            else:
                self.send_message(f"📊 *CryptoEmperor AI 日报*\n\n{content}")
            
            return True
        except Exception as e:
            print(f"❌ 日报推送失败: {e}")
            return False
    
    def send_alert(self, title, message, level='INFO'):
        """
        发送告警消息
        
        Args:
            title: 标题
            message: 消息内容
            level: 级别 (INFO/WARNING/ERROR)
        """
        # 级别图标
        icons = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '🚨'
        }
        icon = icons.get(level, 'ℹ️')
        
        text = f"{icon} *{title}*\n\n{message}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 错误级别不静默
        disable_notification = (level == 'INFO')
        
        return self.send_message(text, disable_notification=disable_notification)
    
    def send_risk_alert(self, alert_type, details):
        """
        发送风控告警
        
        Args:
            alert_type: 告警类型 (stop_loss/daily_loss_limit/position_limit)
            details: 详情字典
        """
        alerts = {
            'stop_loss': '🛑 *止损触发*',
            'daily_loss_limit': '🚨 *日亏损闸门触发*',
            'position_limit': '⚠️ *仓位超限*'
        }
        
        title = alerts.get(alert_type, '⚠️ *风控告警*')
        
        message = ""
        for key, value in details.items():
            message += f"*{key}*: {value}\n"
        
        return self.send_alert(title, message, level='WARNING')
