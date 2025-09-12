#!/bin/bash
# 最终修复脚本：解决Docker容器文件同步问题

echo "🔧 最终修复：解决Docker容器文件同步问题..."
echo "=" * 50

echo "📋 问题分析:"
echo "Discord Bot容器中的文件与我们更新的文件不同步"
echo "需要将更新的文件复制到容器中"

echo ""
echo "📋 解决方案:"
echo "1. 将更新的文件复制到容器中"
echo "2. 重启容器以应用更新"

echo ""
echo "🔧 执行修复..."

# 将更新的文件复制到容器中
echo "复制更新的配置管理器到容器..."
docker cp /opt/discord-bot/orderblock_config_manager.py discord-bot-main:/app/orderblock_config_manager.py

echo "复制更新的webhook到容器..."
docker cp /opt/discord-bot/orderblock_webhook.py discord-bot-main:/app/orderblock_webhook.py

echo "复制更新的配置文件到容器..."
docker cp /opt/discord-bot/orderblock_routes.conf discord-bot-main:/app/orderblock_routes.conf

# 验证文件复制
echo ""
echo "📋 验证文件复制..."
echo "容器中的配置管理器文件:"
docker exec discord-bot-main ls -la /app/orderblock_config_manager.py

echo ""
echo "容器中的webhook文件:"
docker exec discord-bot-main ls -la /app/orderblock_webhook.py

echo ""
echo "容器中的配置文件:"
docker exec discord-bot-main ls -la /app/orderblock_routes.conf

# 测试容器中的导入
echo ""
echo "📋 测试容器中的导入..."
docker exec discord-bot-main python -c "
import sys
sys.path.append('/app')
try:
    from orderblock_config_manager import SimpleOrderBlockConfig
    print('✅ 成功导入SimpleOrderBlockConfig')
    config = SimpleOrderBlockConfig()
    print('默认频道:', config.default_channels)
    print('AAPL路由:', config.get_channels_for_ticker('AAPL'))
    print('NYSE:AAPL路由:', config.get_channels_for_ticker('NYSE:AAPL'))
    print('NASDAQ:TSLA路由:', config.get_channels_for_ticker('NASDAQ:TSLA'))
except Exception as e:
    print('❌ 导入失败:', e)
    import traceback
    traceback.print_exc()
"

echo ""
echo "✅ 修复完成！"
echo "现在可以重启Discord Bot服务以应用更新"
