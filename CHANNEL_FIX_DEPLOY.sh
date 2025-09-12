#!/bin/bash
# VPS Docker更新 - 频道权限修复部署脚本

echo "🚀 开始部署频道权限修复到VPS Docker环境..."
echo "==============================================="

# 检查Docker是否运行
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行或无权限访问"
    exit 1
fi

# 停止Discord Bot容器
echo "⏸️ 停止Discord Bot容器..."
docker-compose stop discord-bot

# 等待容器完全停止
sleep 3

# 重新构建Discord Bot镜像
echo "🔧 重新构建Discord Bot镜像..."
docker-compose build discord-bot

# 启动更新后的Discord Bot
echo "🚀 启动更新后的Discord Bot..."
docker-compose up -d discord-bot

# 等待服务启动
echo "⏳ 等待Discord Bot启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
echo "=================="

# 检查Discord Bot容器状态
DISCORD_STATUS=$(docker-compose ps discord-bot | grep -E "Up|running" | wc -l)
if [ $DISCORD_STATUS -gt 0 ]; then
    echo "✅ Discord Bot: 运行中"
else
    echo "❌ Discord Bot: 停止"
fi

# 检查最近的日志
echo ""
echo "📝 最近的Discord Bot日志:"
echo "========================="
docker-compose logs --tail=20 discord-bot

echo ""
echo "🎉 频道权限修复部署完成！"
echo "========================="
echo ""
echo "本次部署包含的所有修复："
echo "✓ 修复了频道判断逻辑bug - CT命令在chart频道正常使用"
echo "✓ chart频道现在正确识别名为'chart'或'request'的频道"
echo "✓ 移除了频道隔离的过度限制"
echo "✓ 修复了Chart-img API配置问题 - 更正了配置项名称"
echo "✓ 修复了Config对象属性错误 - tradingview_session_id配置"
echo "✓ 更新了环境配置模板 - 使用CHART_IMG_API_KEY而非TRADINGVIEW_SESSION"
echo ""
echo "⚠️ 注意: 如果遇到数据库字段错误，请运行:"
echo "sudo bash VPS_DATABASE_FIX.sh"
echo ""
echo "测试命令："
echo "在Discord中使用: @TDbot-tradingview CT TSLA,15m"
echo ""
echo "如需查看实时日志："
echo "docker-compose logs -f discord-bot"