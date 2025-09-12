# VPS部署检查清单 - Order Block Chart Integration

## 部署前检查

### 1. VPS环境准备
- [ ] VPS可正常访问
- [ ] Docker和Docker Compose已安装
- [ ] Git已配置
- [ ] 足够的磁盘空间(至少5GB)
- [ ] 网络连接稳定

### 2. 代码同步
- [ ] 最新代码已推送到Git仓库
- [ ] VPS上代码已更新 (`git pull`)
- [ ] 确认关键文件存在:
  - [ ] `bot.py` (包含OB命令处理)
  - [ ] `chart_service.py` (包含get_ob_chart方法)
  - [ ] `webhook_service.py` (包含obData解析)
  - [ ] `orderblock_webhook.py` (专用OB webhook)
  - [ ] `orderblock_config_manager.py`
  - [ ] `manage_routes.py`
  - [ ] `orderblock_routes.conf`

### 3. 环境变量配置
在VPS的 `.env` 文件中确保包含:
```bash
# 必需变量
DISCORD_TOKEN=your_discord_token
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot

# Order Block Chart服务
OB_LAYOUT_ID=IoT1qwuk
CHART_IMG_API_KEY=your_chart_img_api_key (可选)
TRADINGVIEW_SESSION_ID=your_session_id (可选)
TRADINGVIEW_SESSION_ID_SIGN=your_session_sign (可选)
```

### 4. Order Block路由配置
检查 `orderblock_routes.conf` 文件:
```bash
# 示例配置
NVDA=1405694945809141781
COIN=1405694949533548684
```

## 部署执行

### 方法1: 使用自动部署脚本
```bash
# 在VPS项目目录中执行
./deploy_ob_chart_integration.sh
```

### 方法2: 手动部署步骤
```bash
# 1. 备份当前配置
cp .env .env.backup
cp orderblock_routes.conf orderblock_routes.conf.backup

# 2. 停止服务
docker-compose down

# 3. 更新代码
git pull origin main

# 4. 重新构建
docker-compose build --no-cache discord-bot

# 5. 启动服务
docker-compose up -d

# 6. 检查状态
docker-compose ps
docker-compose logs -f discord-bot
```

## 部署后验证

### 1. 服务状态检查
```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs --tail=50 discord-bot | grep -E "(ERROR|INFO|SUCCESS)"

# 检查API健康状态
curl http://localhost:5000/api/health
```

### 2. Order Block功能测试

#### A. OB Discord命令测试
在Discord中发送消息测试：
```
@TD AIassistant OB NVDA,15m
```

#### B. obData解析测试
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
    }
  }'
```

#### C. OB Webhook测试
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

**预期响应**: {"status": "success", "message": "Order Block信号处理成功"}

### 3. Discord验证
- [ ] **OB命令**: 私信收到OB图表，频道显示成功提示
- [ ] **obData解析**: 私信显示"Order Block Info"字段
- [ ] **交互按钮**: 私信包含"Order Block"按钮
- [ ] **供需区显示**: 显示Nearest Supply/Demand字段
- [ ] **OB Webhook**: 配置频道收到Order Block消息
- [ ] **图表附件**: 验证消息包含专业OB图表
- [ ] **英文界面**: 确认所有字段显示为英文
- [ ] **Footer**: 验证显示"TD AIassistant Order Block MoneyFlow system"

### 4. 系统监控
```bash
# 监控系统资源
docker stats

# 监控日志流
docker-compose logs -f discord-bot

# 检查特定关键词
docker-compose logs discord-bot | grep -E "(图表|chart_service|orderblock)"
```

## 常见问题排查

### 问题1: 图表生成失败
**症状**: 收到Order Block消息但没有图表
**排查**:
```bash
# 检查Chart-img API配置
grep -E "(CHART_IMG|OB_LAYOUT)" .env

# 查看图表服务日志
docker-compose logs discord-bot | grep chart_service
```

### 问题2: 路由配置不生效
**症状**: 信号发送到默认频道而非配置频道
**排查**:
```bash
# 检查配置文件
cat orderblock_routes.conf

# 验证配置格式
python3 -c "
from orderblock_config_manager import OrderBlockConfigManager
manager = OrderBlockConfigManager()
print(manager.get_routes())
"
```

### 问题3: 服务启动失败
**症状**: Docker容器无法启动
**排查**:
```bash
# 查看详细错误
docker-compose logs discord-bot

# 检查端口占用
netstat -tulpn | grep -E "(5000|8080)"

# 检查依赖安装
docker-compose exec discord-bot pip list | grep -E "(discord|chart|gemini)"
```

## 回滚计划

如果出现严重问题，执行回滚:
```bash
# 1. 停止服务
docker-compose down

# 2. 回滚代码到稳定版本
git log --oneline -10  # 查看最近提交
git checkout [stable_commit_hash]

# 3. 恢复配置
cp .env.backup .env
cp orderblock_routes.conf.backup orderblock_routes.conf

# 4. 重新启动
docker-compose up -d
```

## 成功标准

部署成功的标志:
- [ ] 所有Docker容器正常运行
- [ ] API健康检查返回正常
- [ ] **OB Discord命令**: `@bot OB NVDA,15m`正常工作
- [ ] **obData解析**: webhook中obData字段正确显示
- [ ] **交互按钮**: Order Block按钮生成专用图表
- [ ] **供需区字段**: Nearest Supply/Demand正确显示
- [ ] **OB Webhook**: 专用端点响应成功并发送图表
- [ ] **英文界面**: 所有字段显示为英文
- [ ] **图表生成**: OB专用布局(IoT1qwuk)正常工作
- [ ] 系统日志无错误信息
- [ ] 连续运行24小时稳定

---
*检查清单更新时间: 2025-08-27*
*适用版本: Order Block Chart Integration*