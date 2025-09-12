#!/bin/bash
# 快速修复VPS部署中的Git冲突问题
set -e

echo "🔧 修复VPS部署Git冲突..."

cd /opt/discord-bot

# 备份重要文件
echo "📦 备份重要配置..."
cp .env .env.backup 2>/dev/null || echo "未找到.env文件"
cp docker-compose.yml docker-compose.yml.backup 2>/dev/null || echo "未找到docker-compose.yml"
cp Dockerfile Dockerfile.backup 2>/dev/null || echo "未找到Dockerfile"

# 强制更新代码
echo "🔄 强制更新项目代码..."
git fetch origin
git reset --hard origin/main

# 恢复配置文件
echo "⚙️ 恢复配置文件..."
if [ -f ".env.backup" ]; then
    mv .env.backup .env
    echo "✅ 恢复.env配置"
fi

# 重新创建Docker配置
echo "🐳 重建Docker配置..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# 安装核心依赖
RUN pip install discord.py aiohttp flask requests psycopg2-binary SQLAlchemy python-dotenv pytz psutil

# 安装AI依赖 (容错处理)
RUN pip install anthropic || echo "⚠️ 跳过anthropic安装"
RUN pip install openai || echo "⚠️ 跳过openai安装" 
RUN pip install google-generativeai || echo "⚠️ 跳过google-generativeai安装"
RUN pip install google-genai || echo "⚠️ 跳过google-genai安装"

COPY . .
RUN mkdir -p /app/config /app/daily_logs /app/logs /app/templates
EXPOSE 5000 8080 8081
CMD ["python", "main_with_api.py"]
EOF

cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16
    container_name: discord-bot-db
    environment:
      POSTGRES_DB: discord_bot
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: discord123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d discord_bot"]
      interval: 10s
      timeout: 5s
      retries: 5

  discord-bot:
    build: .
    container_name: discord-bot-main
    environment:
      - DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot
    env_file:
      - .env
    ports:
      - "5000:5000"
    volumes:
      - ./config:/app/config
      - ./daily_logs:/app/daily_logs
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  config-server:
    build: .
    container_name: discord-bot-config
    env_file:
      - .env
    ports:
      - "8081:8080"
    volumes:
      - ./config:/app/config
      - ./templates:/app/templates
    restart: unless-stopped
    command: python config_web_server.py

volumes:
  postgres_data:
EOF

# 重新构建和启动服务
echo "🚀 重新构建服务..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 30

# 检查状态
echo "📊 检查服务状态..."
docker-compose ps

SERVER_IP=$(hostname -I | awk '{print $1}')

echo
echo "✅ 修复完成！"
echo "🌐 访问地址:"
echo "  - 主页: http://$SERVER_IP"
echo "  - 配置: http://$SERVER_IP/config/"
echo "  - 健康检查: http://$SERVER_IP/health"
echo
echo "🔧 管理命令:"
echo "docker-compose logs -f    # 查看日志"
echo "docker-compose restart    # 重启服务"
echo "docker-compose ps         # 查看状态"