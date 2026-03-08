#!/bin/bash
# CryptoEmperor AI 一键演示脚本（用于录屏）

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CryptoEmperor AI - 完整功能演示${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
sleep 2

# 场景 1：实时信号生成
echo -e "${BLUE}📊 场景 1：实时信号生成${NC}"
echo -e "${YELLOW}正在扫描 BTC/ETH/BNB/SOL...${NC}"
echo ""
sleep 1

python3 main.py

echo ""
sleep 2

# 场景 2：日报预览
echo -e "${BLUE}📋 场景 2：今日日报预览${NC}"
echo ""
sleep 1

head -40 reports/report_$(date '+%Y-%m-%d').md

echo ""
echo -e "${GREEN}✅ 完整日报已保存到 reports/ 目录${NC}"
echo ""
sleep 2

# 场景 3：回测演示
echo -e "${BLUE}📈 场景 3：策略回测验证${NC}"
echo ""
sleep 1

python3 backtest_demo.py

echo ""
sleep 2

# 场景 4：风控配置
echo -e "${BLUE}🛡️ 场景 4：风控配置${NC}"
echo ""
sleep 1

echo "风控参数（config.yaml）："
echo "  • 单币种最大仓位: 10%"
echo "  • 总仓位限制: 50%"
echo "  • 止损比例: 5%"
echo "  • 日亏损闸门: 10%"
echo "  • 每日最大交易次数: 20 次"

echo ""
sleep 2

# 场景 5：自动化部署
echo -e "${BLUE}🐳 场景 5：Docker 一键部署${NC}"
echo ""
sleep 1

echo "Docker Compose 配置："
cat docker-compose.yml | head -20

echo ""
echo -e "${GREEN}✅ 支持一键部署：docker-compose up -d${NC}"
echo ""
sleep 2

# 场景 6：项目统计
echo -e "${BLUE}📊 场景 6：项目统计${NC}"
echo ""
sleep 1

echo "项目文件："
ls -1 | grep -E '\.(py|yaml|md|sh)$' | wc -l | xargs echo "  • Python/配置/文档文件:"

echo ""
echo "Git 提交历史："
git log --oneline | head -6

echo ""
sleep 2

# 结束
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 演示完成${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}CryptoEmperor AI - 让交易更智能${NC}"
echo -e "${YELLOW}GitHub: github.com/axe2023/cryptoemperor-ai${NC}"
echo ""
