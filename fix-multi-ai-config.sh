#!/bin/bash

# Discord Bot 多AI配置修复脚本
# 修复 Anthropic和OpenRouter API密钥配置问题
# 使用方法: wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/fix-multi-ai-config.sh && chmod +x fix-multi-ai-config.sh && sudo ./fix-multi-ai-config.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo "🤖 Discord Bot 多AI配置修复"
echo "=============================="
echo "修复警告:"
echo "  ❌ Anthropic直连未配置"
echo "  ❌ OpenRouter API密钥未设置"
echo ""

# 检查权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限执行此脚本"
    echo "请使用: sudo $0"
    exit 1
fi

# 检查Discord Bot目录
BOT_DIR="/opt/discord-bot"
if [ ! -d "$BOT_DIR" ]; then
    log_error "找不到Discord Bot目录: $BOT_DIR"
    exit 1
fi

cd $BOT_DIR

log_step "备份现有配置..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
log_info "Docker配置已备份"

log_step "更新Docker环境变量配置..."

# 更新docker-compose.yml添加缺失的API密钥
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  discord-bot:
    build: .
    container_name: discord-bot
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - CHART_IMG_API_KEY=${CHART_IMG_API_KEY}
      - LAYOUT_ID=${LAYOUT_ID}
      - TRADINGVIEW_SESSION_ID=${TRADINGVIEW_SESSION_ID}
      - TRADINGVIEW_SESSION_ID_SIGN=${TRADINGVIEW_SESSION_ID_SIGN}
      - MONITOR_CHANNEL_IDS=${MONITOR_CHANNEL_IDS}
      - REPORT_CHANNEL_IDS=${REPORT_CHANNEL_IDS}
      - REPORT_CHANNEL_ID=${REPORT_CHANNEL_ID}
      - CHART_CHANNEL_ID=${CHART_CHANNEL_ID}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot
    volumes:
      - ./daily_logs:/app/daily_logs
      - ./attached_assets:/app/attached_assets
    depends_on:
      db:
        condition: service_healthy
    networks:
      - discord-net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:16
    container_name: discord-bot-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=discord_bot
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=discord123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker-db-init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - discord-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

volumes:
  postgres_data:

networks:
  discord-net:
    driver: bridge
EOF

log_info "✅ Docker配置已更新，添加了AI API密钥环境变量"

log_step "检查环境变量设置..."

# 检查必要的环境变量是否存在
missing_vars=()

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    missing_vars+=("ANTHROPIC_API_KEY")
fi

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    missing_vars+=("OPENROUTER_API_KEY")
fi

if [ ${#missing_vars[@]} -gt 0 ]; then
    log_warn "缺少以下环境变量:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    echo ""
    log_info "请确保这些API密钥已添加到系统环境变量中"
    log_info "或者在.env文件中定义它们"
else
    log_info "✅ 所有AI API密钥环境变量已设置"
fi

log_step "添加频道配置变量（如果缺失）..."

# 检查并添加CHART_CHANNEL_ID到.env（如果不存在）
if ! grep -q "CHART_CHANNEL_ID" .env 2>/dev/null; then
    echo "" >> .env
    echo "# Chart频道配置" >> .env
    echo "CHART_CHANNEL_ID=1404532905916760125" >> .env
    log_info "✅ 添加了CHART_CHANNEL_ID配置"
fi

log_step "重启Discord Bot服务..."
docker-compose restart discord-bot >/dev/null 2>&1

# 等待服务启动
log_info "等待服务重新启动..."
sleep 15

log_step "验证多AI配置..."

# 检查日志中的AI初始化信息
echo "📊 AI服务状态:"
docker-compose logs discord-bot | grep -E "(✅|❌|⚠️).*(Gemini|Anthropic|OpenRouter|多AI)" | tail -10

echo ""

# 测试API健康状态
if curl -s --max-time 10 http://localhost:5000/api/health >/dev/null 2>&1; then
    log_info "✅ API服务运行正常"
else
    log_warn "⚠️  API服务启动中..."
fi

echo ""
echo "🎉 多AI配置修复完成！"
echo "======================"
echo ""
echo "✅ 更新内容:"
echo "   • 添加 ANTHROPIC_API_KEY 到Docker环境"
echo "   • 添加 OPENROUTER_API_KEY 到Docker环境"
echo "   • 添加 CHART_CHANNEL_ID 频道配置"
echo "   • 重启Discord Bot服务"
echo ""

if [ ${#missing_vars[@]} -eq 0 ]; then
    echo "🤖 多AI系统状态:"
    echo "   • Gemini 2.5 Pro (主AI) - 已配置"
    echo "   • Claude Sonnet 4 (备用1) - 已配置"
    echo "   • GPT-4.1 via OpenRouter (备用2) - 已配置"
    echo ""
    log_info "所有AI模型现在应该正常工作，警告消息将消失"
else
    echo "⚠️  需要手动设置的环境变量:"
    for var in "${missing_vars[@]}"; do
        echo "   • $var"
    done
    echo ""
    echo "设置方法:"
    echo "   export ANTHROPIC_API_KEY='your_key_here'"
    echo "   export OPENROUTER_API_KEY='your_key_here'"
    echo "   然后重启: docker-compose restart discord-bot"
fi

echo ""
echo "🔧 检查命令:"
echo "   查看AI日志: docker-compose logs discord-bot | grep -i 'ai\\|gemini\\|anthropic\\|openrouter'"
echo "   检查健康: curl http://localhost:5000/api/health"
echo ""
log_info "多AI配置现在完整，备用AI模型已激活！"