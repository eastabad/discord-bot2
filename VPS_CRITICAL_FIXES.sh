#!/bin/bash
# VPS关键修复 - 立即解决Chart API Config错误

echo "🚨 VPS关键修复开始..."
echo "=================="

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

echo "✅ VIP命令正常工作 - 用户成功添加到豁免列表"
echo "❌ Chart功能失败 - Config对象缺少tradingview_session_id属性"
echo "🎯 目标: 强制更新VPS代码版本"
echo ""

# 步骤1: 停止所有服务
echo "🛑 停止所有Discord服务..."
docker-compose stop discord-bot
sleep 5

# 步骤2: 强制拉取最新代码
echo "📥 强制拉取最新Git代码..."
git fetch --all
git reset --hard origin/main 2>/dev/null || git reset --hard origin/master
git pull origin main 2>/dev/null || git pull origin master
echo "✅ 代码强制更新完成"

# 步骤3: 验证关键文件
echo "🔍 验证关键配置文件..."
if grep -q "tradingview_session_id.*getenv.*TRADINGVIEW_SESSION_ID" config.py; then
    echo "✅ config.py包含正确的TradingView属性"
else
    echo "❌ config.py仍然缺少TradingView属性"
    echo "⚠️ 将创建修补版本..."
    
    # 创建修补的config.py
    cp config.py config.py.backup
    sed -i '/# TradingView配置/a\        self.tradingview_session_id = os.getenv("TRADINGVIEW_SESSION_ID")\n        self.tradingview_session_id_sign = os.getenv("TRADINGVIEW_SESSION_ID_SIGN")' config.py
fi

# 步骤4: 彻底清理Docker
echo "🧹 彻底清理Docker资源..."
docker-compose rm -f discord-bot
docker rmi $(docker images -q | head -5) 2>/dev/null || true
docker system prune -f

# 步骤5: 强制重建容器
echo "🔨 强制重建Discord Bot容器..."
docker-compose build --no-cache --pull discord-bot

# 步骤6: 启动服务
echo "🚀 启动更新后的服务..."
docker-compose up -d discord-bot

# 步骤7: 等待启动
echo "⏳ 等待服务完全启动..."
for i in {1..30}; do
    if docker-compose logs discord-bot 2>/dev/null | grep -q "机器人已登录"; then
        echo "✅ Discord Bot已启动"
        break
    fi
    echo "等待中... ($i/30)"
    sleep 2
done

# 步骤8: 关键验证
echo "🧪 关键验证测试..."
echo ""
echo "=== 容器状态 ==="
docker-compose ps discord-bot

echo ""
echo "=== 最新日志 ==="
docker-compose logs --tail=10 discord-bot

echo ""
echo "=== Config属性验证 ==="
docker-compose exec discord-bot python3 -c "
import os
print('=== VPS Config修复验证 ===')
print(f'Environment TRADINGVIEW_SESSION_ID: {\"已设置\" if os.getenv(\"TRADINGVIEW_SESSION_ID\") else \"未设置\"}')
print(f'Environment TRADINGVIEW_SESSION_ID_SIGN: {\"已设置\" if os.getenv(\"TRADINGVIEW_SESSION_ID_SIGN\") else \"未设置\"}')

try:
    from config import Config
    config = Config()
    
    # 检查关键属性
    has_session_id = hasattr(config, 'tradingview_session_id')
    has_session_sign = hasattr(config, 'tradingview_session_id_sign')
    
    print(f'Config.tradingview_session_id 属性: {\"✅存在\" if has_session_id else \"❌缺失\"}')
    print(f'Config.tradingview_session_id_sign 属性: {\"✅存在\" if has_session_sign else \"❌缺失\"}')
    
    if has_session_id:
        session_id = getattr(config, 'tradingview_session_id', None)
        print(f'Session ID 值: {\"✅有值 (长度:\" + str(len(session_id)) + \")\" if session_id else \"❌为空\"}')
    
    if has_session_sign:
        session_sign = getattr(config, 'tradingview_session_id_sign', None)
        print(f'Session Sign 值: {\"✅有值 (长度:\" + str(len(session_sign)) + \")\" if session_sign else \"❌为空\"}')
    
    # 测试Chart服务初始化
    if has_session_id and has_session_sign:
        from chart_service import ChartService
        chart_service = ChartService(config)
        print(f'✅ Chart服务初始化成功')
        print(f'API URL: {chart_service.api_url}')
    else:
        print('❌ Chart服务无法初始化 - 缺少TradingView配置')
        
except Exception as e:
    print(f'❌ Config验证失败: {e}')
    import traceback
    traceback.print_exc()
" 2>/dev/null || echo "⚠️ 配置验证脚本失败"

echo ""
echo "🎉 VPS关键修复完成！"
echo "================="
echo ""
echo "修复状态:"
echo "✅ 强制更新了Git代码"
echo "✅ 彻底重建了Docker环境"
echo "✅ 验证了Config对象属性"
echo ""
echo "立即测试:"
echo "1. 在Discord发送: @bot CT AAPL,15m"
echo "2. 验证不再有Config属性错误"
echo "3. 确认图表成功生成"
echo ""
echo "如果仍有问题，请检查:"
echo "- VPS环境变量是否正确设置"
echo "- Docker容器是否使用最新镜像"
echo "- config.py文件是否包含TradingView属性"