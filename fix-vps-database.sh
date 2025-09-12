#!/bin/bash

# Discord Bot VPS 数据库修复脚本
# 解决数据库容器启动失败的问题
# 使用方法: wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/fix-vps-database.sh && chmod +x fix-vps-database.sh && sudo ./fix-vps-database.sh

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

echo "🔧 Discord Bot VPS 数据库修复工具"
echo "=================================="
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

log_step "诊断数据库问题..."

# 停止所有容器
log_info "停止所有容器..."
docker-compose down >/dev/null 2>&1 || true

# 检查并清理数据库卷
log_info "清理数据库卷..."
docker volume ls | grep discord-bot_postgres_data && {
    log_warn "发现旧的数据库卷，正在删除..."
    docker volume rm discord-bot_postgres_data 2>/dev/null || true
}

# 清理未使用的Docker资源
log_info "清理Docker资源..."
docker system prune -f >/dev/null 2>&1

# 检查数据库初始化文件
log_step "检查数据库配置..."

if [ ! -f "docker-db-init.sql" ]; then
    log_warn "数据库初始化文件不存在，正在创建..."
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

-- 为查询性能创建索引
CREATE INDEX IF NOT EXISTS idx_user_request_limits_user_id ON user_request_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_request_limits_date ON user_request_limits(request_date);
CREATE INDEX IF NOT EXISTS idx_user_request_limits_user_date ON user_request_limits(user_id, request_date);

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

-- TradingView webhook数据表
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

-- Personal webhook表
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

-- 为查询性能创建索引
CREATE INDEX IF NOT EXISTS idx_exempt_users_user_id ON exempt_users(user_id);
CREATE INDEX IF NOT EXISTS idx_tradingview_signals_symbol ON tradingview_signals(symbol);
CREATE INDEX IF NOT EXISTS idx_tradingview_signals_time ON tradingview_signals(signal_time);
CREATE INDEX IF NOT EXISTS idx_personal_webhooks_user_id ON personal_webhooks(user_id);
CREATE INDEX IF NOT EXISTS idx_personal_webhooks_secret ON personal_webhooks(webhook_secret);

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
    BEFORE UPDATE ON user_request_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_exempt_users_updated_at ON exempt_users;
CREATE TRIGGER update_exempt_users_updated_at
    BEFORE UPDATE ON exempt_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tradingview_signals_updated_at ON tradingview_signals;
CREATE TRIGGER update_tradingview_signals_updated_at
    BEFORE UPDATE ON tradingview_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_personal_webhooks_updated_at ON personal_webhooks;
CREATE TRIGGER update_personal_webhooks_updated_at
    BEFORE UPDATE ON personal_webhooks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 显示完成信息
SELECT 'Discord机器人数据库初始化完成' as status;
EOF
    log_info "数据库初始化文件已创建"
fi

# 确保docker-compose.yml配置正确
log_step "检查Docker Compose配置..."

if [ ! -f "docker-compose.yml" ]; then
    log_error "docker-compose.yml文件不存在"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    log_warn ".env文件不存在，请确保环境变量正确配置"
fi

# 重新拉取PostgreSQL镜像
log_step "更新PostgreSQL镜像..."
docker pull postgres:16

# 重新构建Discord Bot镜像
log_step "重建Discord Bot镜像..."
docker-compose build --no-cache discord-bot

# 单独启动数据库服务
log_step "启动数据库服务..."
docker-compose up -d db

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

# 验证数据库连接
log_step "验证数据库连接..."
if docker-compose exec -T db psql -U postgres -d discord_bot -c "SELECT 1;" >/dev/null 2>&1; then
    log_info "✅ 数据库连接验证成功"
else
    log_error "数据库连接失败"
    docker-compose logs db
    exit 1
fi

# 启动完整服务
log_step "启动完整服务..."
docker-compose up -d

# 等待服务启动
sleep 10

# 验证服务状态
log_step "验证服务状态..."
docker-compose ps

# 检查API健康状态
if curl -s --max-time 10 http://localhost:5000/api/health >/dev/null 2>&1; then
    log_info "✅ API服务运行正常"
else
    log_warn "⚠️  API服务启动中，请稍后检查"
fi

# 显示数据库信息
log_step "数据库信息:"
docker-compose exec -T db psql -U postgres -d discord_bot -c "\dt" 2>/dev/null || true

echo ""
echo "🎉 数据库修复完成！"
echo "====================="
echo ""
echo "📊 服务状态:"
echo "   数据库: PostgreSQL 16 (健康)"
echo "   API服务: http://localhost:5000"
echo ""
echo "🔧 管理命令:"
echo "   查看日志: cd $BOT_DIR && docker-compose logs -f"
echo "   重启服务: cd $BOT_DIR && docker-compose restart"
echo "   数据库连接: docker-compose exec db psql -U postgres -d discord_bot"
echo ""
log_info "数据库问题已解决，Discord Bot服务现在应该正常运行了！"