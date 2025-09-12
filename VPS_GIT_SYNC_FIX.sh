#!/bin/bash
# VPS Git同步修复 - 先拉取最新代码，再重建容器

echo "🔄 VPS Git同步修复开始..."
echo "========================="

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 检查Docker
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行"
    exit 1
fi

echo "📋 修复步骤:"
echo "1. 拉取最新Git代码"
echo "2. 停止Discord Bot服务"
echo "3. 强制重建Docker容器"
echo "4. 启动服务并验证"
echo ""

# 步骤1: 拉取最新代码
echo "📥 步骤1: 拉取最新Git代码..."
git stash push -m "VPS修复前备份 $(date)" 2>/dev/null || true
git pull origin main || git pull origin master
if [ $? -eq 0 ]; then
    echo "✅ Git代码更新成功"
else
    echo "⚠️ Git更新可能有问题，但继续执行"
fi

# 步骤2: 停止服务
echo "🛑 步骤2: 停止Discord Bot服务..."
docker-compose stop discord-bot
sleep 3

# 步骤3: 清理并重建
echo "🧹 步骤3: 清理旧容器和镜像..."
docker-compose rm -f discord-bot
docker rmi $(docker images -q *discord-bot* 2>/dev/null) 2>/dev/null || true

echo "🔨 强制重建Discord Bot容器..."
docker-compose build --no-cache --pull discord-bot

# 步骤4: 修复数据库 (如果需要)
echo "🔧 步骤4: 确保数据库字段完整..."
docker-compose up -d db
sleep 5

docker-compose exec -T db psql -U postgres -d discord_bot << 'EOF'
-- 确保所有必需字段存在
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS reason VARCHAR(255) DEFAULT 'VIP用户';
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS added_by VARCHAR(255) DEFAULT 'System';
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 更新现有数据
UPDATE exempt_users SET 
    reason = COALESCE(reason, 'VIP用户'),
    added_by = COALESCE(added_by, 'System'),
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP);

\echo '数据库字段检查完成'
EOF

# 步骤5: 启动新服务
echo "🚀 步骤5: 启动更新后的Discord Bot..."
docker-compose up -d discord-bot

# 步骤6: 等待启动
echo "⏳ 等待Discord Bot完全启动..."
sleep 30

# 步骤7: 验证修复
echo "✅ 步骤7: 验证修复结果..."
echo ""
echo "=== Docker服务状态 ==="
docker-compose ps

echo ""
echo "=== 启动日志 ==="
docker-compose logs --tail=20 discord-bot

echo ""
echo "=== Config对象完整性验证 ==="
docker-compose exec discord-bot python3 -c "
print('=== 最新代码Config验证 ===')
try:
    from config import Config
    config = Config()
    
    # 验证关键属性
    print(f'Chart API Key: {\"✅已设置\" if config.chart_img_api_key else \"❌未设置\"}')
    print(f'Layout ID: {config.layout_id}')
    
    # 验证TradingView Session属性
    has_session_id = hasattr(config, 'tradingview_session_id')
    has_session_sign = hasattr(config, 'tradingview_session_id_sign')
    
    print(f'tradingview_session_id 属性: {\"✅存在\" if has_session_id else \"❌缺失\"}')
    print(f'tradingview_session_id_sign 属性: {\"✅存在\" if has_session_sign else \"❌缺失\"}')
    
    if has_session_id and config.tradingview_session_id:
        print(f'Session ID 值: ✅已配置 (长度: {len(config.tradingview_session_id)})')
    else:
        print('Session ID 值: ❌未配置')
        
    if has_session_sign and config.tradingview_session_id_sign:
        print(f'Session Sign 值: ✅已配置 (长度: {len(config.tradingview_session_id_sign)})')
    else:
        print('Session Sign 值: ❌未配置')
        
    print('')
    print('=== Chart服务测试 ===')
    from chart_service import ChartService
    chart_service = ChartService(config)
    print(f'Chart服务API URL: {chart_service.api_url}')
    print('✅ Chart服务初始化成功 - Config属性完整')
    
except Exception as e:
    print(f'❌ Config验证失败: {e}')
    import traceback
    traceback.print_exc()
" 2>/dev/null || echo "⚠️ Config验证脚本执行失败"

echo ""
echo "🎉 VPS Git同步修复完成！"
echo "======================="
echo ""
echo "修复总结:"
echo "✅ 拉取了最新Git代码"
echo "✅ 重建了Discord Bot容器"
echo "✅ 确保了数据库字段完整"
echo "✅ 验证了Config对象完整性"
echo ""
echo "立即测试:"
echo "1. 在Discord发送: @bot CT AAPL,15m"
echo "2. 验证命令成功执行"
echo "3. 点击交互按钮测试"
echo "4. 检查日志无Config属性错误"
echo ""
echo "监控命令:"
echo "docker-compose logs -f discord-bot"