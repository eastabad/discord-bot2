# VPS Docker更新说明 - 频道权限修复

## 📋 更新概述

本次更新修复了Discord Bot的频道权限判断逻辑问题，解决了CT命令在chart频道被错误拦截的bug。

## 🔧 修复内容

### 主要修复
- **修复频道判断逻辑**: `is_chart_channel`方法现在正确识别包含"chart"或"request"的频道名
- **移除过度限制**: 修复了频道隔离逻辑，允许在合适的频道使用对应命令
- **优化权限检查**: 改进了频道权限验证逻辑，避免误判

### 文件变更
- `bot.py`: 修复`is_chart_channel()`和频道隔离逻辑

## 🚀 部署命令

在VPS上运行以下命令更新Docker环境：

```bash
# 1. 进入项目目录
cd /path/to/your/discord-bot

# 2. 运行更新脚本
sudo bash CHANNEL_FIX_DEPLOY.sh
```

或者手动执行：

```bash
# 停止Discord Bot
docker-compose stop discord-bot

# 重新构建镜像
docker-compose build discord-bot

# 启动更新后的服务
docker-compose up -d discord-bot

# 查看日志确认正常运行
docker-compose logs -f discord-bot
```

## ✅ 验证测试

更新完成后，在Discord中测试：

1. **Chart频道测试**:
   ```
   @TDbot-tradingview CT TSLA,15m
   ```
   应该正常处理图表请求

2. **Report频道测试**:
   ```
   @TDbot-tradingview RP AAPL,1h
   ```
   应该正常处理报告请求

## 📊 预期结果

- ✅ CT命令在chart频道正常工作
- ✅ RP命令在report频道正常工作
- ✅ 频道隔离逻辑正确执行
- ✅ 用户不再收到错误的频道权限提示

## 🔍 故障排除

如果遇到问题：

1. **检查容器状态**:
   ```bash
   docker-compose ps
   ```

2. **查看详细日志**:
   ```bash
   docker-compose logs discord-bot
   ```

3. **重启所有服务**:
   ```bash
   docker-compose restart
   ```

## 📝 更新记录

- **日期**: 2025-08-18
- **版本**: Channel Permission Fix v1.0
- **状态**: 已在开发环境验证，准备部署到生产环境