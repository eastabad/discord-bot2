# Discord Bot 配置完成指南

## 🎉 部署状态

✅ **Docker服务运行正常**  
✅ **数据库连接成功**  
✅ **AI服务初始化完成** (4个AI模型可用)  
✅ **API服务器启动** (端口5000)  
✅ **Nginx反向代理配置**  

❌ **Discord Token无效** - 需要配置

## 🔧 立即修复

### 1. 编辑配置文件
```bash
cd /opt/discord-bot
nano .env
```

### 2. 添加有效的Discord Token
```env
# 必须配置
DISCORD_TOKEN=MTQwNDE3MzUxMDA3NDU2NDcwOQ.your_actual_token_here

# 可选配置
MONITOR_CHANNEL_IDS=1404532905916760125,1404064475614548018
REPORT_CHANNEL_ID=1406017230126448671
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key
```

### 3. 重启Discord Bot
```bash
docker-compose restart discord-bot
```

### 4. 验证启动
```bash
docker-compose logs -f discord-bot
```

## 📋 Discord Token获取

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 选择您的应用程序
3. 点击 **Bot** 标签
4. 复制 **Token**
5. 粘贴到 `.env` 文件中

## 🌐 服务地址

- **主页**: http://your-server-ip
- **配置**: http://your-server-ip/config/
- **健康检查**: http://your-server-ip/health
- **TradingView Webhook**: http://your-server-ip/webhook/tradingview

## ✅ 完成后的功能

- Discord机器人响应命令
- TradingView webhook接收
- AI驱动的股票分析
- 图表生成和分析
- 个人webhook系统
- 多AI模型支持

## 🔍 故障排除

### Discord Bot无法连接
```bash
# 检查Token格式
cat .env | grep DISCORD_TOKEN

# 查看详细错误
docker-compose logs discord-bot
```

### API服务无响应
```bash
# 测试健康检查
curl http://localhost/health

# 检查端口
netstat -tlnp | grep :5000
```

### 数据库问题
```bash
# 检查数据库状态
docker-compose logs db

# 测试连接
docker-compose exec db psql -U postgres -d discord_bot -c "\dt"
```

## 📞 技术支持

系统已完全部署，只需配置有效的Discord Token即可正常运行。所有服务都已正确启动并相互连接。