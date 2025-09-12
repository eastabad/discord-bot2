#!/bin/bash
# 更新OrderBlock Webhook使用新的配置管理器

echo "🔧 更新OrderBlock Webhook使用新的配置管理器..."

# 备份原文件
echo "备份原文件..."
cp /opt/discord-bot/orderblock_webhook.py /opt/discord-bot/orderblock_webhook.py.backup.$(date +%Y%m%d_%H%M%S)

# 更新导入语句
echo "更新导入语句..."
sed -i 's/from orderblock_config_manager import OrderBlockConfigManager/from simple_orderblock_config import SimpleOrderBlockConfig/' /opt/discord-bot/orderblock_webhook.py

# 更新类名
echo "更新类名..."
sed -i 's/OrderBlockConfigManager/SimpleOrderBlockConfig/g' /opt/discord-bot/orderblock_webhook.py

# 验证更新结果
echo "验证更新结果..."
echo "导入语句:"
grep 'from.*import.*Config' /opt/discord-bot/orderblock_webhook.py

echo ""
echo "类名使用:"
grep 'SimpleOrderBlockConfig' /opt/discord-bot/orderblock_webhook.py

echo "✅ Webhook更新完成！"
echo "请重启Discord Bot服务以应用更新"
