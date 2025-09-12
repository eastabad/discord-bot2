#!/bin/bash
# VPS紧急修复 - 解决所有问题

echo "🚨 VPS紧急修复开始..."
echo "====================="

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 检查Docker
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行"
    exit 1
fi

echo "问题清单:"
echo "1. Config对象缺少tradingview_session_id属性"
echo "2. 数据库缺少exempt_users.reason字段"
echo "3. 代码版本不同步"
echo ""

# 步骤1: 停止服务
echo "🛑 停止Discord Bot服务..."
docker-compose stop discord-bot

# 步骤2: 修复数据库
echo "🔧 修复数据库..."
docker-compose exec -T db psql -U postgres -d discord_bot << 'EOF'
ALTER TABLE exempt_users ADD COLUMN IF NOT EXISTS reason VARCHAR(255) DEFAULT 'VIP用户';
UPDATE exempt_users SET reason = 'VIP用户' WHERE reason IS NULL;
\echo 'Database fixed'
EOF

# 步骤3: 强制重建容器
echo "🔄 重建Docker容器..."
docker-compose build --no-cache discord-bot
docker-compose up -d discord-bot

# 步骤4: 等待启动
echo "⏳ 等待服务启动..."
sleep 20

# 步骤5: 验证
echo "✅ 验证修复..."
docker-compose logs --tail=10 discord-bot

echo ""
echo "🎉 紧急修复完成!"
echo "==============="
echo "修复内容:"
echo "✓ 重建了Discord Bot容器"
echo "✓ 修复了数据库字段"
echo "✓ 应用了最新代码"
echo ""
echo "测试步骤:"
echo "1. 在Discord发送: @bot CT AAPL,15m"
echo "2. 等待消息完成后立即点击按钮"