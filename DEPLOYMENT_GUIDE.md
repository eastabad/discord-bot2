# VPS部署指南 - 最新修复版本

## 更新内容概述
本次更新包含以下重要修复和增强:

### 1. Gemini 2.5 Pro 优化
- 修复了角色配置过滤问题
- 简化系统指令调用避免内容过滤
- 增强配额管理和错误处理

### 2. TradersPost命令修复  
- 支持 `!traderpost` 和 `!traderspost` 两种拼写
- 修复DMChannel属性错误
- 移除管理员权限限制，所有用户可用
- 增强错误提示和日志记录

### 3. AI模型故障转移
- 智能多AI模型备份系统
- Gemini配额耗尽时自动切换到Claude/GPT
- 透明的错误处理和用户反馈

## 部署步骤

### 方法1: 使用更新脚本 (推荐)
```bash
# 在VPS上执行
cd /opt/discord-bot
wget [脚本URL]/VPS_DOCKER_UPDATE.sh
chmod +x VPS_DOCKER_UPDATE.sh
sudo ./VPS_DOCKER_UPDATE.sh
```

### 方法2: 手动部署
```bash
# 1. 停止现有容器
cd /opt/discord-bot
docker-compose down

# 2. 手动更新关键文件
# 上传以下文件到对应位置:
#   - bot.py
#   - multi_ai_service.py  
#   - config/simple_ai_templates.json
#   - models.py
#   - webhook_service.py

# 3. 重建镜像
docker-compose build --no-cache discord-bot

# 4. 启动服务  
docker-compose up -d

# 5. 检查状态
docker-compose logs -f discord-bot
```

## 验证部署

### 1. 基础健康检查
```bash
# API服务检查
curl http://localhost:5000/api/health

# AI模型状态检查  
curl http://localhost:5000/api/ai-status
```

### 2. Discord Bot功能测试
- 发送私信测试: `!traderpost info`
- 图表命令测试: `CT TSLA`  
- 报告命令测试: `RP TSLA`

### 3. 监控日志
```bash
# 实时查看日志
docker-compose logs -f discord-bot

# 查看容器状态
docker-compose ps
```

## 核心文件清单
确保以下文件已更新到最新版本:
- ✅ `bot.py` (TradersPost命令修复)
- ✅ `multi_ai_service.py` (Gemini 2.5 Pro优化)
- ✅ `config/simple_ai_templates.json` (AI模板配置)
- ✅ `models.py` (数据库模型)
- ✅ `webhook_service.py` (Webhook处理)

## 故障排除

### TradersPost命令无响应
```bash
# 检查bot.py中的has_admin_command函数
grep -n "traderspost\|traderpost" bot.py

# 检查数据库连接
docker-compose exec discord-bot python -c "from models import get_db_session; print('DB OK')"
```

### Gemini API配额问题
```bash
# 检查AI服务日志
docker-compose logs discord-bot | grep -i gemini

# 查看故障转移日志
docker-compose logs discord-bot | grep -i "fallback\|quota"
```

### 部署后验证清单
- [ ] Discord Bot在线
- [ ] API端点响应正常
- [ ] 4个AI模型可用
- [ ] TradersPost命令正常工作
- [ ] 图表生成功能正常
- [ ] Webhook接收正常

## 联系支持
如果遇到部署问题，请提供:
1. `docker-compose ps` 输出
2. `docker-compose logs discord-bot` 最后50行
3. 具体错误现象描述
