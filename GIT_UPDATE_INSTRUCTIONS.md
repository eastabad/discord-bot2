# Git更新说明 - 修复VPS Chart功能

## 问题确认
✅ **开发环境**: config.py包含正确的TradingView属性（第37-38行）
❌ **VPS环境**: 使用旧版config.py，缺少TradingView属性
❌ **Git仓库**: 可能还是旧版本，需要手动提交更新

## 关键代码差异

**开发环境config.py (正确版本) - 第37-38行:**
```python
self.tradingview_session_id = os.getenv('TRADINGVIEW_SESSION_ID')
self.tradingview_session_id_sign = os.getenv('TRADINGVIEW_SESSION_ID_SIGN')
```

**VPS错误信息:**
```
'Config' object has no attribute 'tradingview_session_id'
```

## 解决步骤

### 1. 检查Git状态
```bash
git status
git diff config.py
```

### 2. 手动提交更新 (如果config.py有更改)
```bash
git add config.py
git commit -m "Fix: Add TradingView session attributes to Config class for Chart-img API support"
git push
```

### 3. VPS强制更新
在VPS上运行：
```bash
sudo bash VPS_GIT_SYNC_FIX.sh
```

或者手动执行：
```bash
cd /opt/discord-bot
git fetch --all
git reset --hard origin/main
docker-compose down
docker-compose build --no-cache discord-bot
docker-compose up -d discord-bot
```

### 4. 验证修复
VPS修复后应该看到：
```
2025-08-18 xx:xx:xx - config - INFO - TradingView Session ID已配置 (长度: 32)
2025-08-18 xx:xx:xx - config - INFO - TradingView Session Sign已配置 (长度: 47)
```

### 5. 测试Chart功能
Discord发送：`@bot CT AAPL,15m`
应该不再有Config属性错误

## 文件比较

**需要确保Git仓库包含以下关键行:**

`config.py` 第35-45行应该是：
```python
# TradingView配置 (Chart-img API会话信息，可选)
self.tv_session = os.getenv('TRADINGVIEW_SESSION')  # 兼容性保留
self.tradingview_session_id = os.getenv('TRADINGVIEW_SESSION_ID')        # <-- 第37行 关键
self.tradingview_session_id_sign = os.getenv('TRADINGVIEW_SESSION_ID_SIGN')  # <-- 第38行 关键

# 调试信息
if self.tradingview_session_id:
    self.logger.info(f'TradingView Session ID已配置 (长度: {len(self.tradingview_session_id)})')
if self.tradingview_session_id_sign:
    self.logger.info(f'TradingView Session Sign已配置 (长度: {len(self.tradingview_session_id_sign)})')
```

## 确认清单
- [ ] Git仓库包含更新的config.py
- [ ] VPS拉取最新代码
- [ ] Docker重建容器
- [ ] 验证Config属性存在
- [ ] Chart功能正常工作