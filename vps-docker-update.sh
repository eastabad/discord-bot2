#!/bin/bash

# Discord Bot VPS Docker One-Click Update Script
# 使用方法: wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/vps-docker-update.sh && chmod +x vps-docker-update.sh && ./vps-docker-update.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        echo "请使用: sudo $0"
        exit 1
    fi
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_info "Docker环境检查通过"
}

# 备份当前环境变量
backup_env() {
    log_step "备份当前环境变量..."
    
    if [ -f "/opt/discord-bot/.env" ]; then
        cp /opt/discord-bot/.env /opt/discord-bot/.env.backup.$(date +%Y%m%d_%H%M%S)
        log_info "环境变量已备份"
    else
        log_warn "未找到现有的.env文件"
    fi
}

# 停止现有容器
stop_containers() {
    log_step "停止现有Discord Bot容器..."
    
    cd /opt/discord-bot || {
        log_error "Discord Bot目录不存在: /opt/discord-bot"
        exit 1
    }
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down || log_warn "停止容器时出现警告"
        log_info "容器已停止"
    else
        log_warn "未找到docker-compose.yml文件"
    fi
}

# 下载最新代码
download_latest() {
    log_step "下载最新代码..."
    
    # 创建临时目录
    TEMP_DIR="/tmp/discord-bot-update-$(date +%Y%m%d_%H%M%S)"
    mkdir -p $TEMP_DIR
    
    cd $TEMP_DIR
    
    # 下载最新代码
    log_info "从GitHub下载最新代码..."
    wget -q --show-progress https://github.com/eastabad/DiscordBot/archive/refs/heads/main.zip -O discord-bot-latest.zip
    
    if [ $? -ne 0 ]; then
        log_error "下载失败"
        exit 1
    fi
    
    # 解压文件
    log_info "解压代码文件..."
    unzip -q discord-bot-latest.zip
    
    if [ ! -d "DiscordBot-main" ]; then
        log_error "解压失败，未找到代码目录"
        exit 1
    fi
    
    log_info "代码下载完成"
    echo "TEMP_DIR=$TEMP_DIR" > /tmp/discord-bot-update-vars
}

# 更新代码文件
update_files() {
    log_step "更新代码文件..."
    
    source /tmp/discord-bot-update-vars
    
    # 备份旧代码
    if [ -d "/opt/discord-bot/backup" ]; then
        rm -rf /opt/discord-bot/backup
    fi
    mkdir -p /opt/discord-bot/backup
    
    # 备份关键文件
    if [ -f "/opt/discord-bot/.env" ]; then
        cp /opt/discord-bot/.env /opt/discord-bot/backup/
    fi
    if [ -f "/opt/discord-bot/docker-compose.yml" ]; then
        cp /opt/discord-bot/docker-compose.yml /opt/discord-bot/backup/
    fi
    
    log_info "旧文件已备份到 /opt/discord-bot/backup/"
    
    # 复制新文件
    log_info "复制新代码文件..."
    cp -r $TEMP_DIR/DiscordBot-main/* /opt/discord-bot/
    
    # 恢复环境变量文件
    if [ -f "/opt/discord-bot/backup/.env" ]; then
        cp /opt/discord-bot/backup/.env /opt/discord-bot/
        log_info "环境变量文件已恢复"
    fi
    
    # 设置正确的权限
    chown -R root:root /opt/discord-bot
    chmod +x /opt/discord-bot/*.sh
    
    log_info "代码文件更新完成"
}

# 重建Docker镜像
rebuild_docker() {
    log_step "重建Docker镜像..."
    
    cd /opt/discord-bot
    
    # 清理旧镜像（可选）
    log_info "清理未使用的Docker镜像..."
    docker system prune -f || log_warn "清理镜像时出现警告"
    
    # 重建镜像
    log_info "重建Discord Bot镜像..."
    docker-compose build --no-cache
    
    if [ $? -ne 0 ]; then
        log_error "Docker镜像构建失败"
        exit 1
    fi
    
    log_info "Docker镜像重建完成"
}

# 启动服务
start_services() {
    log_step "启动Discord Bot服务..."
    
    cd /opt/discord-bot
    
    # 启动服务
    docker-compose up -d
    
    if [ $? -ne 0 ]; then
        log_error "服务启动失败"
        exit 1
    fi
    
    log_info "服务启动成功"
}

# 验证服务状态
verify_services() {
    log_step "验证服务状态..."
    
    sleep 10  # 等待服务启动
    
    cd /opt/discord-bot
    
    # 检查容器状态
    log_info "检查容器状态..."
    docker-compose ps
    
    # 检查API健康状态
    log_info "检查API健康状态..."
    if curl -s http://localhost:5000/api/health > /dev/null; then
        log_info "✅ API服务运行正常"
    else
        log_warn "⚠️  API服务可能未完全启动，请稍后检查"
    fi
    
    # 显示最近日志
    log_info "最近的服务日志:"
    docker-compose logs --tail=20 discord-bot
}

# 清理临时文件
cleanup() {
    log_step "清理临时文件..."
    
    if [ -f "/tmp/discord-bot-update-vars" ]; then
        source /tmp/discord-bot-update-vars
        if [ -d "$TEMP_DIR" ]; then
            rm -rf $TEMP_DIR
        fi
        rm -f /tmp/discord-bot-update-vars
    fi
    
    log_info "临时文件清理完成"
}

# 显示更新摘要
show_summary() {
    echo ""
    echo "==================== 更新完成 ===================="
    log_info "Discord Bot已成功更新到最新版本"
    echo ""
    echo "📊 服务状态检查:"
    echo "   API服务: http://$(hostname -I | awk '{print $1}'):5000/api/health"
    echo "   数据库: PostgreSQL (Docker内部)"
    echo ""
    echo "🔧 管理命令:"
    echo "   查看日志: cd /opt/discord-bot && docker-compose logs -f"
    echo "   重启服务: cd /opt/discord-bot && docker-compose restart"
    echo "   停止服务: cd /opt/discord-bot && docker-compose down"
    echo ""
    echo "📁 重要目录:"
    echo "   项目目录: /opt/discord-bot"
    echo "   备份目录: /opt/discord-bot/backup"
    echo "   日志目录: /opt/discord-bot/daily_logs"
    echo ""
    log_info "如遇问题，请检查备份文件: /opt/discord-bot/backup/"
    echo "=================================================="
}

# 主函数
main() {
    echo "==================== Discord Bot VPS Docker 一键更新 ===================="
    echo "本脚本将自动更新您的Discord Bot到最新版本"
    echo "更新内容包括: 频道清理功能完全重构、AI模型增强、个人Webhook系统等"
    echo ""
    
    read -p "是否继续更新？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "更新已取消"
        exit 0
    fi
    
    # 执行更新步骤
    check_root
    check_docker
    backup_env
    stop_containers
    download_latest
    update_files
    rebuild_docker
    start_services
    verify_services
    cleanup
    show_summary
    
    log_info "🎉 Discord Bot更新完成！"
}

# 错误处理
trap 'log_error "更新过程中出现错误，正在清理..."; cleanup; exit 1' ERR

# 运行主函数
main "$@"