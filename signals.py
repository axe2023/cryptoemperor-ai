#!/usr/bin/env python3
"""
信号历史记录模块 - 持久化交易信号
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SignalRecorder:
    """信号记录器"""
    
    def __init__(self, data_dir='data'):
        """
        初始化信号记录器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        self.signals_file = os.path.join(data_dir, 'signals.json')
        self.signals = self._load_signals()
    
    def _load_signals(self):
        """加载历史信号"""
        if os.path.exists(self.signals_file):
            try:
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载信号历史失败: {e}")
                return []
        return []
    
    def _save_signals(self):
        """保存信号到文件"""
        try:
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(self.signals, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存信号失败: {e}")
    
    def add_signal(self, symbol, price, rsi, signal_type, metadata=None):
        """
        添加新信号
        
        Args:
            symbol: 交易对
            price: 当前价格
            rsi: RSI值
            signal_type: 信号类型 (买入/卖出/观望)
            metadata: 额外元数据 (24h涨跌幅、成交量等)
        """
        signal = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'signal': signal_type,
            'metadata': metadata or {}
        }
        
        self.signals.append(signal)
        self._save_signals()
    
    def get_signals_by_date(self, date_str=None):
        """
        获取指定日期的信号
        
        Args:
            date_str: 日期字符串 (YYYY-MM-DD)，默认今天
        
        Returns:
            list: 信号列表
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        return [
            s for s in self.signals 
            if s['timestamp'].startswith(date_str)
        ]
    
    def get_signals_by_symbol(self, symbol, days=7):
        """
        获取指定交易对最近N天的信号
        
        Args:
            symbol: 交易对
            days: 天数
        
        Returns:
            list: 信号列表
        """
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        return [
            s for s in self.signals 
            if s['symbol'] == symbol and s['timestamp'] >= cutoff
        ]
    
    def get_signal_stats(self, days=7):
        """
        获取信号统计
        
        Args:
            days: 统计天数
        
        Returns:
            dict: 统计数据
        """
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        recent_signals = [s for s in self.signals if s['timestamp'] >= cutoff]
        
        stats = {
            'total': len(recent_signals),
            'buy': 0,
            'sell': 0,
            'hold': 0,
            'by_symbol': {}
        }
        
        for signal in recent_signals:
            signal_type = signal['signal']
            if '买入' in signal_type:
                stats['buy'] += 1
            elif '卖出' in signal_type:
                stats['sell'] += 1
            else:
                stats['hold'] += 1
            
            symbol = signal['symbol']
            if symbol not in stats['by_symbol']:
                stats['by_symbol'][symbol] = {'buy': 0, 'sell': 0, 'hold': 0}
            
            if '买入' in signal_type:
                stats['by_symbol'][symbol]['buy'] += 1
            elif '卖出' in signal_type:
                stats['by_symbol'][symbol]['sell'] += 1
            else:
                stats['by_symbol'][symbol]['hold'] += 1
        
        return stats
    
    def cleanup_old_signals(self, days=30):
        """
        清理旧信号
        
        Args:
            days: 保留最近N天的信号
        """
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        old_count = len(self.signals)
        self.signals = [s for s in self.signals if s['timestamp'] >= cutoff]
        new_count = len(self.signals)
        
        if old_count > new_count:
            self._save_signals()
            print(f"🗑️ 清理了 {old_count - new_count} 条旧信号")
