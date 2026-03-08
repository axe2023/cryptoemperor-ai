#!/usr/bin/env python3
"""
Twitter 监控模块 - 基于 OpenTwitter 6551 API
"""

import os
import requests
from datetime import datetime

class TwitterMonitor:
    """Twitter KOL 监控器"""
    
    def __init__(self, api_token=None):
        """
        初始化 Twitter 监控器
        
        Args:
            api_token: OpenTwitter API Token
        """
        self.api_token = api_token or os.getenv('TWITTER_TOKEN')
        self.base_url = "https://ai.6551.io"
        
        # 预定义的加密 KOL 列表
        self.kol_list = [
            'binance',           # 币安官方
            'cz_binance',        # CZ
            'VitalikButerin',    # Vitalik
            'elonmusk',          # Elon Musk
            'CoinDesk',          # CoinDesk
            'Cointelegraph'      # Cointelegraph
        ]
    
    def get_user_info(self, username):
        """
        获取 Twitter 用户信息
        
        Args:
            username: Twitter 用户名
        
        Returns:
            dict: 用户信息
        """
        if not self.api_token:
            print("⚠️ OpenTwitter API Token 未配置")
            return None
        
        url = f"{self.base_url}/open/twitter_user_info"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {"username": username}
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result.get('data', {})
        except Exception as e:
            print(f"❌ 获取用户信息失败 ({username}): {e}")
            return None
    
    def search_tweets(self, keyword, limit=20):
        """
        搜索推文
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
        
        Returns:
            list: 推文列表
        """
        if not self.api_token:
            print("⚠️ OpenTwitter API Token 未配置")
            return []
        
        url = f"{self.base_url}/open/twitter_search"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "keywords": keyword,  # 注意：是 keywords 不是 keyword
            "maxResults": limit,
            "product": "Top"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            # 注意：返回的是 data 数组，不是 data.tweets
            return result.get('data', [])
        except Exception as e:
            print(f"❌ 搜索推文失败: {e}")
            return []
    
    def analyze_kol_sentiment(self, symbol, kol_usernames=None):
        """
        分析 KOL 对币种的情绪
        
        Args:
            symbol: 交易对（如 "BTCUSDT"）
            kol_usernames: KOL 用户名列表（默认使用预定义列表）
        
        Returns:
            dict: 情绪分析结果
        """
        coin = symbol.replace('USDT', '').replace('BUSD', '')
        kol_list = kol_usernames or self.kol_list
        
        # 搜索相关推文
        tweets = self.search_tweets(keyword=coin, limit=50)
        
        if not tweets:
            return {
                'sentiment_score': 0.0,
                'signal': 'neutral',
                'tweet_count': 0,
                'positive_count': 0,
                'negative_count': 0
            }
        
        # 简单情绪分析（基于关键词）
        positive_keywords = ['bullish', 'moon', 'pump', 'buy', 'long', 'up', '🚀', '📈', '💎']
        negative_keywords = ['bearish', 'dump', 'sell', 'short', 'down', 'crash', '📉', '⚠️']
        
        positive_count = 0
        negative_count = 0
        
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            
            # 检查正面关键词
            if any(keyword in text for keyword in positive_keywords):
                positive_count += 1
            
            # 检查负面关键词
            if any(keyword in text for keyword in negative_keywords):
                negative_count += 1
        
        # 计算情绪得分
        total_tweets = len(tweets)
        sentiment_score = (positive_count - negative_count) / total_tweets * 100 if total_tweets > 0 else 0.0
        
        # 判断信号
        if sentiment_score > 20:
            signal = 'bullish'
        elif sentiment_score < -20:
            signal = 'bearish'
        else:
            signal = 'neutral'
        
        return {
            'sentiment_score': sentiment_score,
            'signal': signal,
            'tweet_count': total_tweets,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def get_trending_topics(self, symbol):
        """
        获取币种相关的热门话题
        
        Args:
            symbol: 交易对
        
        Returns:
            list: 热门推文列表
        """
        coin = symbol.replace('USDT', '').replace('BUSD', '')
        tweets = self.search_tweets(keyword=coin, limit=10)
        
        # 格式化推文
        formatted_tweets = []
        for tweet in tweets:
            formatted_tweets.append({
                'text': tweet.get('text', ''),
                'author': tweet.get('author', {}).get('username', ''),
                'likes': tweet.get('likeCount', 0),
                'retweets': tweet.get('retweetCount', 0),
                'time': tweet.get('createdAt', '')
            })
        
        return formatted_tweets
