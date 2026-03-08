#!/bin/bash
# CryptoEmperor AI 自动化运行脚本

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}CryptoEmperor AI - 自动化运行${NC}"
echo -e "${GREEN}时间: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查环境变量
if [ -z "$BINANCE_API_KEY" ] || [ -z "$BINANCE_SECRET_KEY" ]; then
    echo -e "${RED}❌ 错误: 未配置 Binance API 环境变量${NC}"
    exit 1
fi

# 运行主程序
echo -e "${YELLOW}📊 运行信号扫描...${NC}"
python3 main.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 信号扫描完成${NC}"
else
    echo -e "${RED}❌ 信号扫描失败${NC}"
    exit 1
fi

# 检查日报文件
REPORT_FILE="reports/report_$(date '+%Y-%m-%d').md"
if [ -f "$REPORT_FILE" ]; then
    echo -e "${GREEN}✅ 日报已生成: $REPORT_FILE${NC}"
    
    # 显示日报摘要
    echo -e "${YELLOW}📋 日报摘要:${NC}"
    head -n 20 "$REPORT_FILE"
    echo ""
else
    echo -e "${RED}⚠️ 日报文件未找到${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 运行完成${NC}"
echo -e "${GREEN}========================================${NC}"
