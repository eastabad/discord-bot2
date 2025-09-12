#!/bin/bash
# 文件同步到VPS脚本 (本地使用)

VPS_HOST="your-vps-host.com"
VPS_USER="root"
VPS_PATH="/opt/discord-bot"

echo "🔄 准备同步文件到VPS..."

# 核心文件列表
FILES=(
    "bot.py"
    "multi_ai_service.py"
    "config/simple_ai_templates.json"
    "models.py" 
    "webhook_service.py"
    "config.py"
    "simple_ai_template.py"
)

echo "📁 检查本地文件..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        echo "✅ $file ($size bytes)"
    else
        echo "❌ $file 不存在"
        exit 1
    fi
done

echo ""
echo "🚀 开始同步到VPS: $VPS_USER@$VPS_HOST:$VPS_PATH"
echo "注意: 请确保已配置SSH密钥认证"
echo ""

# 创建备份目录
ssh $VPS_USER@$VPS_HOST "mkdir -p $VPS_PATH/backup_$(date +%Y%m%d_%H%M%S)"

# 同步文件
for file in "${FILES[@]}"; do
    echo "📤 同步 $file..."
    
    # 备份原文件
    ssh $VPS_USER@$VPS_HOST "cp $VPS_PATH/$file $VPS_PATH/backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null" || true
    
    # 上传新文件
    scp "$file" $VPS_USER@$VPS_HOST:$VPS_PATH/$file
    
    if [ $? -eq 0 ]; then
        echo "✅ $file 同步成功"
    else
        echo "❌ $file 同步失败"
        exit 1
    fi
done

echo ""
echo "📋 同步完成! 接下来在VPS上执行:"
echo "cd $VPS_PATH && ./VPS_DOCKER_UPDATE.sh"

