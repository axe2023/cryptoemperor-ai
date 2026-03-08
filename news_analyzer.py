#!/usr/bin/env python3
"""
新闻情绪分析模块 - 基于 OpenNews 6551 API
"""

import os
import requests
from datetime import datetime

class NewsAnalyzer:
    """新闻情绪分析器"""
    
    def __init__(self, api_token=None):
        """
        初始化新闻分析器
        
        Args:
            api_token: OpenNews API Token
        """
        self.api_token = api_token or os.getenv('OPENNEWS_TOKEN')
        self.base_url = "https://ai.6551.io"
    
    def search_news(self, keyword, limit=10, page=1, coin_filter=None):
        """
        搜索新闻
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            page: 页码
            coin_filter: 币种过滤（如 "BTC"）
        
        Returns:
            dict: 新闻列表和统计信息
        """
        if not self.api_token:
            print("⚠️ OpenNews API Token 未配置")
            return None
        
        url = f"{self.base_url}/open/news_search"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "keyword": keyword,
            "limit": limit,
            "page": page
        }
        
        if coin_filter:
            payload["coin"] = coin_filter
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 新闻搜索失败: {e}")
            return None
    
    def analyze_sentiment(self, symbol, hours=24, limit=20):
        """
        分析币种相关新闻情绪
        
        Args:
            symbol: 交易对（如 "BTCUSDT"）
            hours: 分析最近N小时的新闻
            limit: 分析新闻数量
        
        Returns:
            dict: 情绪分析结果
        """
        # 提取币种代码（BTCUSDT → BTC）
        coin = symbol.replace('USDT', '').replace('BUSD', '')
        
        # 搜索新闻
        result = self.search_news(keyword=coin, limit=limit, coin_filter=coin)
        
        if not result or not result.get('success'):
            return {
                'sentiment_score': 0.0,
                'signal': 'neutral',
                'news_count': 0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0
            }
        
        news_list = result.get('data', [])
        
        # 统计情绪
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        total_score = 0
        
        for news in news_list:
            ai_rating = news.get('aiRating', {})
            signal = ai_rating.get('signal', 'neutral')
            score = ai_rating.get('score', 0)
            
            if signal == 'bullish':
                bullish_count += 1
                total_score += score
            elif signal == 'bearish':
                bearish_count += 1
                total_score -= score
            else:
                neutral_count += 1
        
        # 计算情绪得分（-100 到 100）
        total_news = len(news_list)
        if total_news > 0:
            sentiment_score = (bullish_count - bearish_count) / total_news * 100
        else:
            sentiment_score = 0.0
        
        # 判断整体信号
        if sentiment_score > 30:
            overall_signal = 'bullish'
        elif sentiment_score < -30:
            overall_signal = 'bearish'
        else:
            overall_signal = 'neutral'
        
        return {
            'sentiment_score': sentiment_score,
            'signal': overall_signal,
            'news_count': total_news,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'avg_score': total_score / total_news if total_news > 0 else 0
        }
    
    def get_top_news(self, symbol, limit=5):
        """
        获取币种相关的热门新闻
        
        Args:
            symbol: 交易对
            limit: 返回数量
        
        Returns:
            list: 新闻列表
        """
        coin = symbol.replace('USDT', '').replace('BUSD', '')
        result = self.search_news(keyword=coin, limit=limit, coin_filter=coin)
        
        if not result or not result.get('success'):
            return []
        
        news_list = result.get('data', [])
        
        # 格式化新闻
        formatted_news = []
        for news in news_list:
            ai_rating = news.get('aiRating', {})
            formatted_news.append({
                'title': news.get('text', ''),
                'summary': ai_rating.get('summary', ''),
                'signal': ai_rating.get('signal', 'neutral'),
                'score': ai_rating.get('score', 0),
                'grade': ai_rating.get('grade', 'C'),
                'source': news.get('newsType', ''),
                'link': news.get('link', ''),
                'time': news.get('ts', '')
            })
        
        return formatted_news
