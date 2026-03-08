# 6551 API 快速启用指南

## 🚀 5 分钟启用情绪分析

### 步骤 1：确认环境变量已配置
```bash
# 检查 Token 是否已设置
echo $OPENNEWS_TOKEN
echo $TWITTER_TOKEN
```

如果输出为空，运行：
```bash
source ~/.zshrc
```

### 步骤 2：启用情绪分析
编辑 `config.yaml`：
```yaml
sentiment_analysis:
  enable_news: true           # 改为 true
  enable_twitter: true        # 改为 true
  news_limit: 10
  twitter_limit: 50
```

### 步骤 3：运行测试
```bash
cd ~/.openclaw/workspace/cryptoemperor-ai
python3 main.py
```

### 预期输出
```
2026-03-08 16:50:00 | INFO | 新闻情绪分析已启用
2026-03-08 16:50:00 | INFO | Twitter 情绪分析已启用
2026-03-08 16:50:01 | INFO | BTCUSDT 新闻情绪: neutral (0.0)
2026-03-08 16:50:02 | INFO | BTCUSDT Twitter 情绪: neutral (16.7)
🟢 买入信号 | BTCUSDT | 价格: $67,280.40 | RSI: 28.15 (超卖) | 新闻: neutral (0.0) | Twitter: neutral (16.7)
```

## 📊 信号增强示例

### 场景 1：强烈买入
```
输入:
- RSI: 25 (超卖)
- 新闻情绪: bullish (45.2)
- Twitter 情绪: bullish (32.1)

输出:
🟢🟢 强烈买入 | BTCUSDT | 价格: $67,280.40 | RSI: 25.00 (超卖) + 情绪利好
```

### 场景 2：情绪冲突 → 观望
```
输入:
- RSI: 25 (超卖)
- 新闻情绪: bearish (-35.8)
- Twitter 情绪: bearish (-28.3)

输出:
⚪ 观望 | BTCUSDT | 价格: $67,280.40 | RSI: 25.00 (超卖但情绪不佳)
```

## 🔧 故障排查

### 问题：日志显示"新闻情绪分析失败"
**原因**：API Token 未配置或网络问题

**解决**：
```bash
# 1. 检查 Token
echo $OPENNEWS_TOKEN

# 2. 如果为空，重新配置
export OPENNEWS_TOKEN="your_token_here"

# 3. 测试 API
curl -s -H "Authorization: Bearer $OPENNEWS_TOKEN" "https://ai.6551.io/open/news_type" | head -20
```

### 问题：额度不足
**解决**：访问 https://6551.io/mcp 充值或调整扫描频率

### 问题：想禁用情绪分析
**解决**：编辑 `config.yaml`，设置 `enable_news: false` 和 `enable_twitter: false`

## 📈 额度优化建议

### 当前配置（默认）
- 每次扫描 4 个币种
- 每个币种消耗约 0.5 额度
- 每次扫描总消耗：约 2 额度

### 优化方案 1：减少币种
编辑 `config.yaml`：
```yaml
symbols:
  - BTCUSDT  # 只监控 BTC
```
每次扫描消耗：约 0.5 额度

### 优化方案 2：减少扫描频率
编辑 `scheduler.py`：
```python
config = {
    'scan_times': ['09:00', '15:00', '21:00'],  # 从 5 次减少到 3 次
    'report_time': '22:00'
}
```
每日消耗：约 6 额度（3 次 × 2 额度）

### 优化方案 3：仅在关键时刻启用
手动运行时启用情绪分析，定时任务禁用：
```yaml
sentiment_analysis:
  enable_news: false  # 定时任务禁用
  enable_twitter: false
```

手动运行时临时启用：
```bash
# 临时启用
sed -i '' 's/enable_news: false/enable_news: true/' config.yaml
python3 main.py
# 运行后恢复
sed -i '' 's/enable_news: true/enable_news: false/' config.yaml
```

## 🎯 推荐配置

### 保守型（月消耗 < 100 额度）
- 监控 1-2 个币种
- 每日扫描 3 次
- 仅启用新闻情绪分析

### 平衡型（月消耗 150-300 额度）
- 监控 4 个币种
- 每日扫描 5 次
- 同时启用新闻和 Twitter 分析

### 激进型（月消耗 > 500 额度）
- 监控 10+ 个币种
- 每日扫描 10+ 次
- 全功能启用

---

**当前你的配置**：平衡型（月消耗约 300 额度）
**剩余额度**：29,997（足够使用 100 个月）
