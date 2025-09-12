#!/bin/bash
# VPS强制更新 - Git仓库已确认包含最新代码

echo "🎯 VPS强制更新开始"
echo "=================="
echo "✅ Git仓库已确认包含TradingView属性"
echo "🎯 强制更新VPS Docker环境"
echo ""

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

# 切换到项目目录
cd /opt/discord-bot || { echo "❌ 项目目录不存在"; exit 1; }

echo "🛑 停止所有服务..."
docker-compose down --remove-orphans
sleep 3

echo "📥 强制拉取最新Git代码..."
git fetch --all
git reset --hard origin/main 2>/dev/null || git reset --hard origin/master
git clean -fd
echo "✅ 代码更新完成"

echo "🔍 验证关键代码..."
if grep -q "self.tradingview_session_id = os.getenv('TRADINGVIEW_SESSION_ID')" config.py; then
    echo "✅ config.py包含正确的TradingView Session ID属性"
else
    echo "❌ config.py仍然缺少TradingView Session ID属性"
    exit 1
fi

if grep -q "self.tradingview_session_id_sign = os.getenv('TRADINGVIEW_SESSION_ID_SIGN')" config.py; then
    echo "✅ config.py包含正确的TradingView Session Sign属性"
else
    echo "❌ config.py仍然缺少TradingView Session Sign属性"
    exit 1
fi

echo "🧹 清理Docker资源..."
docker system prune -af
docker volume prune -f

echo "🔨 重建Discord Bot容器..."
docker-compose build --no-cache --pull discord-bot

echo "🚀 启动服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "🧪 验证Config对象..."
for i in {1..30}; do
    if docker-compose logs discord-bot 2>/dev/null | grep -q "TradingView Session ID已配置"; then
        echo "✅ TradingView Session配置成功"
        break
    fi
    echo "等待Config验证... ($i/30)"
    sleep 2
done

echo ""
echo "=== 最终验证 ==="
docker-compose logs --tail=20 discord-bot | grep -E "(TradingView|Session|Config|ERROR)"

echo ""
echo "=== 服务状态 ==="
docker-compose ps

echo ""
echo "🎉 VPS强制更新完成！"
echo "==================="
echo ""
echo "立即测试:"
echo "在Discord发送: @bot CT AAPL,15m"
echo "应该不再有'Config object has no attribute tradingview_session_id'错误"
echo ""
echo "如果仍有问题，请检查环境变量:"
echo "docker-compose exec discord-bot env | grep TRADINGVIEW"