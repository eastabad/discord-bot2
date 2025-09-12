#!/bin/bash
# 最终诊断脚本：找出多频道问题的根本原因

echo "🔍 最终诊断：找出多频道问题的根本原因..."
echo "=" * 50

echo "📋 1. 检查配置文件内容..."
echo "配置文件行数:"
wc -l /opt/discord-bot/orderblock_routes.conf

echo ""
echo "配置文件内容 (前10行):"
head -10 /opt/discord-bot/orderblock_routes.conf

echo ""
echo "配置文件内容 (后10行):"
tail -10 /opt/discord-bot/orderblock_routes.conf

echo ""
echo "📋 2. 检查配置管理器文件..."
echo "配置管理器文件大小:"
ls -la /opt/discord-bot/orderblock_config_manager.py

echo ""
echo "配置管理器类名:"
grep "class.*:" /opt/discord-bot/orderblock_config_manager.py

echo ""
echo "📋 3. 检查webhook文件..."
echo "webhook导入语句:"
grep "from.*import.*Config" /opt/discord-bot/orderblock_webhook.py

echo ""
echo "webhook类名使用:"
grep "Config.*(" /opt/discord-bot/orderblock_webhook.py

echo ""
echo "📋 4. 直接测试配置管理器..."
echo "直接测试配置管理器:"
cd /opt/discord-bot && python3 -c "
import sys
sys.path.append('/opt/discord-bot')
from orderblock_config_manager import SimpleOrderBlockConfig

config = SimpleOrderBlockConfig()
print('默认频道:', config.default_channels)
print('AAPL路由:', config.get_channels_for_ticker('AAPL'))
print('NYSE:AAPL路由:', config.get_channels_for_ticker('NYSE:AAPL'))
print('NASDAQ:TSLA路由:', config.get_channels_for_ticker('NASDAQ:TSLA'))
"

echo ""
echo "📋 5. 检查Discord Bot进程..."
echo "Discord Bot进程ID:"
docker exec discord-bot-main ps aux | grep python

echo ""
echo "Discord Bot Python路径:"
docker exec discord-bot-main python -c "import sys; print('\n'.join(sys.path))"

echo ""
echo "📋 6. 检查Discord Bot模块导入..."
echo "Discord Bot中的配置管理器导入:"
docker exec discord-bot-main python -c "
import sys
sys.path.append('/opt/discord-bot')
try:
    from orderblock_config_manager import SimpleOrderBlockConfig
    print('✅ 成功导入SimpleOrderBlockConfig')
    config = SimpleOrderBlockConfig()
    print('默认频道:', config.default_channels)
    print('AAPL路由:', config.get_channels_for_ticker('AAPL'))
except Exception as e:
    print('❌ 导入失败:', e)
"

echo ""
echo "🔍 诊断完成！"
