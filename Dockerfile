# Discord Bot Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY docker-requirements.txt requirements.txt

# 安装Python依赖 - 分步骤避免版本冲突
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 安装基础依赖
RUN pip install --no-cache-dir discord.py aiohttp flask requests psycopg2-binary SQLAlchemy python-dotenv pytz psutil

# 安装AI依赖 - 容错处理
RUN pip install --no-cache-dir anthropic || echo "Anthropic安装失败"
RUN pip install --no-cache-dir openai || echo "OpenAI安装失败"
RUN pip install --no-cache-dir google-generativeai || echo "Google GenerativeAI安装失败"
RUN pip install --no-cache-dir google-genai || echo "Google GenAI安装失败"

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p /app/config /app/daily_logs /app/logs /app/templates

# 设置权限
RUN chmod +x *.py

# 暴露端口
EXPOSE 5000 8080

# 默认命令
CMD ["python", "main_with_api.py"]