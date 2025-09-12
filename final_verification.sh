#!/bin/bash
# 最终验证脚本：确认配置管理器的状态

echo "🔍 最终验证：确认配置管理器的状态..."
echo "=" * 50

echo "📋 1. 检查容器中的文件状态..."
echo "配置管理器文件:"
docker exec discord-bot-main ls -la /app/orderblock_config_manager.py

echo ""
echo "配置文件:"
docker exec discord-bot-main ls -la /app/orderblock_routes.conf

echo ""
echo "webhook文件:"
docker exec discord-bot-main ls -la /app/orderblock_webhook.py

echo ""
echo "📋 2. 检查配置文件内容..."
echo "配置文件内容 (前10行):"
docker exec discord-bot-main head -10 /app/orderblock_routes.conf

echo ""
echo "配置文件内容 (后10行):"
docker exec discord-bot-main tail -10 /app/orderblock_routes.conf

echo ""
echo "📋 3. 直接测试配置管理器..."
echo "直接测试配置管理器:"
docker exec discord-bot-main python -c "
import sys
sys.path.append('/app')
from orderblock_config_manager import SimpleOrderBlockConfig

config = SimpleOrderBlockConfig()
print('默认频道:', config.default_channels)
print('AAPL路由:', config.get_channels_for_ticker('AAPL'))
print('NYSE:AAPL路由:', config.get_channels_for_ticker('NYSE:AAPL'))
print('NASDAQ:TSLA路由:', config.get_channels_for_ticker('NASDAQ:TSLA'))
"

echo ""
echo "📋 4. 检查Discord Bot启动日志..."
echo "Discord Bot启动日志 (最后50行):"
docker logs discord-bot-main --tail 50 | grep -E "(orderblock|config|SimpleOrderBlockConfig)"

echo ""
echo "📋 5. 检查Discord Bot进程..."
echo "Discord Bot进程状态:"
docker ps | grep discord-bot

echo ""
echo "🔍 验证完成！"
