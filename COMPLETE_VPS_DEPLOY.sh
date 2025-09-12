#!/bin/bash
# Discord Bot 完整VPS部署脚本 - 包含域名和HTTPS配置
set -e

echo "================================================================="
echo "🚀 Discord Bot 完整VPS部署 (含域名&HTTPS)"
echo "================================================================="

# 检查root权限
if [[ $EUID -ne 0 ]]; then
   echo "❌ 错误: 需要root权限"
   echo "使用: sudo bash COMPLETE_VPS_DEPLOY.sh [your-domain.com]"
   exit 1
fi

# 获取域名参数
DOMAIN_NAME=""
if [ "$1" != "" ]; then
    DOMAIN_NAME="$1"
    echo "🌐 配置域名: $DOMAIN_NAME"
else
    echo "⚠️  未提供域名，将使用IP地址访问"
    echo "如需域名和HTTPS，请运行: sudo bash $0 your-domain.com"
fi

# 更新系统
echo "📦 更新系统包..."
apt-get update && apt-get upgrade -y

# 安装必要软件
echo "📦 安装系统依赖..."
apt-get install -y curl wget git nginx certbot python3-certbot-nginx ufw

# 配置防火墙
echo "🔒 配置防火墙..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp
ufw allow 8081/tcp

# 安装Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 安装Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    usermod -aG docker $USER 2>/dev/null || true
fi

# 安装Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 安装Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 创建项目目录
PROJECT_DIR="/opt/discord-bot"
echo "📁 准备项目目录: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 下载项目文件
echo "📥 下载项目文件..."
if [ -d ".git" ]; then
    echo "更新现有项目..."
    # 备份本地部署脚本
    if [ -f "COMPLETE_VPS_DEPLOY.sh" ]; then
        cp COMPLETE_VPS_DEPLOY.sh COMPLETE_VPS_DEPLOY.sh.backup
    fi
    
    # 强制更新，忽略本地修改
    git fetch origin
    git reset --hard origin/main
    
    # 恢复部署脚本
    if [ -f "COMPLETE_VPS_DEPLOY.sh.backup" ]; then
        mv COMPLETE_VPS_DEPLOY.sh.backup COMPLETE_VPS_DEPLOY.sh
    fi
else
    echo "克隆新项目..."
    rm -rf * .git* 2>/dev/null || true
    git clone https://github.com/eastabad/DiscordBot.git .
fi

# 创建优化的Dockerfile
echo "🐳 配置Docker环境..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip

# 安装核心依赖
RUN pip install discord.py aiohttp flask requests psycopg2-binary SQLAlchemy python-dotenv pytz psutil

# 安装AI依赖 (容错处理)
RUN pip install anthropic || echo "⚠️ 跳过anthropic安装"
RUN pip install openai || echo "⚠️ 跳过openai安装" 
RUN pip install google-generativeai || echo "⚠️ 跳过google-generativeai安装"
RUN pip install google-genai || echo "⚠️ 跳过google-genai安装"

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p /app/config /app/daily_logs /app/logs /app/templates

# 暴露端口
EXPOSE 5000 8080 8081

# 启动命令
CMD ["python", "main_with_api.py"]
EOF

# 创建docker-compose.yml
echo "🐳 配置Docker Compose..."
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

# 创建或更新.env文件
echo "⚙️ 配置环境变量..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Discord配置
DISCORD_TOKEN=your_discord_token_here
MONITOR_CHANNEL_IDS=your_channel_ids_here
REPORT_CHANNEL_ID=your_report_channel_id_here

# API密钥
CHART_IMG_API_KEY=your_chart_api_key_here
LAYOUT_ID=your_layout_id_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Webhook配置
WEBHOOK_URL=https://your-domain.com/webhook
TRADINGVIEW_SESSION=your_session_here

# 数据库配置
DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot
EOF
    echo "✅ 已创建.env配置文件"
else
    echo "✅ 使用现有.env配置文件"
fi

# 配置Nginx
echo "🌐 配置Nginx反向代理..."

# 确保webroot目录存在
mkdir -p /var/www/html

# 根据是否有域名配置不同的Nginx
if [ "$DOMAIN_NAME" != "" ]; then
    # 有域名的配置 - 先配置HTTP，稍后申请SSL
    cat > /etc/nginx/sites-available/discord-bot << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    # Let's Encrypt验证
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # API路由
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Webhook路由
    location /webhook/ {
        proxy_pass http://127.0.0.1:5000/webhook/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 配置管理
    location /config/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:5000/api/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 默认路由到配置页面
    location / {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
else
    # 仅IP访问的配置
    cat > /etc/nginx/sites-available/discord-bot << 'EOF'
server {
    listen 80;
    server_name _;
    
    # API路由
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Webhook路由
    location /webhook/ {
        proxy_pass http://127.0.0.1:5000/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 配置管理
    location /config/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:5000/api/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 默认路由到配置页面
    location / {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
fi

# 启用Nginx配置
ln -sf /etc/nginx/sites-available/discord-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
echo "🔧 测试Nginx配置..."
nginx -t

# 重启Nginx
systemctl restart nginx
systemctl enable nginx

# 启动Docker服务
echo "🐳 构建并启动Docker服务..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 如果有域名，配置SSL证书
if [ "$DOMAIN_NAME" != "" ]; then
    echo "🔒 配置SSL证书..."
    echo "请确保域名 $DOMAIN_NAME 已指向此服务器IP"
    read -p "域名已正确解析？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 申请SSL证书
        certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME || echo "⚠️ SSL证书申请失败，稍后可手动配置"
        
        # 设置自动续期
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
        echo "✅ SSL证书自动续期已设置"
    else
        echo "⚠️ 请先配置域名解析，然后手动运行:"
        echo "certbot --nginx -d $DOMAIN_NAME"
    fi
fi

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 获取访问地址
SERVER_IP=$(hostname -I | awk '{print $1}')

echo
echo "================================================================="
echo "🎉 部署完成！"
echo "================================================================="

if [ "$DOMAIN_NAME" != "" ]; then
    echo "🌐 域名访问:"
    echo "  - 主页: https://$DOMAIN_NAME"
    echo "  - 配置: https://$DOMAIN_NAME/config/"
    echo "  - API健康: https://$DOMAIN_NAME/health"
    echo "  - TradingView Webhook: https://$DOMAIN_NAME/webhook/tradingview"
    echo
    echo "🔒 HTTP访问 (自动重定向到HTTPS):"
    echo "  - http://$DOMAIN_NAME"
fi

echo "🌐 IP访问:"
echo "  - 主页: http://$SERVER_IP"
echo "  - 配置: http://$SERVER_IP/config/"
echo "  - API健康: http://$SERVER_IP/health"
echo "  - TradingView Webhook: http://$SERVER_IP/webhook/tradingview"

echo
echo "📁 项目目录: $PROJECT_DIR"
echo "⚙️ 配置文件: $PROJECT_DIR/.env"
echo
echo "🔧 管理命令:"
echo "cd $PROJECT_DIR"
echo "docker-compose logs -f         # 查看日志"
echo "docker-compose restart         # 重启服务"
echo "docker-compose ps              # 查看状态"
echo "docker-compose down            # 停止服务"
echo "docker-compose up -d           # 启动服务"
echo
echo "⚠️ 请编辑 $PROJECT_DIR/.env 文件配置API密钥"
echo "然后运行: docker-compose restart"
echo "================================================================="