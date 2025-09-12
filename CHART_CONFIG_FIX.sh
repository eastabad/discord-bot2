#!/bin/bash
# Chart配置修复脚本 - 修复Chart API配置问题

echo "🔧 修复Chart API配置问题..."
echo "================================="

# 重启Discord Bot应用修复
echo "🔄 重启Discord Bot..."
docker-compose restart discord-bot

echo ""
echo "⏳ 等待Discord Bot启动..."
sleep 10

echo ""
echo "📝 检查启动日志..."
docker-compose logs --tail=15 discord-bot

echo ""
echo "🧪 测试Chart API配置..."
docker-compose exec discord-bot python3 -c "
from config import Config
config = Config()
print('Chart配置检查:')
print(f'  CHART_IMG_API_KEY: {\"已设置\" if config.chart_img_api_key else \"未设置\"}')
print(f'  LAYOUT_ID: {config.layout_id}')
print(f'  TradingView Session: {\"已设置\" if config.tradingview_session_id else \"未设置\"}')
"

echo ""
echo "✅ Chart配置修复完成！"
echo "======================="
echo ""
echo "配置说明："
echo "✓ 图表功能使用chart-img.com API"
echo "✓ 需要CHART_IMG_API_KEY才能生成图表"
echo "✓ TradingView session配置是可选的"
echo ""
echo "测试建议："
echo "在Discord中点击交互按钮测试图表功能"