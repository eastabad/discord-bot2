#!/bin/bash
# =================================================================
# TDbot Discord Bot 数据库快速修复脚本
# 修复TradingView webhook数据表结构问题
# =================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then
   error "此脚本需要root权限运行"
   exit 1
fi

log "开始修复TradingView数据库表结构..."

# 检测Docker Compose命令
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# 1. 停止容器
log "停止Docker容器..."
$COMPOSE_CMD down

# 2. 备份当前数据（可选）
log "创建数据库备份..."
if docker volume ls | grep -q discord-bot_postgres_data; then
    docker run --rm -v discord-bot_postgres_data:/source -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /source .
    success "数据库已备份到当前目录"
fi

# 3. 清理数据卷
log "清理数据卷（重新初始化数据库）..."
docker volume rm discord-bot_postgres_data 2>/dev/null || warn "数据卷可能不存在"

# 4. 重新启动服务
log "重新启动服务..."
$COMPOSE_CMD up -d

# 5. 等待数据库初始化
log "等待数据库初始化..."
sleep 20

# 6. 验证表结构
log "验证数据库表结构..."
if docker exec discord-bot-db psql -U postgres -d discord_bot -c "\d tradingview_data" >/dev/null 2>&1; then
    success "tradingview_data表创建成功"
    
    # 显示表结构
    echo "当前表结构："
    docker exec discord-bot-db psql -U postgres -d discord_bot -c "\d tradingview_data"
else
    error "表创建失败"
    exit 1
fi

# 7. 测试webhook接收
log "测试webhook接收功能..."
sleep 10

if curl -s http://localhost:5000/api/health >/dev/null; then
    success "API服务正常运行"
    
    # 测试webhook端点
    echo "测试webhook..."
    curl -X POST http://localhost:5000/webhook/test \
      -H "Content-Type: application/json" \
      -d '{"ticker": "TEST", "action": "buy", "quantity": 100, "data": {"test": true}}' \
      2>/dev/null && success "Webhook测试成功" || warn "Webhook测试失败"
else
    warn "API服务可能还在启动中"
fi

# 8. 检查服务状态
log "检查服务状态..."
echo "=== Docker容器状态 ==="
docker ps

echo -e "\n=== 最新日志 ==="
echo "Discord Bot主服务："
docker logs discord-bot-main --tail=5

echo -e "\n数据库服务："
docker logs discord-bot-db --tail=5

success "=============================="
success "数据库修复完成！"
success "=============================="

log "修复内容："
log "✓ 清理并重新初始化PostgreSQL数据库"
log "✓ 使用新的tradingview_data表结构"
log "✓ 包含所有必需字段：data_type, action, quantity等"
log "✓ 重启所有Docker服务"
echo
log "服务状态："
log "- 主服务: http://localhost:5000"
log "- 配置服务: http://localhost:8081"
log "- API健康检查: http://localhost:5000/api/health"
echo
warn "注意：数据库已重新初始化，之前的数据已清空"
warn "如果需要恢复数据，请使用备份文件进行恢复"
echo
log "如果TradingView webhook仍然失败，请："
log "1. 检查Discord Bot日志: docker logs discord-bot-main -f"
log "2. 验证.env文件中的配置"
log "3. 确认TradingView发送的数据格式"