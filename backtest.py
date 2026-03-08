#!/usr/bin/env python3
"""
回测引擎 - 验证策略历史表现
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Backtester:
    """回测引擎"""
    
    def __init__(self, initial_capital=10000.0):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
    
    def calculate_rsi(self, prices, period=14):
        """计算 RSI"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def run_backtest(self, client, symbol, start_date, end_date, 
                     rsi_period=14, oversold=30, overbought=70, 
                     interval='15m'):
        """
        运行回测
        
        Args:
            client: Binance 客户端
            symbol: 交易对
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            rsi_period: RSI 周期
            oversold: 超卖阈值
            overbought: 超买阈值
            interval: K线周期
        
        Returns:
            dict: 回测结果
        """
        # 获取历史数据
        klines = client.get_historical_klines(
            symbol, 
            interval, 
            start_date, 
            end_date
        )
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 计算 RSI
        prices = df['close'].values
        
        # 回测循环
        for i in range(rsi_period + 1, len(prices)):
            current_price = prices[i]
            current_time = df.iloc[i]['timestamp']
            
            # 计算当前 RSI
            rsi = self.calculate_rsi(prices[i-rsi_period-1:i], period=rsi_period)
            
            # 交易逻辑
            if symbol not in self.positions:
                # 无持仓，检查买入信号
                if rsi < oversold:
                    # 买入
                    quantity = self.capital / current_price
                    self.positions[symbol] = {
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'quantity': quantity
                    }
                    self.trades.append({
                        'time': current_time,
                        'type': 'BUY',
                        'price': current_price,
                        'quantity': quantity,
                        'rsi': rsi
                    })
            else:
                # 有持仓，检查卖出信号
                if rsi > overbought:
                    # 卖出
                    position = self.positions[symbol]
                    quantity = position['quantity']
                    entry_price = position['entry_price']
                    
                    pnl = (current_price - entry_price) * quantity
                    self.capital += pnl
                    
                    self.trades.append({
                        'time': current_time,
                        'type': 'SELL',
                        'price': current_price,
                        'quantity': quantity,
                        'rsi': rsi,
                        'pnl': pnl,
                        'return_pct': (current_price - entry_price) / entry_price * 100
                    })
                    
                    del self.positions[symbol]
            
            # 记录权益曲线
            current_equity = self.capital
            if symbol in self.positions:
                current_equity += self.positions[symbol]['quantity'] * current_price
            
            self.equity_curve.append({
                'time': current_time,
                'equity': current_equity
            })
        
        # 计算回测指标
        return self._calculate_metrics()
    
    def _calculate_metrics(self):
        """计算回测指标"""
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0.0,
                'total_return': 0.0,
                'max_drawdown': 0.0
            }
        
        # 统计交易
        sell_trades = [t for t in self.trades if t['type'] == 'SELL']
        total_trades = len(sell_trades)
        winning_trades = len([t for t in sell_trades if t['pnl'] > 0])
        
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0.0
        
        # 总收益
        final_equity = self.equity_curve[-1]['equity'] if self.equity_curve else self.initial_capital
        total_return = (final_equity - self.initial_capital) / self.initial_capital * 100
        
        # 最大回撤
        equity_values = [e['equity'] for e in self.equity_curve]
        peak = equity_values[0]
        max_drawdown = 0.0
        
        for equity in equity_values:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': total_trades - winning_trades,
            'win_rate': win_rate,
            'total_return': total_return,
            'final_equity': final_equity,
            'max_drawdown': max_drawdown,
            'trades': sell_trades
        }
