#!/bin/bash
# VPS Docker更新脚本 - 仅更新容器，不涉及Git操作
# 适用于手动上传代码后的Docker重建

echo "🚀 开始VPS Docker更新..."

# 确保在正确的目录
cd /opt/discord-bot || { echo "❌ 目录不存在"; exit 1; }

# 显示当前文件状态
echo "📁 当前目录文件列表:"
ls -la

# 检查关键文件
echo "🔍 检查关键文件..."
CRITICAL_FILES=(
    "bot.py"
    "multi_ai_service.py"
    "config/simple_ai_templates.json" 
    "models.py"
    "webhook_service.py"
    "docker-compose.yml"
    "Dockerfile"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file ($(stat -f%z "$file" 2>/dev/null || stat -c%s "$file") bytes)"
    else
        echo "❌ $file 缺失"
    fi
done

# 备份当前容器状态
echo "💾 备份当前容器状态..."
docker-compose ps > container_status_backup_$(date +%Y%m%d_%H%M%S).txt

# 停止现有容器
echo "⏹️ 停止现有容器..."
docker-compose down

# 清理旧镜像（可选）
echo "🧹 清理旧Docker镜像..."
docker image prune -f

# 重建Discord Bot镜像
echo "🔨 重建Discord Bot镜像（无缓存）..."
docker-compose build --no-cache discord-bot

if [ $? -ne 0 ]; then
    echo "❌ Docker镜像构建失败"
    exit 1
fi

# 检查环境配置
echo "🔧 验证环境配置..."
if [ -f ".env" ]; then
    echo "✅ .env文件存在"
    # 验证关键环境变量
    REQUIRED_ENV=(
        "DISCORD_TOKEN"
        "DATABASE_URL"
        "GEMINI_API_KEY"
        "ANTHROPIC_API_KEY"
    )
    
    for env_var in "${REQUIRED_ENV[@]}"; do
        if grep -q "^${env_var}=" .env; then
            echo "✅ $env_var 已配置"
        else
            echo "⚠️ $env_var 可能缺失"
        fi
    done
else
    echo "❌ .env文件不存在"
    exit 1
fi

# 启动更新后的服务
echo "🚀 启动更新后的服务..."
docker-compose up -d

# 等待服务启动完成
echo "⏳ 等待服务启动完成..."
sleep 15

# 检查容器状态
echo "📊 检查容器运行状态..."
docker-compose ps

# 检查服务日志
echo "📋 显示最新启动日志..."
echo "=== Discord Bot 日志 ==="
docker-compose logs --tail=30 discord-bot

echo "=== Config Server 日志 ==="
docker-compose logs --tail=10 config-server

# 健康检查
echo "🏥 执行健康检查..."
sleep 5

# API健康检查
if curl -f -s http://localhost:5000/api/health >/dev/null 2>&1; then
    echo "✅ API服务运行正常"
    
    # AI模型状态检查
    echo "🤖 检查AI模型状态..."
    curl -s http://localhost:5000/api/ai-status | head -c 300
    echo ""
else
    echo "❌ API服务无响应"
    echo "检查端口5000是否被占用:"
    netstat -tlnp | grep :5000 || ss -tlnp | grep :5000
fi

# 配置服务检查
if curl -f -s http://localhost:8081 >/dev/null 2>&1; then
    echo "✅ 配置服务运行正常"
else
    echo "⚠️ 配置服务可能未启动"
fi

echo ""
echo "🎉 VPS Docker更新完成！"
echo ""
echo "📝 本次更新内容："
echo "  ✓ Gemini 2.5 Pro 角色配置优化"
echo "  ✓ 多AI模型配额管理和故障转移"
echo "  ✓ TradersPost命令修复 (!traderpost/!traderspost)"
echo "  ✓ DMChannel属性错误修复"
echo "  ✓ 增强的错误处理和日志记录"
echo ""
echo "🔧 监控命令："
echo "  docker-compose logs -f discord-bot    # 查看实时日志"
echo "  docker-compose ps                     # 查看容器状态"
echo "  curl http://localhost:5000/api/health # API健康检查"
echo ""
if [ -f "container_status_backup_$(date +%Y%m%d)*.txt" ]; then
    echo "💾 容器状态备份已保存"
fi
