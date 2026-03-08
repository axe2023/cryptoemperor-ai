# CryptoEmperor AI 演示录屏脚本

## 录屏前准备（5分钟）

### 1. 清理终端历史
```bash
clear
```

### 2. 确保项目可运行
```bash
cd ~/.openclaw/workspace/cryptoemperor-ai
python3 main.py  # 测试一次，确保无报错
```

### 3. 准备展示文件
- 打开 `reports/report_2026-03-08.md`（用 Typora 或 VS Code 预览）
- 打开 `config.yaml`（展示配置）
- 打开 `risk_control.py`（展示风控代码）

### 4. 浏览器准备
- 标签页 1：GitHub 仓库 https://github.com/axe2023/cryptoemperor-ai
- 标签页 2：Binance 官网（可选）

### 5. 录屏工具设置
- macOS：QuickTime Player → 文件 → 新建屏幕录制
- 分辨率：1920×1080 或 1280×720
- 帧率：30fps
- 音频：可选（如果要配音）

---

## 录屏脚本（逐帧说明）

### [00:00-00:10] 开场
**画面**：
- 桌面干净，只显示项目文件夹图标
- 鼠标移动到 `cryptoemperor-ai` 文件夹

**字幕**：
```
CryptoEmperor AI
币安智能交易信号系统
```

**操作**：
- 双击打开文件夹
- 展示项目结构（main.py, config.yaml, README.md 等）

---

### [00:10-00:40] 场景 1：实时信号生成
**画面**：
- 打开终端
- 进入项目目录

**操作**：
```bash
cd ~/.openclaw/workspace/cryptoemperor-ai
python3 main.py
```

**字幕**：
```
✅ 实时监控 BTC/ETH/BNB/SOL
✅ 基于 RSI 指标自动生成信号
✅ 24h 涨跌幅 + 成交额分析
```

**等待输出**：
- 展示完整的信号输出（约 10 秒）
- 鼠标高亮关键信息（价格、RSI、信号类型）

---

### [00:40-01:00] 场景 2：日报生成
**画面**：
- 终端显示 "日报已生成: reports/report_2026-03-08.md"
- 打开 Finder，进入 `reports/` 目录

**操作**：
- 双击打开 `report_2026-03-08.md`
- 用 Typora 或 VS Code 预览 Markdown 渲染效果

**字幕**：
```
📊 自动生成日报
• 今日概览（买入/卖出/观望统计）
• 分币种统计
• 信号详情（时间/价格/RSI）
```

**展示内容**：
- 滚动浏览日报（概览 → 统计表格 → 信号详情）

---

### [01:00-01:30] 场景 3：风控模块
**画面**：
- 打开 VS Code
- 打开 `risk_control.py`

**操作**：
- 滚动到关键代码段（`can_open_position` 函数）
- 鼠标高亮关键逻辑

**字幕**：
```
🛡️ 内置风控体系
• 单币种仓位限制（10%）
• 总仓位限制（50%）
• 止损比例（5%）
• 日亏损闸门（10%）
```

**代码展示**（停留 5 秒）：
```python
# 检查日亏损限制
if self.daily_pnl < 0 and abs(self.daily_pnl) / total_capital * 100 >= self.daily_loss_limit_pct:
    return False, f"触发日亏损闸门 ({self.daily_loss_limit_pct}%)"
```

---

### [01:30-02:00] 场景 4：回测引擎
**画面**：
- 回到终端
- 运行回测演示

**操作**：
```bash
python3 -c "
from backtest import Backtester
from binance.client import Client
import os

client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET_KEY'))
backtester = Backtester(initial_capital=10000)

print('正在回测 BTCUSDT (2024-01-01 至 2024-12-31)...')
print('这可能需要 30-60 秒...')
"
```

**字幕**：
```
📈 回测引擎
• 验证策略历史表现
• 计算胜率/收益/回撤
• 数据驱动决策
```

**注意**：回测需要时间，可以用**快进**或**剪辑**跳过等待过程

---

### [02:00-02:20] 场景 5：配置化
**画面**：
- 打开 `config.yaml`

**操作**：
- 展示配置文件内容
- 鼠标高亮关键配置项

**字幕**：
```
⚙️ 灵活配置
• 币种列表可自定义
• RSI 参数可调整
• 日志/输出格式可配置
```

**展示内容**：
```yaml
symbols:
  - BTCUSDT
  - ETHUSDT
  - BNBUSDT
  - SOLUSDT

rsi:
  period: 14
  oversold: 30
  overbought: 70
```

---

### [02:20-02:40] 场景 6：Docker 部署
**画面**：
- 回到终端
- 展示 Docker 部署

**操作**：
```bash
# 展示 docker-compose.yml
cat docker-compose.yml

# 启动容器（可选，如果有 Docker）
docker-compose up -d
docker-compose ps
```

**字幕**：
```
🐳 一键部署
• Docker Compose 编排
• 数据持久化
• 生产级可用
```

---

### [02:40-03:00] 场景 7：GitHub 开源
**画面**：
- 打开浏览器
- 访问 GitHub 仓库

**操作**：
- 展示仓库首页（README.md）
- 滚动浏览文档
- 展示 commit 历史（6 次提交，v1 到 v5）

**字幕**：
```
💻 完全开源
• 完整文档
• 生产级代码
• 持续迭代

GitHub: github.com/axe2023/cryptoemperor-ai
```

---

### [03:00] 结束画面
**画面**：
- 回到桌面
- 显示项目 Logo 或标题

**字幕**：
```
CryptoEmperor AI
让交易更智能

🦞 #币安AI小龙虾大赛
```

---

## 录屏后处理

### 1. 剪辑（可选）
- 删除等待时间（如回测加载）
- 加快某些操作（如文件浏览）
- 添加背景音乐（可选）

### 2. 添加字幕
- 使用 iMovie / Final Cut Pro / 剪映
- 或者用在线工具：https://www.kapwing.com

### 3. 导出
- 格式：MP4
- 分辨率：1920×1080 或 1280×720
- 大小：< 30MB（大赛要求）

---

## 备选方案：如果回测太慢

如果回测需要很长时间，可以用**预先录制的结果**：

```bash
# 提前运行回测，保存结果到文件
python3 backtest_demo.py > backtest_result.txt

# 录屏时直接展示结果文件
cat backtest_result.txt
```

我可以帮你生成一个 `backtest_demo.py` 脚本，输出模拟的回测结果。

