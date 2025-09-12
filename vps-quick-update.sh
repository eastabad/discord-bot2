#!/bin/bash

# Discord Bot VPS 快速更新脚本 - 频道清理功能升级
# 使用方法: wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/vps-quick-update.sh && chmod +x vps-quick-update.sh && ./vps-quick-update.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "==================== Discord Bot 快速更新 ===================="
echo "📋 本次更新内容:"
echo "   ✅ 频道清理功能完全重构 - 改为清空所有历史消息"
echo "   ✅ 自动清理策略升级 - 每日凌晨2点UTC完全清空"
echo "   ✅ 手动清理命令增强 - !cleanup_now 现在清空所有历史"
echo "   ✅ 保留策略优化 - 仅保留置顶消息"
echo ""

read -p "是否继续更新？(y/N): " -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "更新已取消"
    exit 0
fi

# 检查环境
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限，请使用: sudo $0"
    exit 1
fi

if [ ! -d "/opt/discord-bot" ]; then
    log_error "Discord Bot目录不存在: /opt/discord-bot"
    exit 1
fi

cd /opt/discord-bot

# 备份环境变量
log_info "备份当前配置..."
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
fi

# 停止服务
log_info "停止Discord Bot服务..."
docker-compose down 2>/dev/null || log_warn "停止服务时出现警告"

# 下载关键更新文件
log_info "下载更新文件..."
TEMP_DIR="/tmp/discord-bot-quick-update"
mkdir -p $TEMP_DIR

# 下载主要更新文件
wget -q https://raw.githubusercontent.com/eastabad/DiscordBot/main/channel_cleaner.py -O $TEMP_DIR/channel_cleaner.py
wget -q https://raw.githubusercontent.com/eastabad/DiscordBot/main/bot.py -O $TEMP_DIR/bot.py
wget -q https://raw.githubusercontent.com/eastabad/DiscordBot/main/main_with_api.py -O $TEMP_DIR/main_with_api.py

if [ $? -ne 0 ]; then
    log_error "下载文件失败"
    exit 1
fi

# 验证文件完整性
for file in channel_cleaner.py bot.py main_with_api.py; do
    if [ ! -f "$TEMP_DIR/$file" ] || [ ! -s "$TEMP_DIR/$file" ]; then
        log_error "文件 $file 下载不完整"
        exit 1
    fi
done

# 备份旧文件
log_info "备份旧文件..."
mkdir -p backup/$(date +%Y%m%d_%H%M%S)
cp channel_cleaner.py bot.py main_with_api.py backup/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# 更新文件
log_info "更新核心文件..."
cp $TEMP_DIR/channel_cleaner.py ./
cp $TEMP_DIR/bot.py ./
cp $TEMP_DIR/main_with_api.py ./

# 恢复环境变量
if [ -f ".env.backup.$(date +%Y%m%d)_"* ]; then
    latest_backup=$(ls -t .env.backup.* | head -n1)
    cp $latest_backup .env
    log_info "环境变量已恢复"
fi

# 重建并启动
log_info "重建Docker镜像..."
docker-compose build --no-cache

log_info "启动服务..."
docker-compose up -d

# 验证服务
sleep 8
log_info "验证服务状态..."

if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
    log_info "✅ API服务运行正常"
else
    log_warn "⚠️  API服务启动中，请稍后检查"
fi

# 清理
rm -rf $TEMP_DIR

echo ""
echo "==================== 更新完成 ===================="
log_info "🎉 频道清理功能已升级！"
echo ""
echo "📋 新功能说明:"
echo "   • !cleanup_now - 现在会清空所有历史消息"
echo "   • 自动清理 - 每日凌晨2点UTC完全清空监控频道"
echo "   • 保留策略 - 仅保留置顶消息，删除所有其他消息"
echo ""
echo "🔧 管理命令:"
echo "   查看日志: docker-compose logs -f"
echo "   重启服务: docker-compose restart"
echo ""
log_info "更新完成，Discord Bot现在使用增强的频道清理功能！"
echo "=================================================="