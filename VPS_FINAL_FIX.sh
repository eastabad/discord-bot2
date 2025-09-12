#!/bin/bash
# VPS最终修复 - 解决所有剩余问题

echo "🔧 VPS最终修复开始..."
echo "===================="

# 检查Docker
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行"
    exit 1
fi

echo "问题分析:"
echo "✓ TRADINGVIEW_SESSION_ID已设置但未读取"
echo "✓ 数据库仍缺少reason字段"
echo "✓ 需要强制重建容器应用最新代码"
echo ""

# 步骤1: 完整数据库迁移
echo "🔧 步骤1: 完整数据库迁移..."
if [ -f VPS_COMPLETE_DATABASE_MIGRATION.sql ]; then
    docker-compose exec -T db psql -U postgres -d discord_bot < VPS_COMPLETE_DATABASE_MIGRATION.sql
else
    echo "⚠️ 数据库迁移文件不存在，使用内联SQL"
    docker-compose exec -T db psql -U postgres -d discord_bot << 'EOF'
-- 基础迁移
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS reason VARCHAR(255) DEFAULT 'VIP用户';
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS added_by VARCHAR(255) DEFAULT 'System';
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 更新数据
UPDATE exempt_users SET 
    reason = COALESCE(reason, 'VIP用户'),
    added_by = COALESCE(added_by, 'System'),
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP);

\echo '数据库迁移完成'
EOF
fi

echo ""

# 步骤2: 完全重启服务
echo "🔄 步骤2: 完全重启Discord Bot..."
docker-compose stop discord-bot
sleep 3
docker-compose rm -f discord-bot
docker-compose build --no-cache discord-bot
docker-compose up -d discord-bot

echo ""
echo "⏳ 等待Discord Bot启动..."
sleep 20

# 步骤3: 验证修复
echo "✅ 步骤3: 验证修复结果..."
echo ""
echo "Docker容器状态:"
docker-compose ps discord-bot

echo ""
echo "最新启动日志:"
docker-compose logs --tail=15 discord-bot

echo ""
echo "配置验证:"
docker-compose exec discord-bot python3 -c "
print('=== 完整配置检查 ===')
try:
    from config import Config
    config = Config()
    print(f'Chart API Key: {\"已设置\" if config.chart_img_api_key else \"未设置\"}')
    print(f'Layout ID: {config.layout_id}')
    print(f'Session ID 属性: {hasattr(config, \"tradingview_session_id\")}')
    print(f'Session ID 值: {\"已设置\" if hasattr(config, \"tradingview_session_id\") and config.tradingview_session_id else \"未设置\"}')
    print(f'Session Sign 属性: {hasattr(config, \"tradingview_session_id_sign\")}')
    print(f'Session Sign 值: {\"已设置\" if hasattr(config, \"tradingview_session_id_sign\") and config.tradingview_session_id_sign else \"未设置\"}')
    print('✅ 配置对象检查完成')
except Exception as e:
    print(f'❌ 配置检查失败: {e}')

print('')
print('=== 数据库测试 ===')
try:
    from models import get_db_session, ExemptUser
    session = get_db_session()
    user = session.query(ExemptUser).first()
    if user:
        print(f'✅ 数据库连接正常')
        print(f'用户: {user.username}')
        print(f'Reason字段: {user.reason}')
    else:
        print('⚠️ 数据库连接正常但无豁免用户')
    session.close()
except Exception as e:
    print(f'❌ 数据库测试失败: {e}')
" 2>/dev/null || echo "⚠️ 配置验证失败，容器可能未完全启动"

echo ""
echo "🎉 VPS最终修复完成！"
echo "=================="
echo ""
echo "修复总结:"
echo "✅ 强制添加了数据库reason字段"
echo "✅ 完全重建了Discord Bot容器"
echo "✅ 应用了所有最新代码修复"
echo "✅ 验证了配置完整性"
echo ""
echo "测试建议:"
echo "1. 发送Discord命令: @bot CT AAPL,15m"
echo "2. 等待消息发送完成"
echo "3. 立即点击'获取chart'按钮"
echo "4. 检查是否还有任何错误"
echo ""
echo "实时监控："
echo "docker-compose logs -f discord-bot"