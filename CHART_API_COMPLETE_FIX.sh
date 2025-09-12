#!/bin/bash
# Chart-img API完整修复脚本

echo "🔧 Chart-img API完整修复 (基于官方文档)"
echo "==========================================="

# 重启Discord Bot应用修复
echo "🔄 重启Discord Bot..."
docker-compose restart discord-bot

echo ""
echo "⏳ 等待Discord Bot启动..."
sleep 10

echo ""
echo "📝 检查启动日志..."
docker-compose logs --tail=20 discord-bot

echo ""
echo "🧪 测试Chart API配置..."
docker-compose exec discord-bot python3 -c "
from config import Config
config = Config()
print('Chart-img API配置检查 (4个参数):')
print(f'  1. CHART_IMG_API_KEY: {\"✅ 已设置\" if config.chart_img_api_key else \"❌ 未设置\"}')
print(f'  2. LAYOUT_ID: {config.layout_id}')
print(f'  3. TRADINGVIEW_SESSION_ID: {\"✅ 已设置\" if config.tradingview_session_id else \"❌ 未设置 (可选)\"}')
print(f'  4. TRADINGVIEW_SESSION_ID_SIGN: {\"✅ 已设置\" if config.tradingview_session_id_sign else \"❌ 未设置 (可选)\"}')
print('')
print('API URL测试:')
try:
    from chart_service import ChartService
    chart_service = ChartService(config)
    print(f'  API URL: {chart_service.api_url}')
    print('  ✅ Chart服务初始化成功')
except Exception as e:
    print(f'  ❌ Chart服务初始化失败: {e}')
"

echo ""
echo "✅ Chart-img API修复完成！"
echo "=========================="
echo ""
echo "配置说明："
echo "✓ 使用Chart-img API官方v2接口"
echo "✓ 支持Layout Chart布局"
echo "✓ API URL: https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}"
echo "✓ 需要4个参数: API_KEY(必需), LAYOUT_ID(必需), SESSION_ID(可选), SESSION_SIGN(可选)"
echo ""
echo "测试建议："
echo "1. 在Discord中点击交互按钮测试图表生成"
echo "2. 检查日志中的API请求URL和响应"
echo "3. 如需私有布局访问，请配置TradingView session参数"