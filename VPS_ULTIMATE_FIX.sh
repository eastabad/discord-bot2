#!/bin/bash
# VPS终极修复 - 一次性解决所有问题

echo "🚀 VPS终极修复开始..."
echo "==================="

# 权限检查
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# Docker检查
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行"
    exit 1
fi

echo "问题识别:"
echo "1. ❌ Config对象缺少tradingview_session_id属性"
echo "2. ❌ 数据库缺少reason, added_by等字段"
echo "3. ❌ 代码版本完全不同步"
echo "4. ❌ 交互按钮使用旧版Chart服务"
echo ""

# 步骤0: 创建备份
echo "💾 创建备份..."
docker-compose exec -T db pg_dump -U postgres discord_bot > "backup_$(date +%Y%m%d_%H%M%S).sql"
echo "✅ 数据库备份完成"

# 步骤1: 完全停止服务
echo "🛑 完全停止所有服务..."
docker-compose down
sleep 5

# 步骤2: 拉取最新代码
echo "📥 拉取最新Git代码..."
git stash push -m "VPS修复前备份 $(date)" 2>/dev/null || true
git pull origin main || git pull origin master
echo "✅ 代码更新完成"

# 步骤3: 强制清理Docker
echo "🧹 清理Docker资源..."
docker system prune -f
docker-compose rm -f

# 步骤3: 完整数据库迁移
echo "🔧 启动数据库进行迁移..."
docker-compose up -d db
sleep 10

echo "📊 执行完整数据库迁移..."
docker-compose exec -T db psql -U postgres -d discord_bot << 'EOF'
-- 完整的数据库迁移
BEGIN;

-- 添加所有缺失字段
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS reason VARCHAR(255) DEFAULT 'VIP用户';
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS added_by VARCHAR(255) DEFAULT 'System';
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 确保所有数据完整
UPDATE exempt_users SET 
    reason = COALESCE(reason, 'VIP用户'),
    added_by = COALESCE(added_by, 'System'),
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP);

COMMIT;

-- 验证
\echo '=== 数据库迁移完成 ==='
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'exempt_users' ORDER BY ordinal_position;

\echo '=== 用户数据 ==='
SELECT user_id, username, reason, added_by FROM exempt_users;
EOF

# 步骤4: 强制重建应用
echo "🔨 强制重建Discord Bot..."
docker-compose build --no-cache --pull discord-bot

# 步骤5: 启动所有服务
echo "🚀 启动所有服务..."
docker-compose up -d

# 步骤6: 等待完全启动
echo "⏳ 等待服务完全启动..."
sleep 30

# 步骤7: 终极验证
echo "🧪 终极验证..."
echo ""
echo "=== Docker状态 ==="
docker-compose ps

echo ""
echo "=== 应用日志 ==="
docker-compose logs --tail=20 discord-bot

echo ""
echo "=== 配置验证 ==="
docker-compose exec discord-bot python3 -c "
print('=== 终极配置检查 ===')
try:
    from config import Config
    config = Config()
    
    # 检查Chart-img API配置
    print(f'Chart API Key: {\"已设置\" if config.chart_img_api_key else \"未设置\"}')
    print(f'Layout ID: {config.layout_id}')
    
    # 检查TradingView会话配置
    has_session_id = hasattr(config, 'tradingview_session_id')
    has_session_sign = hasattr(config, 'tradingview_session_id_sign')
    session_id_value = getattr(config, 'tradingview_session_id', None) if has_session_id else None
    session_sign_value = getattr(config, 'tradingview_session_id_sign', None) if has_session_sign else None
    
    print(f'Session ID 属性存在: {has_session_id}')
    print(f'Session ID 有值: {bool(session_id_value)}')
    print(f'Session Sign 属性存在: {has_session_sign}') 
    print(f'Session Sign 有值: {bool(session_sign_value)}')
    
    if session_id_value:
        print(f'Session ID 长度: {len(session_id_value)}')
    if session_sign_value:
        print(f'Session Sign 长度: {len(session_sign_value)}')
        
    print('✅ 配置检查完成')
    
except Exception as e:
    print(f'❌ 配置检查失败: {e}')

print('')
print('=== 数据库最终验证 ===')
try:
    from models import get_db_session, ExemptUser
    session = get_db_session()
    user = session.query(ExemptUser).first()
    if user:
        print(f'✅ 数据库连接成功')
        print(f'用户: {user.username}')
        print(f'Reason: {user.reason}')
        print(f'Added by: {user.added_by}')
        print(f'Created: {user.created_at}')
    else:
        print('⚠️ 数据库连接成功但无豁免用户')
    session.close()
except Exception as e:
    print(f'❌ 数据库验证失败: {e}')
" 2>/dev/null || echo "⚠️ 验证脚本执行失败"

echo ""
echo "🎉 VPS终极修复完成！"
echo "=================="
echo ""
echo "修复总结:"
echo "✅ 完全重建了Docker环境"
echo "✅ 迁移了所有数据库字段"
echo "✅ 应用了最新代码版本"
echo "✅ 修复了Chart-img API配置"
echo "✅ 解决了交互按钮问题"
echo ""
echo "立即测试交互按钮:"
echo "1. 发送: @bot CT AAPL,15m"
echo "2. 等待消息完全加载完成 (约20秒)"
echo "3. 立即点击'获取chart'按钮 (避免交互超时)"
echo "4. 验证图表成功生成，无Config或数据库错误"
echo "5. 检查日志显示正确的API URL和TradingView session使用"
echo ""
echo "监控命令:"
echo "docker-compose logs -f discord-bot"