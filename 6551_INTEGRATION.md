# 6551 API 集成说明

CryptoEmperor AI 现已集成 6551 API，支持新闻和 Twitter 情绪分析，增强信号准确性。

## 功能说明

### 新闻情绪分析
- 基于 OpenNews API 搜索币种相关新闻
- AI 自动评分和情绪分析（bullish/bearish/neutral）
- 作为 RSI 信号的辅助判断

### Twitter 情绪分析
- 监控加密 KOL 和币安官方账号
- 分析推文情绪（正面/负面关键词）
- 实时捕捉市场热点

## 配置步骤

### 1. 获取 6551 API Token
访问 https://6551.io/mcp 获取你的 API Token

### 2. 配置环境变量
编辑 `.env` 文件，添加：
```bash
# 6551 API Token（同一个 Token 用于新闻和 Twitter）
OPENNEWS_TOKEN=your_6551_token_here
TWITTER_TOKEN=your_6551_token_here
```

### 3. 启用情绪分析
编辑 `config.yaml`，修改：
```yaml
sentiment_analysis:
  enable_news: true           # 启用新闻情绪分析
  enable_twitter: true        # 启用 Twitter 情绪分析
  news_limit: 10              # 分析新闻数量
  twitter_limit: 50           # 分析推文数量
```

### 4. 运行测试
```bash
python3 main.py
```

## 信号增强逻辑

### 强烈买入（🟢🟢）
- RSI < 30（超卖）
- 新闻情绪 bullish（利好）
- Twitter 情绪 bullish（利好）

### 强烈卖出（🔴🔴）
- RSI > 70（超买）
- 新闻情绪 bearish（利空）
- Twitter 情绪 bearish（利空）

### 观望（⚪）
- RSI 中性，或
- RSI 信号与情绪冲突（如 RSI 超卖但新闻利空）

## 输出示例

```
🟢🟢 强烈买入 | BTCUSDT | 价格: $67,280.40 | RSI: 28.15 (超卖) + 情绪利好 | 24h: 📉 -0.83% | 成交额: $965.9M | 新闻: bullish (45.2) | Twitter: bullish (32.1)
```

## API 额度管理

- 每次扫描消耗：1-2 额度（取决于币种数量）
- 建议每日扫描次数：5-10 次
- 月消耗估算：150-300 额度

## 注意事项

1. **API Token 安全**：不要将 Token 提交到 Git 仓库
2. **额度监控**：定期检查 https://6551.io/mcp 的额度使用情况
3. **可选功能**：情绪分析是可选的，不启用也不影响基础功能
4. **网络要求**：需要稳定的网络连接访问 6551 API

## 故障排查

### 问题：API 返回 401 Unauthorized
**解决**：检查 Token 是否正确配置，确保 `OPENNEWS_TOKEN` 和 `TWITTER_TOKEN` 已设置

### 问题：情绪分析失败
**解决**：
1. 检查网络连接
2. 确认 6551 API 额度是否充足
3. 查看日志文件 `logs/YYYY-MM-DD.log` 获取详细错误信息

### 问题：信号没有情绪信息
**解决**：确认 `config.yaml` 中 `sentiment_analysis.enable_news` 和 `enable_twitter` 已设置为 `true`

## 禁用情绪分析

如果不需要情绪分析功能，只需在 `config.yaml` 中设置：
```yaml
sentiment_analysis:
  enable_news: false
  enable_twitter: false
```

系统将回退到纯 RSI 信号模式。
