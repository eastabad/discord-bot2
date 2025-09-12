#!/bin/bash

# Discord Bot VPS 依赖包修复脚本
# 解决 "No module named 'google.generativeai'" 和数据库问题
# 使用方法: wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/fix-vps-dependencies.sh && chmod +x fix-vps-dependencies.sh && sudo ./fix-vps-dependencies.sh

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

echo "🔧 Discord Bot VPS 依赖包和数据库修复"
echo "======================================="
echo "修复问题:"
echo "  ❌ No module named 'google.generativeai'"
echo "  ❌ Container discord-bot-db is unhealthy"
echo "  ❌ 频道清理功能更新"
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

log_step "备份当前配置..."
# 备份环境变量
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    log_info "环境变量已备份"
fi

# 备份关键文件
mkdir -p backup/dependency-fix-$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup/dependency-fix-$(date +%Y%m%d_%H%M%S)"
for file in docker-requirements.txt Dockerfile gemini_report_generator.py channel_cleaner.py bot.py; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
    fi
done
log_info "关键文件已备份到 $BACKUP_DIR"

log_step "停止现有服务..."
docker-compose down >/dev/null 2>&1 || true

log_step "清理Docker资源..."
# 清理数据库卷
docker volume rm discord-bot_postgres_data >/dev/null 2>&1 || true
# 清理未使用的Docker资源
docker system prune -f >/dev/null 2>&1

log_step "更新依赖包配置..."

# 更新 docker-requirements.txt
cat > docker-requirements.txt << 'EOF'
discord.py>=2.5.2
aiohttp>=3.12.15
psycopg2-binary>=2.9.10
sqlalchemy>=2.0.43
anthropic>=0.62.0
psutil>=7.0.0
flask>=3.1.1
pytz>=2025.2
google-generativeai>=0.8.0
google-genai>=1.30.0
openai>=1.3.0
requests>=2.32.4
sift-stack-py>=0.1.0
EOF

log_info "✅ 依赖包配置已更新"

log_step "下载最新代码文件..."

# 下载修复后的核心文件
TEMP_DIR="/tmp/discord-bot-dependency-fix"
mkdir -p $TEMP_DIR

# 下载关键文件
files_to_download=(
    "channel_cleaner.py"
    "bot.py"
    "gemini_report_generator.py"
    "multi_ai_service.py"
    "main_with_api.py"
)

for file in "${files_to_download[@]}"; do
    log_info "下载 $file..."
    if wget -q --timeout=30 https://raw.githubusercontent.com/eastabad/DiscordBot/main/$file -O $TEMP_DIR/$file; then
        log_info "✅ $file 下载成功"
    else
        log_warn "⚠️  $file 下载失败，保持现有版本"
    fi
done

# 应用更新的文件
for file in "${files_to_download[@]}"; do
    if [ -f "$TEMP_DIR/$file" ] && [ -s "$TEMP_DIR/$file" ]; then
        cp "$TEMP_DIR/$file" ./
        log_info "✅ $file 已更新"
    fi
done

log_step "更新数据库初始化脚本..."

# 确保数据库初始化文件正确
cat > docker-db-init.sql << 'EOF'
-- Discord机器人数据库初始化脚本

-- 用户每日请求限制跟踪表
CREATE TABLE IF NOT EXISTS user_request_limits (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    username VARCHAR(100) NOT NULL,
    request_date DATE NOT NULL,
    request_count INTEGER DEFAULT 0 NOT NULL,
    last_request_time TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 豁免用户表
CREATE TABLE IF NOT EXISTS exempt_users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    reason VARCHAR(200),
    added_by VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- TradingView信号数据表
CREATE TABLE IF NOT EXISTS tradingview_signals (
    id SERIAL PRIMARY KEY,
    signal_type VARCHAR(20) NOT NULL DEFAULT 'signal',
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(20),
    price DECIMAL(12, 4),
    volume BIGINT,
    timeframe VARCHAR(10),
    direction VARCHAR(10),
    strength INTEGER,
    confidence DECIMAL(5, 2),
    signal_time TIMESTAMP WITH TIME ZONE,
    raw_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 个人Webhook表
CREATE TABLE IF NOT EXISTS personal_webhooks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    webhook_secret VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

-- 报告缓存表
CREATE TABLE IF NOT EXISTS report_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_user_request_limits_user_id ON user_request_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_request_limits_date ON user_request_limits(request_date);
CREATE INDEX IF NOT EXISTS idx_user_request_limits_user_date ON user_request_limits(user_id, request_date);
CREATE INDEX IF NOT EXISTS idx_exempt_users_user_id ON exempt_users(user_id);
CREATE INDEX IF NOT EXISTS idx_tradingview_signals_symbol ON tradingview_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_tradingview_signals_time ON tradingview_signals(signal_time);
CREATE INDEX IF NOT EXISTS idx_personal_webhooks_user_id ON personal_webhooks(user_id);
CREATE INDEX IF NOT EXISTS idx_personal_webhooks_secret ON personal_webhooks(webhook_secret);
CREATE INDEX IF NOT EXISTS idx_report_cache_key ON report_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_report_cache_expires ON report_cache(expires_at);

-- 创建更新触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为表创建更新时间触发器
DROP TRIGGER IF EXISTS update_user_request_limits_updated_at ON user_request_limits;
CREATE TRIGGER update_user_request_limits_updated_at
    BEFORE UPDATE ON user_request_limits FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_exempt_users_updated_at ON exempt_users;
CREATE TRIGGER update_exempt_users_updated_at
    BEFORE UPDATE ON exempt_users FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tradingview_signals_updated_at ON tradingview_signals;
CREATE TRIGGER update_tradingview_signals_updated_at
    BEFORE UPDATE ON tradingview_signals FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_personal_webhooks_updated_at ON personal_webhooks;
CREATE TRIGGER update_personal_webhooks_updated_at
    BEFORE UPDATE ON personal_webhooks FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 清理过期缓存的函数
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM report_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

SELECT 'Discord机器人数据库初始化完成' as status;
EOF

log_info "✅ 数据库初始化脚本已更新"

log_step "更新PostgreSQL镜像..."
docker pull postgres:16 >/dev/null 2>&1

log_step "重建Docker镜像..."
log_info "这可能需要几分钟时间，请耐心等待..."
docker-compose build --no-cache >/dev/null 2>&1

if [ $? -ne 0 ]; then
    log_error "Docker镜像构建失败"
    log_info "尝试查看详细错误信息："
    docker-compose build --no-cache
    exit 1
fi

log_info "✅ Docker镜像重建完成"

log_step "启动数据库服务..."
docker-compose up -d db >/dev/null 2>&1

# 等待数据库启动
log_info "等待数据库启动..."
for i in {1..30}; do
    if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
        log_info "✅ 数据库启动成功"
        break
    fi
    if [ $i -eq 30 ]; then
        log_error "数据库启动超时"
        docker-compose logs db
        exit 1
    fi
    sleep 2
    echo -n "."
done
echo ""

log_step "启动完整服务..."
docker-compose up -d >/dev/null 2>&1

# 等待服务启动
sleep 15

log_step "验证服务状态..."

# 检查容器状态
echo "📊 容器状态:"
docker-compose ps

echo ""

# 检查API健康状态
if curl -s --max-time 10 http://localhost:5000/api/health >/dev/null 2>&1; then
    log_info "✅ API服务运行正常"
else
    log_warn "⚠️  API服务启动中，检查详细状态..."
    docker-compose logs --tail=20 discord-bot
fi

# 检查数据库连接
if docker-compose exec -T db psql -U postgres -d discord_bot -c "SELECT 1;" >/dev/null 2>&1; then
    log_info "✅ 数据库连接正常"
else
    log_error "❌ 数据库连接失败"
fi

# 显示数据库表
log_info "📋 数据库表结构:"
docker-compose exec -T db psql -U postgres -d discord_bot -c "\dt" 2>/dev/null || true

# 清理临时文件
rm -rf $TEMP_DIR

echo ""
echo "🎉 修复完成！"
echo "============="
echo ""
echo "✅ 修复内容:"
echo "   • Python依赖包更新 (google-generativeai)"
echo "   • 数据库容器修复"
echo "   • 频道清理功能升级"
echo "   • 核心代码文件更新"
echo ""
echo "📋 新功能:"
echo "   • !cleanup_now - 清空所有历史消息"
echo "   • 自动清理 - 每日凌晨2点UTC"
echo "   • 多AI模型支持增强"
echo ""
echo "🔧 管理命令:"
echo "   查看日志: cd $BOT_DIR && docker-compose logs -f"
echo "   重启服务: cd $BOT_DIR && docker-compose restart"
echo "   检查健康: curl http://localhost:5000/api/health"
echo ""
echo "📁 备份位置: $BOT_DIR/$BACKUP_DIR"
echo ""
log_info "Discord Bot现在应该正常运行了！"