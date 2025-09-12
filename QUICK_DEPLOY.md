# 快速部署指南 - Order Block完整功能

## 📦 部署包内容
- **57个Python文件** (包含所有Order Block功能)
- **Docker配置** (docker-compose.yml, Dockerfile)
- **配置模板** (.env.example, orderblock_routes.conf)
- **管理工具** (manage_routes.py, 部署脚本)

## 🚀 快速部署步骤

### 1. 上传到VPS
```bash
# 解压部署包到VPS
scp discord-bot-ob-complete-*.tar.gz root@your-vps:/opt/
ssh root@your-vps
cd /opt
tar -xzf discord-bot-ob-complete-*.tar.gz
mv deployment_package discord-bot
cd discord-bot
```

### 2. 配置环境
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置(必填项)
nano .env
```

**必需配置:**
```
DISCORD_TOKEN=your_bot_token
GEMINI_API_KEY=your_gemini_key
GEMINI_API_KEY_2=your_second_gemini_key
OB_LAYOUT_ID=IoT1qwuk
```

### 3. 配置路由
```bash
# 编辑Order Block路由
nano orderblock_routes.conf

# 示例内容:
NVDA=1405694945809141781
COIN=1405694949533548684
```

### 4. 部署启动
```bash
# 安装Docker(如未安装)
curl -fsSL https://get.docker.com | sh

# 启动服务
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 检查状态
docker-compose ps
```

## ✅ 验证部署

### API健康检查
```bash
curl http://localhost:5000/api/health
```

### Discord OB命令测试
```
@TD AIassistant OB NVDA,15m
```

### webhook测试
```bash
curl -X POST http://localhost:5000/webhook/orderblock \
  -H "Content-Type: application/json" \
  -d '{"ticker":"NVDA","timeframe":"15m","event":"New Bullish OB Formed","price":"440.25","bullish_ob":"438.00-442.00"}'
```

## 🎯 新功能特色

✅ **OB Discord命令** - `@bot OB NVDA,15m` (每日3次)
✅ **obData自动解析** - TradingView webhook中Order Block信息
✅ **交互按钮** - Discord私信中专用Order Block按钮
✅ **供需区字段** - Nearest Supply/Demand自动显示
✅ **专用图表** - 使用IoT1qwuk布局的专业OB图表
✅ **英文界面** - 所有字段英文显示
✅ **自动路由** - ticker智能分发到指定频道

## 🔧 管理命令

```bash
# 查看路由配置
python3 manage_routes.py list

# 添加新路由
python3 manage_routes.py add AAPL 1234567890

# 查看实时日志
docker-compose logs -f discord-bot
```

## 📞 支持联系

如遇问题请检查:
1. `docker-compose logs discord-bot` 查看错误
2. 确认.env所有必需变量已配置
3. 验证orderblock_routes.conf格式正确

---
*部署包版本: Order Block Complete v2025.08.27*