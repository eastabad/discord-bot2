# 手动VPS部署指南 - Order Block功能完整包

## 部署包内容

### 核心应用文件
```
bot.py                     # Discord机器人主程序 (包含OB命令)
chart_service.py           # 图表服务 (包含OB图表生成)
webhook_service.py         # Webhook服务 (包含obData解析)
orderblock_webhook.py      # 专用OB webhook端点
api_server.py             # API服务器
main_with_api.py          # 主启动程序
config.py                 # 配置管理
models.py                 # 数据库模型
```

### 配置和管理文件
```
orderblock_config_manager.py  # OB配置管理器
manage_routes.py              # CLI路由管理工具
orderblock_routes.conf        # ticker路由配置文件
.env.example                  # 环境变量模板
docker-compose.yml            # Docker容器配置
Dockerfile                    # Docker镜像构建
```

### 支持服务文件
```
multi_ai_service.py           # 多AI模型服务
gemini_report_generator.py    # Gemini报告生成
rate_limiter.py              # 请求限制
channel_cleaner.py           # 频道清理
daily_logger.py              # 日志记录
prediction_service.py        # 预测服务
report_handler.py            # 报告处理
tradingview_handler.py       # TradingView处理
webhook_handler.py           # Webhook处理
parsing_engine.py            # 解析引擎
ai_template_engine.py        # AI模板引擎
```

## 手动部署步骤

### 1. 准备VPS环境
```bash
# 确保VPS已安装必要软件
sudo apt update
sudo apt install -y docker.io docker-compose git

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER
# 重新登录或运行: newgrp docker
```

### 2. 上传部署包
```bash
# 在VPS上创建项目目录
mkdir -p /opt/discord-bot
cd /opt/discord-bot

# 手动上传所有文件到此目录
# 或使用scp/rsync从本地上传
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加必要配置
nano .env
```

必需的环境变量：
```bash
# Discord配置
DISCORD_TOKEN=your_discord_bot_token

# 数据库配置
DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot

# AI模型配置
GEMINI_API_KEY=your_gemini_api_key
GEMINI_API_KEY_2=your_second_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key

# Order Block图表配置
OB_LAYOUT_ID=IoT1qwuk
CHART_IMG_API_KEY=your_chart_img_key
TRADINGVIEW_SESSION_ID=your_session_id
TRADINGVIEW_SESSION_ID_SIGN=your_session_sign
```

### 4. 配置Order Block路由
```bash
# 编辑ticker路由配置
nano orderblock_routes.conf

# 示例内容:
NVDA=1405694945809141781
COIN=1405694949533548684
TSLA=1404532905916760125
```

### 5. 部署和启动
```bash
# 给脚本执行权限
chmod +x *.sh *.py

# 构建和启动服务
docker-compose down  # 停止现有服务
docker-compose build --no-cache  # 重新构建镜像
docker-compose up -d  # 后台启动

# 检查服务状态
docker-compose ps
docker-compose logs -f discord-bot
```

### 6. 验证部署

#### A. 检查API健康状态
```bash
curl http://localhost:5000/api/health
# 预期响应: {"status": "healthy", "timestamp": "..."}
```

#### B. 测试OB Discord命令
在Discord频道中发送:
```
@TD AIassistant OB NVDA,15m
```

#### C. 测试obData解析
```bash
curl -X POST http://localhost:5000/webhook/tradingview/1145170623354638418/BaO368cMdm1F6lb0 \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "action": "buy",
    "sentiment": "bullish",
    "data": {
      "obData": "Timeframe: 15; Bullish OB: 344.86 - 344.04",
      "lastSupplyText": "349.54 - 347.17 | 1H",
      "lastDemandText": "337.47 - 335.02 | 1H"
    },
    "extras": {
      "referencePrice": 348.28
    }
  }'
```

#### D. 测试Order Block专用webhook
```bash
curl -X POST http://localhost:5000/webhook/orderblock \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "timeframe": "15m",
    "event": "New Bullish OB Formed",
    "price": "440.25",
    "bullish_ob": "438.00-442.00",
    "bearish_ob": "N/A"
  }'
```

## 管理命令

### 查看和修改路由配置
```bash
# 查看当前路由
python3 manage_routes.py list

# 添加新路由
python3 manage_routes.py add AAPL 1234567890123456789

# 删除路由
python3 manage_routes.py remove TSLA

# 验证配置
python3 manage_routes.py validate
```

### 监控和维护
```bash
# 查看实时日志
docker-compose logs -f discord-bot

# 查看系统资源使用
docker stats

# 重启服务
docker-compose restart discord-bot

# 更新应用(上传新文件后)
docker-compose down
docker-compose build --no-cache discord-bot
docker-compose up -d
```

## 故障排查

### 1. 容器启动失败
```bash
# 查看详细错误
docker-compose logs discord-bot

# 检查端口占用
netstat -tulpn | grep -E "(5000|8080)"

# 检查配置文件
cat .env | grep -E "(DISCORD|GEMINI|DATABASE)"
```

### 2. OB功能不工作
```bash
# 检查配置文件
cat orderblock_routes.conf

# 测试配置管理器
python3 -c "
from orderblock_config_manager import OrderBlockConfigManager
manager = OrderBlockConfigManager()
print('Routes:', manager.get_routes())
"

# 检查图表服务
docker-compose exec discord-bot python3 -c "
from chart_service import ChartService
from config import Config
config = Config()
chart = ChartService(config)
print('OB Layout ID:', getattr(config, 'ob_layout_id', 'Not configured'))
"
```

### 3. 图表生成失败
```bash
# 检查网络连接
docker-compose exec discord-bot curl -I https://api.chart-img.com

# 检查TradingView会话
grep -E "(SESSION_ID|SESSION_SIGN)" .env
```

## 成功标准检查清单

部署成功的验证清单:
- [ ] 所有Docker容器状态为"Up"
- [ ] API健康检查返回正常
- [ ] Discord机器人在线状态
- [ ] OB命令 `@bot OB NVDA,15m` 返回图表
- [ ] 个人webhook接收obData正常显示
- [ ] Order Block专用webhook发送成功
- [ ] Discord消息显示英文界面
- [ ] 系统日志无错误信息

## 备份和回滚

### 创建备份
```bash
# 备份当前配置
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
cp orderblock_routes.conf orderblock_routes.conf.backup.$(date +%Y%m%d_%H%M%S)

# 备份数据库 (如需要)
docker-compose exec db pg_dump -U postgres discord_bot > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 紧急回滚
```bash
# 停止服务
docker-compose down

# 恢复备份配置
cp .env.backup.YYYYMMDD_HHMMSS .env
cp orderblock_routes.conf.backup.YYYYMMDD_HHMMSS orderblock_routes.conf

# 重新启动
docker-compose up -d
```

---
*手动部署指南更新时间: 2025-08-27*
*适用于: Order Block完整功能包*