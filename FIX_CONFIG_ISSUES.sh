#!/bin/bash
# 修复Discord Bot配置问题
set -e

echo "🔧 修复Discord Bot配置问题..."

PROJECT_DIR="/opt/discord-bot"
cd $PROJECT_DIR

echo "📝 检查当前.env配置..."
if [ -f .env ]; then
    echo "✅ 找到.env文件"
    
    # 检查Chart-img API配置
    if ! grep -q "CHART_IMG_API_KEY=" .env; then
        echo "⚙️ 添加Chart-img API配置..."
        echo "" >> .env
        echo "# Chart-img API配置 (用于图表生成)" >> .env
        echo "CHART_IMG_API_KEY=your_chart_img_api_key_here" >> .env
        echo "LAYOUT_ID=2051" >> .env
    fi
    
    # 显示当前配置状态
    echo "📋 当前配置状态:"
    echo "Discord Token: $(grep DISCORD_TOKEN .env | head -1 | cut -d'=' -f2 | cut -c1-20)..."
    echo "Monitor Channels: $(grep MONITOR_CHANNEL_IDS .env | head -1 | cut -d'=' -f2)"
    echo "Chart API Key: $(grep CHART_IMG_API_KEY .env | head -1 | cut -d'=' -f2 | cut -c1-20)..."
    
else
    echo "❌ 未找到.env文件，创建模板..."
    cat > .env << 'EOF'
# Discord配置
DISCORD_TOKEN=your_discord_token_here
MONITOR_CHANNEL_IDS=your_channel_ids_here
REPORT_CHANNEL_ID=your_report_channel_id_here

# API密钥
CHART_IMG_API_KEY=your_chart_api_key_here
LAYOUT_ID=2051
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Chart-img API配置 (用于图表生成)
CHART_IMG_API_KEY=your_chart_img_api_key_here
LAYOUT_ID=2051
WEBHOOK_URL=http://your-server-ip/webhook

# 数据库配置
DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot
EOF
fi

echo "🔄 重启Discord Bot服务..."
docker-compose restart discord-bot

echo "⏳ 等待服务重启..."
sleep 10

echo "📊 检查服务状态..."
docker-compose ps

echo "📝 查看最新日志..."
docker-compose logs --tail=20 discord-bot

echo
echo "✅ 配置修复完成"
echo
echo "📋 下一步:"
echo "1. 编辑 .env 文件中的 CHART_IMG_API_KEY"
echo "2. 如需图表功能，请在 chart-img.com 获取API密钥"
echo "3. 运行: docker-compose restart"
echo
echo "🌐 服务访问地址:"
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "  - 主页: http://$SERVER_IP"
echo "  - 配置: http://$SERVER_IP/config/"
echo "  - 健康: http://$SERVER_IP/health"