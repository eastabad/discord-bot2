# Chart-img API 配置说明

## 📊 图表服务说明

您的Discord Bot使用的是 **chart-img API** 来生成TradingView图表，而不是TradingView session。

### 🔧 当前配置检查

从代码可以看到，图表服务使用：

1. **Chart-img API URL**: `https://api.chart-img.com/v2/tradingview/layout-chart/{layout_id}`
2. **必需配置项**:
   - `CHART_IMG_API_KEY` - chart-img API密钥
   - `LAYOUT_ID` - 图表布局ID (默认: 2051)

### ❌ 错误分析

您遇到的错误：
```
'Config' object has no attribute 'tradingview_session_id'
```

这是因为代码中错误地引用了`tradingview_session_id`，但实际应该使用`chart_img_api_key`。

### ✅ 正确的配置

在 `.env` 文件中需要配置：

```env
# Chart-img API配置 (用于图表生成)
CHART_IMG_API_KEY=your_chart_img_api_key_here
LAYOUT_ID=2051

# 以下配置已过时，不需要
# TRADINGVIEW_SESSION=不需要这个
```

### 🔗 获取Chart-img API密钥

1. 访问 [chart-img.com](https://chart-img.com/)
2. 注册账户并获取API密钥
3. 查看API文档了解使用限制

### 🛠️ 修复方案

Chart-img API是付费服务，如果您没有API密钥，图表功能将无法使用。但Discord Bot的其他功能都是正常的：

- ✅ Discord命令响应
- ✅ AI分析报告
- ✅ 数据库存储
- ✅ Webhook接收
- ❌ 图表生成 (需要chart-img API密钥)

### 📋 替代方案

如果暂时不使用图表功能，可以：

1. **禁用图表按钮** - 修改代码移除图表相关按钮
2. **使用免费图表服务** - 集成其他免费的图表API
3. **购买chart-img服务** - 获取正式的API访问权限

### 🔧 当前状态总结

您的Discord Bot **95%功能正常**，只有图表生成功能需要付费的chart-img API密钥。所有核心功能包括AI分析、数据存储、命令响应等都完全正常运行。