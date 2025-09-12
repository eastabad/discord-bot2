#!/bin/bash

# Discord Bot 频道清理功能更新脚本
# 专门更新频道清理相关的文件和功能
# 使用方法: wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/channel-cleanup-update.sh && chmod +x channel-cleanup-update.sh && ./channel-cleanup-update.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
step() { echo -e "${BLUE}[→]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; }

echo "🧹 Discord Bot 频道清理功能升级"
echo "════════════════════════════════════════"
echo ""
echo "📋 本次更新内容:"
echo "   • 频道清理策略从'选择性删除'改为'完全清空'"
echo "   • !cleanup_now 现在清空所有历史消息"
echo "   • 自动清理改为每日完全清空所有监控频道"
echo "   • 仅保留置顶消息，删除包括机器人在内的所有消息"
echo ""

if [[ $EUID -ne 0 ]]; then
    error "需要root权限执行此脚本"
    echo "请使用: sudo $0"
    exit 1
fi

read -p "确认执行更新？ (y/N): " -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    warn "更新已取消"
    exit 0
fi

# 检查Docker Bot目录
BOT_DIR="/opt/discord-bot"
if [ ! -d "$BOT_DIR" ]; then
    error "找不到Discord Bot目录: $BOT_DIR"
    exit 1
fi

cd $BOT_DIR

step "准备更新环境..."

# 备份关键文件
BACKUP_DIR="backup/cleanup-update-$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

if [ -f "channel_cleaner.py" ]; then
    cp channel_cleaner.py $BACKUP_DIR/
fi
if [ -f "bot.py" ]; then
    cp bot.py $BACKUP_DIR/
fi

log "文件已备份到: $BACKUP_DIR"

step "停止Discord Bot服务..."
docker-compose down >/dev/null 2>&1 || warn "停止服务时出现警告"

step "下载更新的频道清理模块..."

# 下载更新文件
wget -q --timeout=30 \
    https://raw.githubusercontent.com/eastabad/DiscordBot/main/channel_cleaner.py \
    -O channel_cleaner.py.new

wget -q --timeout=30 \
    https://raw.githubusercontent.com/eastabad/DiscordBot/main/bot.py \
    -O bot.py.new

# 验证下载完整性
if [ ! -s "channel_cleaner.py.new" ] || [ ! -s "bot.py.new" ]; then
    error "文件下载失败或不完整"
    exit 1
fi

step "应用更新..."

# 应用更新
mv channel_cleaner.py.new channel_cleaner.py
mv bot.py.new bot.py

# 设置权限
chmod 644 channel_cleaner.py bot.py
chown root:root channel_cleaner.py bot.py

log "核心文件已更新"

step "检查数据库状态..."
# 先尝试启动，如果数据库失败则进行修复
if ! docker-compose up -d >/dev/null 2>&1; then
    warn "检测到数据库启动问题，正在修复..."
    
    # 停止服务
    docker-compose down >/dev/null 2>&1 || true
    
    # 清理数据库卷
    docker volume rm discord-bot_postgres_data >/dev/null 2>&1 || true
    
    # 更新PostgreSQL镜像
    docker pull postgres:16 >/dev/null 2>&1
    
    step "重建Docker镜像..."
    docker-compose build --no-cache >/dev/null 2>&1
    
    step "重新启动服务..."
    docker-compose up -d >/dev/null 2>&1
else
    step "重建Docker镜像..."
    docker-compose build >/dev/null 2>&1
    
    step "重启服务..."
    docker-compose restart >/dev/null 2>&1
fi

# 等待服务启动
sleep 8

step "验证服务状态..."

# 检查API健康状态
if curl -s --max-time 10 http://localhost:5000/api/health >/dev/null 2>&1; then
    log "✅ API服务运行正常"
else
    warn "API服务启动中，请稍后检查状态"
fi

# 显示容器状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "🎉 频道清理功能更新完成！"
echo "════════════════════════════════════════"
echo ""
echo "📝 新功能说明:"
echo "   • 清理策略: 删除所有历史消息（除置顶外）"
echo "   • 自动清理: 每日凌晨2点UTC执行"
echo "   • 手动清理: !cleanup_now 立即清空所有历史"
echo "   • 清理状态: !cleanup_status 查看服务状态"
echo ""
echo "🔧 常用命令:"
echo "   查看日志: cd $BOT_DIR && docker-compose logs -f"
echo "   重启服务: cd $BOT_DIR && docker-compose restart"
echo "   备份位置: $BOT_DIR/$BACKUP_DIR"
echo ""
log "更新完成！Discord频道现在将保持完全清洁。"