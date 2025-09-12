# VPS最终部署指南

## 问题确认

### 开发环境状态 ✅
```
2025-08-18 13:05:29,671 - config - INFO - TradingView Session ID已配置 (长度: 32)
2025-08-18 13:05:29,671 - config - INFO - TradingView Session Sign已配置 (长度: 47)
```

### VPS环境状态 ❌
```
Session ID 属性存在: False
Session ID 有值: False  
Session Sign 属性存在: False
Session Sign 有值: False
chart_service - ERROR - 'Config' object has no attribute 'tradingview_session_id'
```

## 根本原因
VPS Docker容器使用旧版config.py，缺少第37-38行的TradingView属性定义：
```python
self.tradingview_session_id = os.getenv('TRADINGVIEW_SESSION_ID')
self.tradingview_session_id_sign = os.getenv('TRADINGVIEW_SESSION_ID_SIGN')
```

## 解决方案

### 立即执行 (推荐)
```bash
sudo bash VPS_GIT_SYNC_FIX.sh
```

**脚本功能:**
1. ✅ Git pull最新代码
2. ✅ 停止旧容器
3. ✅ 强制重建Docker镜像
4. ✅ 修复数据库字段
5. ✅ 启动新容器
6. ✅ 验证Config属性

### 验证修复成功
修复后应该看到：
```
✅ Session ID 属性存在: True
✅ Session ID 有值: True (长度: 32)
✅ Session Sign 属性存在: True  
✅ Session Sign 有值: True (长度: 47)
✅ Chart服务初始化成功 - Config属性完整
```

### 立即测试
1. Discord发送: `@bot CT AAPL,15m`
2. 验证命令成功执行
3. 点击"获取chart"按钮
4. 确认无Config属性错误

## 环境变量确认
你的VPS环境变量设置正确：
- ✅ `TRADINGVIEW_SESSION_ID` (已设置)
- ✅ `TRADINGVIEW_SESSION_ID_SIGN` (已设置)

问题在于VPS运行的代码版本不包含这些属性的读取逻辑。

## 备用方案
如果Git同步失败，使用完整修复：
```bash
sudo bash VPS_ULTIMATE_FIX.sh
```