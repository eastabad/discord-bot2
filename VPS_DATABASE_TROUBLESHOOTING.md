# VPS Discord Bot 数据库问题解决方案

## 🔧 快速修复命令

### 数据库容器启动失败
```bash
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/fix-vps-database.sh && chmod +x fix-vps-database.sh && sudo ./fix-vps-database.sh
```

### 包含数据库修复的完整更新
```bash
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/channel-cleanup-update.sh && chmod +x channel-cleanup-update.sh && sudo ./channel-cleanup-update.sh
```

## 🚨 常见数据库问题

### 1. Container discord-bot-db is unhealthy
**症状**: 数据库容器无法启动，显示unhealthy状态

**原因**:
- Docker卷权限问题
- PostgreSQL镜像版本冲突
- 数据库初始化文件问题
- 端口占用或网络冲突

**解决方案**:
```bash
cd /opt/discord-bot
docker-compose down
docker volume rm discord-bot_postgres_data
docker pull postgres:16
docker-compose up -d db
```

### 2. 数据库连接被拒绝
**症状**: `connection refused` 或 `could not connect to server`

**检查步骤**:
```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看数据库日志
docker-compose logs db

# 3. 测试数据库连接
docker-compose exec db pg_isready -U postgres
```

### 3. 数据库表结构问题
**症状**: 表不存在或字段缺失错误

**修复命令**:
```bash
# 重新初始化数据库
docker-compose exec db psql -U postgres -d discord_bot -f /docker-entrypoint-initdb.d/init.sql
```

## 🔍 详细诊断流程

### 步骤1: 检查服务状态
```bash
cd /opt/discord-bot
docker-compose ps
```

### 步骤2: 查看详细日志
```bash
# 数据库日志
docker-compose logs db

# Discord Bot日志  
docker-compose logs discord-bot
```

### 步骤3: 验证数据库连接
```bash
# 进入数据库容器
docker-compose exec db psql -U postgres -d discord_bot

# 检查表结构
\dt

# 检查表数据
SELECT * FROM user_request_limits LIMIT 5;
```

### 步骤4: 网络连接测试
```bash
# 测试内部网络
docker-compose exec discord-bot ping db

# 测试数据库端口
docker-compose exec discord-bot nc -zv db 5432
```

## 🛠️ 手动修复步骤

### 完全重置数据库
```bash
cd /opt/discord-bot

# 1. 停止所有服务
docker-compose down

# 2. 删除数据库卷
docker volume rm discord-bot_postgres_data

# 3. 清理Docker缓存
docker system prune -f

# 4. 重新拉取镜像
docker pull postgres:16

# 5. 重建并启动
docker-compose build --no-cache
docker-compose up -d
```

### 只重启数据库服务
```bash
cd /opt/discord-bot

# 1. 重启数据库容器
docker-compose restart db

# 2. 等待启动完成
sleep 10

# 3. 验证健康状态
docker-compose exec db pg_isready -U postgres
```

## 📋 数据库表结构

### 核心表
- `user_request_limits` - 用户请求限制
- `exempt_users` - 豁免用户列表
- `tradingview_signals` - TradingView信号数据
- `personal_webhooks` - 个人Webhook配置

### 检查表存在性
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

## 🔐 环境变量检查

### 数据库相关环境变量
```bash
# 检查.env文件
cat /opt/discord-bot/.env | grep -E "(DATABASE|POSTGRES)"

# 应包含:
# DATABASE_URL=postgresql://postgres:discord123@db:5432/discord_bot
```

### Docker Compose环境配置
```yaml
environment:
  - POSTGRES_DB=discord_bot
  - POSTGRES_USER=postgres  
  - POSTGRES_PASSWORD=discord123
```

## 🚀 性能优化

### 数据库性能监控
```sql
-- 检查活跃连接
SELECT count(*) FROM pg_stat_activity;

-- 检查表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 索引优化
```sql
-- 检查索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## 📞 紧急恢复

如果所有方法都失败，使用紧急恢复：

```bash
# 1. 完全停止和清理
cd /opt/discord-bot
docker-compose down -v
docker system prune -af

# 2. 重新下载最新代码
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/fix-vps-database.sh
chmod +x fix-vps-database.sh
sudo ./fix-vps-database.sh

# 3. 如果仍然失败，联系技术支持
docker-compose logs > /tmp/discord-bot-logs.txt
```

---

**记住**: 数据库问题通常是Docker卷权限或网络配置引起的。上述脚本会自动处理大部分常见问题。