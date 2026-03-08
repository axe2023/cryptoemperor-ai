# Docker 部署指南

## 快速开始

### 1. 准备环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 2. 构建镜像
```bash
docker-compose build
```

### 3. 启动服务（调度器模式）
```bash
docker-compose up -d
```

服务将在后台运行，按配置的时间自动执行扫描和日报生成。

### 4. 查看日志
```bash
docker-compose logs -f
```

### 5. 停止服务
```bash
docker-compose down
```

## 一次性运行

如果只想运行一次（不使用调度器）：

```bash
docker-compose --profile once run --rm cryptoemperor-once
```

## 数据持久化

以下目录会挂载到宿主机，数据不会丢失：
- `./data` - 信号历史记录
- `./logs` - 日志文件
- `./reports` - 日报文件
- `./config.yaml` - 配置文件

## 自定义配置

编辑 `config.yaml` 后，重启容器生效：

```bash
docker-compose restart
```

## 环境变量

必填：
- `BINANCE_API_KEY` - Binance API Key
- `BINANCE_SECRET_KEY` - Binance Secret Key

可选：
- `BINANCE_BASE_URL` - API 地址（默认：https://api.binance.com）
- `TELEGRAM_BOT_TOKEN` - Telegram Bot Token
- `TELEGRAM_CHAT_ID` - Telegram Chat ID

## 调度时间配置

编辑 `scheduler.py` 中的 `config` 字典：

```python
config = {
    'scan_times': ['09:00', '12:00', '15:00', '18:00', '21:00'],  # 扫描时间
    'report_time': '22:00'  # 日报时间
}
```

## 故障排查

### 查看容器状态
```bash
docker-compose ps
```

### 查看实时日志
```bash
docker-compose logs -f cryptoemperor
```

### 进入容器调试
```bash
docker-compose exec cryptoemperor bash
```

### 重新构建（代码更新后）
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
