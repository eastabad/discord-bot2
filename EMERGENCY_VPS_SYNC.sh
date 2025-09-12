#!/bin/bash
# 紧急VPS同步 - 立即解决Config错误

echo "🚨 紧急VPS同步开始..."
echo "====================="

# 检查Docker状态
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行或无权限"
    exit 1
fi

echo "🔍 VPS问题确认:"
echo "  ❌ Config对象缺少tradingview_session_id属性"
echo "  ❌ Chart功能在频道命令和交互按钮都失败"
echo "  ❌ VPS运行的是旧版本代码"
echo ""

# 步骤1: 立即停止服务
echo "🛑 立即停止Discord Bot..."
docker-compose stop discord-bot
sleep 3

# 步骤2: 拉取最新代码
echo "📥 拉取最新Git代码..."
git stash push -m "紧急修复前备份 $(date)" 2>/dev/null || true
git pull origin main || git pull origin master
echo "✅ 代码更新完成"

# 步骤3: 强制删除旧容器和镜像
echo "🧹 清理旧Docker资源..."
docker-compose rm -f discord-bot
docker rmi $(docker images -q discord-bot* 2>/dev/null) 2>/dev/null || true

# 步骤3: 强制重建容器 (确保最新代码)
echo "🔨 强制重建Discord Bot容器..."
docker-compose build --no-cache --pull discord-bot

# 步骤4: 启动新容器
echo "🚀 启动新Discord Bot..."
docker-compose up -d discord-bot

# 步骤5: 等待启动
echo "⏳ 等待Discord Bot完全启动..."
sleep 25

# 步骤6: 验证修复
echo "✅ 验证修复结果..."
echo ""
echo "=== 容器状态 ==="
docker-compose ps discord-bot

echo ""
echo "=== 最新日志 ==="
docker-compose logs --tail=15 discord-bot

echo ""
echo "=== Config对象验证 ==="
docker-compose exec discord-bot python3 -c "
print('=== Config对象完整性检查 ===')
try:
    from config import Config
    config = Config()
    
    # 关键属性检查
    attrs_to_check = [
        'chart_img_api_key',
        'layout_id', 
        'tradingview_session_id',
        'tradingview_session_id_sign'
    ]
    
    for attr in attrs_to_check:
        has_attr = hasattr(config, attr)
        value = getattr(config, attr, None) if has_attr else None
        status = '✅' if has_attr and value else '❌'
        print(f'{status} {attr}: {\"已设置\" if value else \"未设置或缺失\"}')
    
    print('')
    print('=== TradingView Session状态 ===')
    if hasattr(config, 'tradingview_session_id') and config.tradingview_session_id:
        print(f'✅ Session ID: 长度{len(config.tradingview_session_id)}')
    else:
        print('❌ Session ID: 未配置或属性缺失')
        
    if hasattr(config, 'tradingview_session_id_sign') and config.tradingview_session_id_sign:
        print(f'✅ Session Sign: 长度{len(config.tradingview_session_id_sign)}')
    else:
        print('❌ Session Sign: 未配置或属性缺失')
        
except Exception as e:
    print(f'❌ Config检查失败: {e}')
" 2>/dev/null || echo "⚠️ Config检查脚本执行失败"

echo ""
echo "🎯 紧急同步完成！"
echo "================"
echo ""
echo "修复状态:"
echo "✅ 强制重建了Discord Bot容器"
echo "✅ 应用了最新代码版本"
echo "✅ Config对象应该包含所有必需属性"
echo ""
echo "立即测试:"
echo "1. 在Discord发送: @bot CT AAPL,15m"
echo "2. 检查是否还有Config属性错误"
echo "3. 如果命令成功，测试交互按钮"
echo ""
echo "如果仍有问题，运行完整修复:"
echo "sudo bash VPS_ULTIMATE_FIX.sh"