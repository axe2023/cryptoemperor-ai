#!/usr/bin/env python3
"""
CryptoEmperor AI - 最小可运行版本 v2
实时价格 + RSI 计算 + 信号输出 + 配置化 + 日志
"""

import os
import sys
import yaml
from binance.client import Client
import pandas as pd
import numpy as np
from datetime import datetime
from logger import setup_logger, cleanup_old_logs
from signals import SignalRecorder
from reporter import DailyReporter
from telegram_bot import TelegramBot
from news_analyzer import NewsAnalyzer
from twitter_monitor import TwitterMonitor

def load_config(config_file='config.yaml'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        sys.exit(1)

def get_client():
    """初始化 Binance 客户端"""
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    base_url = os.getenv('BINANCE_BASE_URL', 'https://api.binance.com')
    
    if not api_key or not secret_key:
        print("❌ 错误：未配置 BINANCE_API_KEY 或 BINANCE_SECRET_KEY")
        sys.exit(1)
    
    client = Client(api_key, secret_key, tld='com')
    if base_url != 'https://api.binance.com':
        client.API_URL = base_url
    
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
    df['volume'] = df['volume'].astype(float)
    return df

def get_24h_ticker(client, symbol):
    """获取24h行情数据"""
    ticker = client.get_ticker(symbol=symbol)
    return {
        'price_change_percent': float(ticker['priceChangePercent']),
        'volume': float(ticker['volume']),
        'quote_volume': float(ticker['quoteVolume'])
    }

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

def generate_signal(rsi, price, symbol, config, ticker_24h=None, news_sentiment=None, twitter_sentiment=None):
    """生成交易信号（增强版：RSI + 新闻情绪 + Twitter 情绪）"""
    oversold = config['rsi']['oversold']
    overbought = config['rsi']['overbought']
    
    # 基础 RSI 信号
    if rsi < oversold:
        base_signal = "买入"
        signal_strength = 1
    elif rsi > overbought:
        base_signal = "卖出"
        signal_strength = 1
    else:
        base_signal = "观望"
        signal_strength = 0
    
    # 新闻情绪加权（如果启用）
    if news_sentiment and config.get('sentiment_analysis', {}).get('enable_news', False):
        news_signal = news_sentiment.get('signal', 'neutral')
        news_score = news_sentiment.get('sentiment_score', 0)
        
        if base_signal == "买入" and news_signal == 'bullish':
            signal_strength += 0.5  # 新闻利好，增强买入信号
        elif base_signal == "买入" and news_signal == 'bearish':
            signal_strength -= 0.3  # 新闻利空，减弱买入信号
        elif base_signal == "卖出" and news_signal == 'bearish':
            signal_strength += 0.5  # 新闻利空，增强卖出信号
        elif base_signal == "卖出" and news_signal == 'bullish':
            signal_strength -= 0.3  # 新闻利好，减弱卖出信号
    
    # Twitter 情绪加权（如果启用）
    if twitter_sentiment and config.get('sentiment_analysis', {}).get('enable_twitter', False):
        twitter_signal = twitter_sentiment.get('signal', 'neutral')
        
        if base_signal == "买入" and twitter_signal == 'bullish':
            signal_strength += 0.3
        elif base_signal == "买入" and twitter_signal == 'bearish':
            signal_strength -= 0.2
        elif base_signal == "卖出" and twitter_signal == 'bearish':
            signal_strength += 0.3
        elif base_signal == "卖出" and twitter_signal == 'bullish':
            signal_strength -= 0.2
    
    # 根据信号强度生成最终信号
    if base_signal == "买入":
        if signal_strength >= 1.5:
            signal_type = "🟢🟢 强烈买入"
            reason = f"RSI: {rsi:.2f} (超卖) + 情绪利好"
        elif signal_strength >= 1.0:
            signal_type = "🟢 买入信号"
            reason = f"RSI: {rsi:.2f} (超卖)"
        else:
            signal_type = "⚪ 观望"
            reason = f"RSI: {rsi:.2f} (超卖但情绪不佳)"
    elif base_signal == "卖出":
        if signal_strength >= 1.5:
            signal_type = "🔴🔴 强烈卖出"
            reason = f"RSI: {rsi:.2f} (超买) + 情绪利空"
        elif signal_strength >= 1.0:
            signal_type = "🔴 卖出信号"
            reason = f"RSI: {rsi:.2f} (超买)"
        else:
            signal_type = "⚪ 观望"
            reason = f"RSI: {rsi:.2f} (超买但情绪不差)"
    else:
        signal_type = "⚪ 观望"
        reason = f"RSI: {rsi:.2f} (中性)"
    
    # 构建输出
    output = f"{signal_type} | {symbol} | 价格: ${price:,.2f} | {reason}"
    
    # 可选：24h涨跌幅
    if config['output']['show_24h_change'] and ticker_24h:
        change = ticker_24h['price_change_percent']
        change_emoji = "📈" if change > 0 else "📉"
        output += f" | 24h: {change_emoji} {change:+.2f}%"
    
    # 可选：成交量
    if config['output']['show_volume'] and ticker_24h:
        volume = ticker_24h['quote_volume']
        output += f" | 成交额: ${volume/1e6:.1f}M"
    
    # 可选：情绪分析
    if news_sentiment and config.get('sentiment_analysis', {}).get('enable_news', False):
        output += f" | 新闻: {news_sentiment['signal']} ({news_sentiment['sentiment_score']:.1f})"
    
    if twitter_sentiment and config.get('sentiment_analysis', {}).get('enable_twitter', False):
        output += f" | Twitter: {twitter_sentiment['signal']} ({twitter_sentiment['sentiment_score']:.1f})"
    
    return output, signal_type

def main():
    """主函数"""
    # 加载配置
    config = load_config()
    
    # 设置日志
    log_level = getattr(__import__('logging'), config['logging']['level'])
    logger = setup_logger(
        log_dir=config['logging']['dir'],
        level=log_level
    )
    
    # 清理旧日志
    cleanup_old_logs(
        log_dir=config['logging']['dir'],
        max_files=config['logging']['max_files']
    )
    
    # 初始化信号记录器
    recorder = SignalRecorder(data_dir='data')
    recorder.cleanup_old_signals(days=30)
    
    # 初始化 Telegram Bot
    telegram_bot = TelegramBot()
    
    # 初始化情绪分析器（如果启用）
    news_analyzer = None
    twitter_monitor = None
    
    if config.get('sentiment_analysis', {}).get('enable_news', False):
        news_analyzer = NewsAnalyzer()
        logger.info("新闻情绪分析已启用")
    
    if config.get('sentiment_analysis', {}).get('enable_twitter', False):
        twitter_monitor = TwitterMonitor()
        logger.info("Twitter 情绪分析已启用")
    
    # 输出头部
    print("=" * 80)
    print("CryptoEmperor AI - 最小可运行版本 v2")
    if config['output']['show_timestamp']:
        print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    logger.info("=" * 60)
    logger.info("CryptoEmperor AI 启动")
    logger.info(f"配置: {len(config['symbols'])} 个交易对, RSI({config['rsi']['period']}), 区间: {config['kline']['interval']}")
    
    # 初始化客户端
    client = get_client()
    logger.info("Binance 客户端初始化成功")
    
    # 处理每个交易对
    signals = []
    for symbol in config['symbols']:
        try:
            # 获取 K 线数据
            df = get_klines(
                client, 
                symbol, 
                interval=config['kline']['interval'], 
                limit=config['kline']['limit']
            )
            prices = df['close'].values
            current_price = prices[-1]
            
            # 获取24h行情
            ticker_24h = None
            if config['output']['show_24h_change'] or config['output']['show_volume']:
                ticker_24h = get_24h_ticker(client, symbol)
            
            # 计算 RSI
            rsi = calculate_rsi(prices, period=config['rsi']['period'])
            
            # 情绪分析（如果启用）
            news_sentiment = None
            twitter_sentiment = None
            
            if news_analyzer:
                try:
                    news_sentiment = news_analyzer.analyze_sentiment(symbol, hours=24, limit=10)
                    logger.info(f"{symbol} 新闻情绪: {news_sentiment['signal']} ({news_sentiment['sentiment_score']:.1f})")
                except Exception as e:
                    logger.warning(f"{symbol} 新闻情绪分析失败: {e}")
            
            if twitter_monitor:
                try:
                    twitter_sentiment = twitter_monitor.analyze_kol_sentiment(symbol)
                    logger.info(f"{symbol} Twitter 情绪: {twitter_sentiment['signal']} ({twitter_sentiment['sentiment_score']:.1f})")
                except Exception as e:
                    logger.warning(f"{symbol} Twitter 情绪分析失败: {e}")
            
            # 生成信号（增强版）
            signal_text, signal_type = generate_signal(
                rsi, current_price, symbol, config, ticker_24h, news_sentiment, twitter_sentiment
            )
            
            print(signal_text)
            logger.info(f"{symbol} | {signal_type} | 价格: ${current_price:,.2f} | RSI: {rsi:.2f}")
            
            # 记录信号
            recorder.add_signal(
                symbol=symbol,
                price=current_price,
                rsi=rsi,
                signal_type=signal_type,
                metadata=ticker_24h
            )
            
            # 推送到 Telegram（仅买入/卖出信号）
            telegram_bot.send_signal(symbol, signal_type, current_price, rsi, ticker_24h)
            
            signals.append({
                'symbol': symbol,
                'price': current_price,
                'rsi': rsi,
                'signal': signal_type
            })
            
        except Exception as e:
            error_msg = f"❌ {symbol} 处理失败: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
    
    print("=" * 80)
    logger.info(f"本次扫描完成，共处理 {len(signals)} 个交易对")
    
    # 生成日报
    reporter = DailyReporter(recorder)
    report_file = reporter.save_report(output_dir='reports')
    logger.info(f"日报已生成: {report_file}")
    
    logger.info("=" * 60)

if __name__ == '__main__':
    main()
