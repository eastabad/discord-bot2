#!/bin/bash
# =================================================================
# TDbot Discord Bot 部署验证脚本
# 验证所有功能是否正常工作
# =================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[检查]${NC} $1"; }
pass() { echo -e "${GREEN}[通过]${NC} $1"; }
fail() { echo -e "${RED}[失败]${NC} $1"; }
warn() { echo -e "${YELLOW}[警告]${NC} $1"; }

DOMAIN="tvdata.tdindicator.top"
DEPLOY_DIR="/opt/discord-bot"
TOTAL_CHECKS=0
PASSED_CHECKS=0

check() {
    ((TOTAL_CHECKS++))
    if eval "$1"; then
        pass "$2"
        ((PASSED_CHECKS++))
        return 0
    else
        fail "$2"
        return 1
    fi
}

echo "========================================"
echo "TDbot Discord Bot 部署验证"
echo "========================================"

# 1. 系统服务检查
log "检查系统服务状态..."
check "systemctl is-active --quiet postgresql" "PostgreSQL数据库服务"
check "systemctl is-active --quiet nginx" "Nginx Web服务器"
check "systemctl is-active --quiet supervisor" "Supervisor进程管理器"

# 2. Discord Bot服务检查
log "检查Discord Bot服务..."
check "supervisorctl status discord-bot-main | grep -q 'RUNNING'" "Discord Bot主服务"
check "supervisorctl status discord-bot-config | grep -q 'RUNNING'" "配置Web服务"

# 3. 端口检查
log "检查端口监听状态..."
check "ss -tlnp | grep -q ':5000'" "Discord Bot API端口 (5000)"
check "ss -tlnp | grep -q ':8080'" "配置服务器端口 (8080)"
check "ss -tlnp | grep -q ':80'" "HTTP端口 (80)"
check "ss -tlnp | grep -q ':443'" "HTTPS端口 (443)"

# 4. 文件和目录检查
log "检查关键文件和目录..."
check "[ -f '$DEPLOY_DIR/.env' ]" "环境配置文件"
check "[ -d '$DEPLOY_DIR/config' ]" "配置目录"
check "[ -d '$DEPLOY_DIR/logs' ]" "日志目录"
check "[ -d '$DEPLOY_DIR/templates' ]" "模板目录"
check "[ -f '$DEPLOY_DIR/main_with_api.py' ]" "主程序文件"
check "[ -f '$DEPLOY_DIR/config_web_server.py' ]" "配置服务文件"

# 5. SSL证书检查
log "检查SSL证书..."
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    check "openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -noout -checkend 86400" "Let's Encrypt证书有效性"
elif [ -f "/etc/ssl/certs/nginx-selfsigned.crt" ]; then
    warn "使用自签名SSL证书"
    ((TOTAL_CHECKS++))
    ((PASSED_CHECKS++))
else
    fail "未找到SSL证书"
    ((TOTAL_CHECKS++))
fi

# 6. 数据库连接检查
log "检查数据库连接..."
check "sudo -u postgres psql -d discord_bot -c 'SELECT 1;' >/dev/null 2>&1" "PostgreSQL数据库连接"

# 7. Web界面HTTP检查
log "检查Web界面访问..."
check "curl -k -s https://localhost/health | grep -q 'status'" "主服务健康检查"
check "curl -s http://localhost:8080/ | grep -q 'html'" "配置服务Web界面"

# 8. API端点检查
log "检查API端点..."
check "curl -s http://localhost:5000/api/health | grep -q 'online'" "API健康检查端点"
check "curl -s http://localhost:5000/simple-config | grep -q '字段配置管理'" "简化配置界面"

# 9. 日志文件检查
log "检查日志文件..."
if [ -f "$DEPLOY_DIR/logs/discord-bot.log" ]; then
    if tail -n 50 "$DEPLOY_DIR/logs/discord-bot.log" | grep -q "已登录\|connected\|ready"; then
        pass "Discord Bot连接日志正常"
        ((PASSED_CHECKS++))
    else
        fail "Discord Bot未成功连接"
    fi
    ((TOTAL_CHECKS++))
else
    fail "未找到Discord Bot日志文件"
    ((TOTAL_CHECKS++))
fi

# 10. 配置验证
log "检查配置完整性..."
if [ -f "$DEPLOY_DIR/.env" ]; then
    if grep -q "DISCORD_TOKEN.*your_discord" "$DEPLOY_DIR/.env"; then
        warn "Discord Token未配置，请编辑.env文件"
    else
        pass "Discord Token已配置"
        ((PASSED_CHECKS++))
    fi
    ((TOTAL_CHECKS++))
fi

# 11. 防火墙检查
log "检查防火墙配置..."
if command -v ufw >/dev/null 2>&1; then
    check "ufw status | grep -q 'Status: active'" "防火墙已启用"
    check "ufw status | grep -q '443/tcp.*ALLOW'" "HTTPS端口已开放"
    check "ufw status | grep -q '80/tcp.*ALLOW'" "HTTP端口已开放"
fi

# 12. 维护脚本检查
log "检查维护工具..."
check "[ -f '$DEPLOY_DIR/maintenance.sh' ]" "维护脚本存在"
check "[ -x '$DEPLOY_DIR/maintenance.sh' ]" "维护脚本可执行"

# 显示总结
echo
echo "========================================"
echo "验证结果总结"
echo "========================================"
echo "总计检查项目: $TOTAL_CHECKS"
echo "通过检查项目: $PASSED_CHECKS"
echo "失败检查项目: $((TOTAL_CHECKS - PASSED_CHECKS))"

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo -e "${GREEN}✅ 所有检查项目通过！部署成功！${NC}"
    exit 0
elif [ $PASSED_CHECKS -gt $((TOTAL_CHECKS * 3 / 4)) ]; then
    echo -e "${YELLOW}⚠️ 大部分检查通过，但有几个问题需要解决${NC}"
    exit 1
else
    echo -e "${RED}❌ 多个关键检查失败，需要排查问题${NC}"
    exit 2
fi