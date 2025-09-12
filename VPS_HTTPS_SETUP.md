# VPS完整部署指南 - 包含域名和HTTPS

## 🚀 一键完整部署

### 带域名和HTTPS (推荐)
```bash
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/COMPLETE_VPS_DEPLOY.sh
chmod +x COMPLETE_VPS_DEPLOY.sh
sudo bash COMPLETE_VPS_DEPLOY.sh your-domain.com
```

### 仅IP访问
```bash
sudo bash COMPLETE_VPS_DEPLOY.sh
```

## 📋 部署包含内容

- ✅ 系统更新和依赖安装
- ✅ Docker和Docker Compose安装  
- ✅ Nginx反向代理配置
- ✅ 防火墙配置 (UFW)
- ✅ SSL证书申请 (Let's Encrypt)
- ✅ 自动证书续期
- ✅ Discord Bot Docker部署
- ✅ PostgreSQL数据库设置
- ✅ 完整的服务监控

## 🌐 域名配置要求

1. **购买域名** (如: your-bot.com)
2. **DNS解析配置**:
   ```
   A记录: your-bot.com → 你的VPS IP地址
   ```
3. **等待DNS生效** (通常5-30分钟)
4. **验证解析**: `nslookup your-bot.com`

## 🔒 HTTPS配置过程

脚本会自动:
1. 安装Certbot和Nginx插件
2. 配置基础HTTP站点
3. 申请Let's Encrypt SSL证书  
4. 配置HTTPS重定向
5. 设置证书自动续期

## 📱 部署后访问

### 带域名的访问地址:
- 🏠 **主页**: https://your-domain.com
- ⚙️ **配置管理**: https://your-domain.com/config/
- 🏥 **健康检查**: https://your-domain.com/health
- 🔗 **TradingView Webhook**: https://your-domain.com/webhook/tradingview

### IP访问地址:
- 🏠 **主页**: http://your-server-ip
- ⚙️ **配置管理**: http://your-server-ip/config/
- 🏥 **健康检查**: http://your-server-ip/health
- 🔗 **TradingView Webhook**: http://your-server-ip/webhook/tradingview

## ⚙️ 配置Discord Token

```bash
cd /opt/discord-bot
nano .env
```

更新以下配置:
```env
DISCORD_TOKEN=你的实际Discord令牌
MONITOR_CHANNEL_IDS=频道ID1,频道ID2
REPORT_CHANNEL_ID=报告频道ID
WEBHOOK_URL=https://your-domain.com/webhook
```

重启服务:
```bash
docker-compose restart
```

## 🔧 高级配置

### SSL证书手动续期
```bash
certbot renew --dry-run  # 测试续期
certbot renew           # 手动续期
```

### Nginx配置调优
```bash
nano /etc/nginx/sites-available/discord-bot
nginx -t               # 测试配置
systemctl reload nginx # 重载配置
```

### 防火墙管理
```bash
ufw status            # 查看状态
ufw allow 22          # 允许SSH
ufw allow 80          # 允许HTTP
ufw allow 443         # 允许HTTPS
```

## 🛠️ 故障排除

### SSL证书问题
```bash
# 检查证书状态
certbot certificates

# 重新申请证书
certbot delete -d your-domain.com
certbot --nginx -d your-domain.com
```

### Nginx配置问题
```bash
# 检查配置语法
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

### Docker服务问题
```bash
cd /opt/discord-bot

# 查看所有容器状态
docker-compose ps

# 查看特定服务日志
docker-compose logs discord-bot
docker-compose logs config-server
docker-compose logs db
```

### 域名解析问题
```bash
# 检查域名解析
nslookup your-domain.com
dig your-domain.com

# 检查从外部访问
curl -I http://your-domain.com
curl -I https://your-domain.com
```

## 🔄 更新部署

```bash
cd /opt/discord-bot
git pull
docker-compose build --no-cache
docker-compose up -d
```

## 📞 技术支持

如遇问题请提供:
1. 域名配置信息
2. 错误日志: `docker-compose logs`
3. Nginx日志: `/var/log/nginx/error.log`
4. SSL证书状态: `certbot certificates`