# Discord Bot 简洁部署

## 一键部署

```bash
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/DEPLOY.sh
chmod +x DEPLOY.sh
sudo bash DEPLOY.sh
```

## 配置

1. 编辑环境变量:
```bash
cd /opt/discord-bot
nano .env
```

2. 添加您的API密钥:
```env
DISCORD_TOKEN=你的Discord令牌
MONITOR_CHANNEL_IDS=频道ID1,频道ID2
ANTHROPIC_API_KEY=你的Anthropic密钥
GEMINI_API_KEY=你的Gemini密钥
```

3. 重启服务:
```bash
docker-compose restart
```

## 服务地址

- 主页: http://your-server-ip
- 配置: http://your-server-ip/config/
- API: http://your-server-ip/health
- Webhook: http://your-server-ip/webhook/tradingview

## 管理

```bash
cd /opt/discord-bot

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down
```

## 系统要求

- Ubuntu 18.04+
- 2GB RAM
- 10GB 存储空间
- Root权限