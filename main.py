#!/usr/bin/env python3
"""
CryptoEmperor AI - Minimal Runnable Version
实时价格 + RSI 计算 + 信号输出
"""

import os
import sys
from binance.client import Client
import pandas as pd
import numpy as np
from datetime import datetime

# Binance API 配置
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
BASE_URL = os.getenv('BINANCE_BASE_URL', 'https://api.binance.com')

def get_client():
    """初始化 Binance 客户端"""
    if not API_KEY or not SECRET_KEY:
        print("❌ 错误：未配置 BINANCE_API_KEY 或 BINANCE_SECRET_KEY")
        sys.exit(1)
    
    client = Client(API_KEY, SECRET_KEY, tld='com')
    if BASE_URL != 'https://api.binance.com':
        client.API_URL = BASE_URL
    
    return client

def get_klines(client, symbol, interval='15m', limit=100):
    """获取 K 线数据"""
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def calculate_rsi(prices, period=14):
    """计算 RSI 指标"""
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

def generate_signal(rsi, price, symbol):
    """生成交易信号"""
    if rsi < 30:
        return f"🟢 买入信号 | {symbol} | 价格: ${price:,.2f} | RSI: {rsi:.2f} (超卖)"
    elif rsi > 70:
        return f"🔴 卖出信号 | {symbol} | 价格: ${price:,.2f} | RSI: {rsi:.2f} (超买)"
    else:
        return f"⚪ 观望 | {symbol} | 价格: ${price:,.2f} | RSI: {rsi:.2f} (中性)"

def main():
    """主函数"""
    print("=" * 60)
    print("CryptoEmperor AI - 最小可运行版本")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 初始化客户端
    client = get_client()
    
    # 测试币种
    symbols = ['BTCUSDT', 'ETHUSDT']
    
    for symbol in symbols:
        try:
            # 获取 K 线数据
            df = get_klines(client, symbol, interval='15m', limit=100)
            prices = df['close'].values
            current_price = prices[-1]
            
            # 计算 RSI
            rsi = calculate_rsi(prices, period=14)
            
            # 生成信号
            signal = generate_signal(rsi, current_price, symbol)
            print(signal)
            
        except Exception as e:
            print(f"❌ {symbol} 处理失败: {str(e)}")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
