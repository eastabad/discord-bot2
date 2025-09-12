#!/bin/bash
# VPS完整更新脚本 - 包含所有修复

echo "🚀 开始VPS完整更新部署..."
echo "=============================="

# 检查Docker是否运行
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker未运行或无权限访问"
    exit 1
fi

echo "📋 本次更新包含："
echo "✓ 频道权限逻辑修复"
echo "✓ Chart-img API完整修复 (基于官方文档4参数)"
echo "✓ 数据库模式修复 (exempt_users.reason字段)"
echo "✓ 配置对象属性修复"
echo "✓ 所有代码更新"
echo ""

# 步骤1: 运行关键修复
echo "🔧 步骤1: 运行关键修复..."
if [ -f VPS_CRITICAL_FIXES.sh ]; then
    bash VPS_CRITICAL_FIXES.sh
else
    echo "⚠️ 关键修复脚本不存在，使用基础数据库修复"
    if [ -f VPS_DATABASE_FIX.sh ]; then
        bash VPS_DATABASE_FIX.sh
    fi
fi

echo ""
echo "⏳ 等待5秒后继续..."
sleep 5

# 步骤2: 部署代码修复
echo "🚀 步骤2: 部署代码修复..."
bash CHANNEL_FIX_DEPLOY.sh

echo ""
echo "🎉 VPS完整更新完成！"
echo "===================="
echo ""
echo "已完成的修复："
echo "✅ 数据库模式更新 (exempt_users.reason字段)"
echo "✅ 频道权限逻辑修复 (CT命令在chart频道正常)"
echo "✅ Chart-img API修复 (v2接口, 4参数支持)"
echo "✅ 配置对象属性修复 (tradingview_session_id)"
echo "✅ Discord Bot服务重启"
echo ""
echo "验证测试："
echo "1. 在Discord chart频道测试: @TDbot-tradingview CT TSLA,15m"
echo "2. 点击交互按钮测试图表生成"
echo "3. 检查用户限制功能是否正常"
echo ""
echo "查看实时日志："
echo "docker-compose logs -f discord-bot"