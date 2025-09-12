#!/bin/bash
# VPS手动更新脚本 - Order Block完整功能包
# 执行位置: /opt/discord-bot

set -e  # 遇到错误时退出

echo "🔄 开始更新Discord Bot - Order Block完整功能"
echo "============================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. 检查当前目录
log_info "检查当前目录..."
if [ ! -f "docker-compose.yml" ]; then
    log_error "请确保在 /opt/discord-bot 目录中执行此脚本"
    exit 1
fi
log_success "目录检查通过"

# 2. 备份当前配置
log_info "备份当前配置..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
[ -f ".env" ] && cp .env "$BACKUP_DIR/"
[ -f "orderblock_routes.conf" ] && cp orderblock_routes.conf "$BACKUP_DIR/"
log_success "配置已备份到: $BACKUP_DIR"

# 3. 停止现有服务
log_info "停止现有服务..."
docker-compose down
log_success "服务已停止"

# 4. 检查环境变量
log_info "检查环境变量配置..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        log_warning ".env不存在，从模板创建..."
        cp .env.example .env
        log_warning "请编辑 .env 文件添加必需的配置"
    else
        log_error ".env.example 文件不存在"
        exit 1
    fi
fi

# 检查关键环境变量
REQUIRED_VARS=("DISCORD_TOKEN" "GEMINI_API_KEY" "OB_LAYOUT_ID")
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" .env; then
        log_warning "环境变量 $var 需要配置"
    fi
done

# 5. 检查Order Block配置
log_info "检查Order Block路由配置..."
if [ ! -f "orderblock_routes.conf" ]; then
    log_warning "创建示例 orderblock_routes.conf..."
    cat > orderblock_routes.conf << EOF
# Order Block路由配置
# 格式: TICKER=CHANNEL_ID1,CHANNEL_ID2
NVDA=1405694945809141781
COIN=1405694949533548684
EOF
    log_info "请根据需要编辑 orderblock_routes.conf"
fi

# 6. 设置权限
log_info "设置文件权限..."
chmod +x *.py *.sh
log_success "权限设置完成"

# 7. 构建新镜像
log_info "构建Docker镜像..."
docker-compose build --no-cache discord-bot
if [ $? -eq 0 ]; then
    log_success "镜像构建成功"
else
    log_error "镜像构建失败"
    exit 1
fi

# 8. 启动服务
log_info "启动服务..."
docker-compose up -d
if [ $? -eq 0 ]; then
    log_success "服务已启动"
else
    log_error "服务启动失败"
    exit 1
fi

# 9. 等待服务就绪
log_info "等待服务就绪..."
sleep 10

# 10. 健康检查
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        log_success "API服务器已就绪"
        break
    fi
    
    if [ $i -eq 30 ]; then
        log_error "API服务器启动超时"
        exit 1
    fi
    
    sleep 2
done

# 11. 显示服务状态
log_info "服务状态:"
docker-compose ps

echo ""
echo "============================================="
log_success "Order Block功能更新完成!"
echo ""
log_info "新增功能:"
echo "  ✅ OB Discord命令: @bot OB NVDA,15m"
echo "  ✅ obData字段自动解析"
echo "  ✅ Order Block专用webhook"
echo "  ✅ 供需区字段增强"
echo "  ✅ 英文界面优化"
echo "  ✅ 自动图表集成"
echo ""
log_info "测试建议:"
echo "  - API健康: curl http://localhost:5000/api/health"
echo "  - 查看日志: docker-compose logs -f discord-bot"
echo "  - Discord测试: @TD AIassistant OB NVDA,15m"
echo ""
log_info "管理工具:"
echo "  - 路由管理: python3 manage_routes.py list"
echo "  - 配置查看: cat orderblock_routes.conf"
echo ""