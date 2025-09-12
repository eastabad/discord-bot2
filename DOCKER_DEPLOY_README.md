# Discord Bot Docker部署包

## 🚀 一键部署

### 方法1: 直接下载脚本
```bash
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/FINAL_DOCKER_DEPLOY.sh
chmod +x FINAL_DOCKER_DEPLOY.sh
sudo bash FINAL_DOCKER_DEPLOY.sh
```

### 方法2: 克隆仓库
```bash
git clone https://github.com/eastabad/DiscordBot.git
cd DiscordBot
sudo bash FINAL_DOCKER_DEPLOY.sh
```

## 📋 系统要求

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- 2GB+ RAM
- 10GB+ 磁盘空间
- Root权限

## ⚙️ 部署后配置

1. **编辑环境变量**
```bash
cd /opt/discord-bot
nano .env
```

2. **添加必要的API密钥**
```env
DISCORD_TOKEN=你的Discord机器人令牌
MONITOR_CHANNEL_IDS=频道ID1,频道ID2
REPORT_CHANNEL_ID=报告频道ID
ANTHROPIC_API_KEY=你的Anthropic密钥
GEMINI_API_KEY=你的Gemini密钥
```

3. **重启服务**
```bash
docker-compose restart
```

## 🔧 管理命令

```bash
# 进入项目目录
cd /opt/discord-bot

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码
git pull && docker-compose build --no-cache && docker-compose up -d
```

## 🌐 服务地址

- 主服务: http://your-server-ip
- 配置管理: http://your-server-ip/config/
- API健康检查: http://your-server-ip/health
- TradingView Webhook: http://your-server-ip/webhook/tradingview

## 🔒 SSL配置 (可选)

```bash
# 安装Certbot
apt install certbot python3-certbot-nginx

# 申请SSL证书
certbot --nginx -d your-domain.com
```

## 📊 功能特性

- Discord机器人自动响应
- TradingView Webhook集成
- AI驱动的股票分析
- 多AI模型支持 (Anthropic, Gemini, OpenAI)
- 个人Webhook系统
- 自动数据存储和报告
- Web配置界面
- 反向代理和负载均衡

## 🛠️ 故障排除

### 服务无法启动
```bash
# 检查日志
docker-compose logs discord-bot
docker-compose logs config-server

# 重新构建
docker-compose build --no-cache
```

### Nginx错误
```bash
# 检查配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

### 数据库连接问题
```bash
# 检查数据库状态
docker-compose logs db

# 重启数据库
docker-compose restart db
```

## 📞 技术支持

如遇问题，请提供：
1. 错误日志 (`docker-compose logs`)
2. 系统信息 (`uname -a`)
3. Docker版本 (`docker --version`)
4. 服务状态 (`docker-compose ps`)