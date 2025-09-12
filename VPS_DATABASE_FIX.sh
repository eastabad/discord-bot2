#!/bin/bash
# VPS数据库模式修复脚本

echo "🔧 开始修复VPS数据库模式..."
echo "================================="

# 检查Docker是否运行
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行或无权限访问"
    exit 1
fi

# 检查数据库容器是否运行
DB_RUNNING=$(docker-compose ps db | grep -E "Up|running" | wc -l)
if [ $DB_RUNNING -eq 0 ]; then
    echo "❌ 数据库容器未运行"
    exit 1
fi

echo "✅ 数据库容器运行正常"

# 执行数据库修复SQL
echo "📝 执行数据库模式修复..."
docker-compose exec -T db psql -U postgres -d discord_bot << 'EOF'
-- 检查当前表结构
\echo '📋 当前exempt_users表结构:'
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'exempt_users' 
ORDER BY ordinal_position;

-- 添加缺失的reason字段
\echo '🔧 添加缺失的reason字段...'
DO $$ 
BEGIN 
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'exempt_users' AND column_name = 'reason'
    ) THEN
        ALTER TABLE exempt_users ADD COLUMN reason VARCHAR(255) DEFAULT 'VIP用户';
        UPDATE exempt_users SET reason = 'VIP用户' WHERE reason IS NULL;
        \echo '✅ reason字段添加成功';
    ELSE
        \echo '⚠️ reason字段已存在';
    END IF;
END $$;

-- 验证修复结果
\echo '📋 修复后的exempt_users表结构:'
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'exempt_users' 
ORDER BY ordinal_position;

-- 显示现有数据
\echo '📊 当前exempt_users数据:'
SELECT user_id, username, reason, created_at FROM exempt_users;
EOF

echo ""
echo "🔄 重启Discord Bot以应用修复..."
docker-compose restart discord-bot

echo ""
echo "⏳ 等待Discord Bot启动..."
sleep 10

echo ""
echo "📝 检查Discord Bot日志..."
docker-compose logs --tail=15 discord-bot

echo ""
echo "✅ 数据库模式修复完成！"
echo "========================="
echo ""
echo "修复内容："
echo "✓ 添加了exempt_users表的reason字段"
echo "✓ 为现有用户设置了默认reason值"
echo "✓ 重启了Discord Bot服务"
echo ""
echo "测试建议："
echo "在Discord中测试CT命令，应该不再出现数据库错误"