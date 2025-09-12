# VPS最终部署指南

## 当前问题状态

### 问题1: Config对象属性缺失
```
'Config' object has no attribute 'tradingview_session_id'
```
**原因**: VPS运行旧版代码，Config类未更新

### 问题2: 数据库字段缺失
```
column exempt_users.reason does not exist
```
**原因**: VPS数据库模式未同步

### 问题3: 代码版本不一致
- 开发环境: 最新修复版本
- VPS环境: 旧版本，未应用修复

## 解决方案

### 选项1: 紧急修复 (推荐)
```bash
sudo bash VPS_EMERGENCY_FIX.sh
```
**特点**:
- 强制重建Docker容器
- 确保使用最新代码
- 修复数据库字段
- 一步解决所有问题

### 选项2: 完整更新
```bash
sudo bash COMPLETE_VPS_UPDATE.sh
```
**特点**:
- 包含所有修复
- 更新部署
- 验证配置

### 选项3: 分步修复
```bash
# 1. 数据库修复
sudo bash VPS_DATABASE_FIX.sh

# 2. 代码更新
sudo bash CHANNEL_FIX_DEPLOY.sh

# 3. 配置验证
sudo bash CHART_API_COMPLETE_FIX.sh
```

## 修复后验证

### 1. 检查服务状态
```bash
docker-compose ps
docker-compose logs discord-bot
```

### 2. 测试功能
- Discord命令: `@bot CT AAPL,15m`
- 交互按钮: 点击"获取chart"
- 检查日志无错误

### 3. 验证配置
```bash
docker-compose exec discord-bot python3 -c "
from config import Config
config = Config()
print(f'Session ID: {hasattr(config, \"tradingview_session_id\")}')
"
```

## 根本原因分析

1. **代码同步问题**: VPS使用的Docker镜像未包含最新修复
2. **数据库迁移**: 开发环境和VPS环境数据库结构不一致
3. **配置更新**: Config类的属性更新未部署到VPS

## 预防措施

1. 使用`--no-cache`重建Docker镜像
2. 在部署脚本中包含数据库迁移
3. 验证配置对象属性完整性
4. 测试所有功能点后确认部署成功