#!/bin/bash
# VPS Dockerfile修复 - 解决vps_requirements.txt缺失问题

echo "🔧 修复VPS Dockerfile错误"
echo "========================="
echo "❌ 错误: COPY vps_requirements.txt requirements.txt - 文件不存在"
echo "✅ 修复: 使用docker-requirements.txt"
echo ""

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 切换到项目目录
cd /opt/discord-bot || { echo "❌ 项目目录不存在"; exit 1; }

echo "📥 拉取最新代码..."
git fetch --all
git reset --hard origin/main 2>/dev/null || git reset --hard origin/master
git pull

echo "🔍 验证requirements文件..."
if [ -f "docker-requirements.txt" ]; then
    echo "✅ docker-requirements.txt 存在"
    cat docker-requirements.txt
else
    echo "❌ docker-requirements.txt 不存在"
    echo "📋 创建基础requirements文件..."
    cat > docker-requirements.txt << 'EOF'
discord.py>=2.3.0
aiohttp>=3.8.0
flask>=2.3.0
requests>=2.31.0
psycopg2-binary>=2.9.0
SQLAlchemy>=2.0.0
python-dotenv>=1.0.0
pytz>=2023.3
psutil>=5.9.0
EOF
fi

echo "🛑 停止服务..."
docker-compose down --remove-orphans

echo "🧹 清理Docker缓存..."
docker system prune -af

echo "🔨 重建容器..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 15

echo "🧪 检查服务状态..."
docker-compose ps

echo "📋 检查日志..."
docker-compose logs --tail=10 discord-bot
docker-compose logs --tail=10 config-server

echo ""
echo "🎉 VPS Dockerfile修复完成！"
echo "=========================="
echo ""
echo "如果仍有问题，手动检查:"
echo "1. docker-compose logs discord-bot"
echo "2. docker-compose logs config-server"
echo "3. docker-compose ps"