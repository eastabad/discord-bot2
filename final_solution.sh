#!/bin/bash
# 最终解决方案：完全替换旧的配置管理器

echo "🔧 最终解决方案：完全替换旧的配置管理器..."

# 备份原文件
echo "备份原文件..."
cp /opt/discord-bot/orderblock_config_manager.py /opt/discord-bot/orderblock_config_manager.py.backup.$(date +%Y%m%d_%H%M%S)

# 完全替换旧的配置管理器文件
echo "完全替换旧的配置管理器文件..."
cp /opt/discord-bot/simple_orderblock_config.py /opt/discord-bot/orderblock_config_manager.py

# 更新导入语句，使用新的类名
echo "更新导入语句..."
sed -i 's/from simple_orderblock_config import SimpleOrderBlockConfig/from orderblock_config_manager import OrderBlockConfigManager/' /opt/discord-bot/orderblock_webhook.py

# 更新类名
echo "更新类名..."
sed -i 's/SimpleOrderBlockConfig/OrderBlockConfigManager/g' /opt/discord-bot/orderblock_webhook.py

# 验证更新结果
echo "验证更新结果..."
echo "导入语句:"
grep 'from.*import.*Config' /opt/discord-bot/orderblock_webhook.py

echo ""
echo "类名使用:"
grep 'OrderBlockConfigManager' /opt/discord-bot/orderblock_webhook.py

echo ""
echo "配置文件路径:"
grep 'config_file.*=' /opt/discord-bot/orderblock_config_manager.py

echo "✅ 最终解决方案完成！"
echo "请重启Discord Bot服务以应用更新"
