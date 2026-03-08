FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p data logs reports

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 默认命令
CMD ["python3", "main.py"]
