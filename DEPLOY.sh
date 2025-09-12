#!/bin/bash
# Discord Bot 简洁部署脚本
set -e

echo "Discord Bot Docker部署开始..."

# 检查root权限
if [[ $EUID -ne 0 ]]; then
   echo "错误: 需要root权限"
   echo "使用: sudo bash DEPLOY.sh"
   exit 1
fi

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "安装Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
fi

if ! command -v docker-compose &> /dev/null; then
    echo "安装Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 安装Nginx
apt-get update && apt-get install -y nginx

# 创建项目目录
PROJECT_DIR="/opt/discord-bot"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 下载项目文件
echo "下载项目文件..."
if [ -d ".git" ]; then
    git pull
else
    rm -rf * .git* 2>/dev/null || true
    git clone https://github.com/eastabad/DiscordBot.git .
fi

# 创建简化的Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

# 安装依赖
RUN pip install discord.py aiohttp flask requests psycopg2-binary SQLAlchemy python-dotenv pytz psutil
RUN pip install anthropic openai google-generativeai google-genai || true

COPY . .
RUN mkdir -p /app/config /app/daily_logs /app/logs /app/templates
EXPOSE 5000 8080 8081
CMD ["python", "main_with_api.py"]
EOF

# 创建docker-compose.yml
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

# 创建.env示例
if [ ! -f .env ]; then
    cat > .env << 'EOF'
DISCORD_TOKEN=your_discord_token_here
MONITOR_CHANNEL_IDS=your_channel_ids_here
REPORT_CHANNEL_ID=your_report_channel_id_here
CHART_IMG_API_KEY=your_chart_api_key_here
LAYOUT_ID=your_layout_id_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
WEBHOOK_URL=http://example.com/webhook
TRADINGVIEW_SESSION=your_session_here
EOF
    echo "已创建.env文件，请编辑添加您的API密钥"
fi

# 配置Nginx
echo "配置Nginx..."
cat > /etc/nginx/sites-available/discord-bot << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /webhook/ {
        proxy_pass http://127.0.0.1:5000/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /config/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/api/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/discord-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 启动服务
echo "启动Docker服务..."
docker-compose down 2>/dev/null || true
docker-compose build
docker-compose up -d

echo "等待服务启动..."
sleep 30

# 检查状态
docker-compose ps

DOMAIN_NAME=$(hostname -I | awk '{print $1}')

echo
echo "部署完成!"
echo "服务地址: http://$DOMAIN_NAME"
echo "配置页面: http://$DOMAIN_NAME/config/"
echo "健康检查: http://$DOMAIN_NAME/health"
echo
echo "管理命令:"
echo "cd $PROJECT_DIR"
echo "docker-compose logs -f    # 查看日志"
echo "docker-compose restart    # 重启服务"
echo "docker-compose ps         # 查看状态"
echo
echo "请编辑 $PROJECT_DIR/.env 文件添加您的API密钥，然后运行:"
echo "docker-compose restart"