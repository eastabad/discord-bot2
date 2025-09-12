# Chart-img API 配置指南

## API概述

Chart-img API是一个付费服务，用于生成TradingView图表。根据官方文档，需要4个参数：

## 必需参数

### 1. x-api-key (必需)
```
CHART_IMG_API_KEY=your_api_key_here
```
- **获取方式**: 注册chart-img.com账户并购买API访问
- **用途**: API认证

### 2. LAYOUT_ID (必需)
```
LAYOUT_ID=2051
```
- **获取方式**: TradingView中创建或选择布局ID
- **用途**: 指定使用哪个图表布局

## 可选参数（用于私有布局）

### 3. tradingview-session-id (可选)
```
TRADINGVIEW_SESSION_ID=your_session_id
```
- **获取方式**: 浏览器cookies中的`sessionid`值
- **用途**: 访问私有布局或受邀指标

### 4. tradingview-session-id-sign (可选)
```
TRADINGVIEW_SESSION_ID_SIGN=your_session_sign
```
- **获取方式**: 浏览器cookies中的`sessionid_sign`值
- **用途**: 与session-id配对使用进行验证

## API请求格式

```bash
POST https://api.chart-img.com/v2/tradingview/layout-chart/{LAYOUT_ID}

Headers:
- x-api-key: {API_KEY}
- content-type: application/json
- tradingview-session-id: {SESSION_ID} (可选)
- tradingview-session-id-sign: {SESSION_SIGN} (可选)

Body:
{
  "symbol": "NASDAQ:TSLA",
  "interval": "15m",
  "width": 1920,
  "height": 1080
}
```

## 配置示例

### 仅公共访问（基础配置）
```env
CHART_IMG_API_KEY=your_api_key_here
LAYOUT_ID=2051
```

### 完整配置（包含私有访问）
```env
CHART_IMG_API_KEY=your_api_key_here
LAYOUT_ID=2051
TRADINGVIEW_SESSION_ID=your_sessionid_cookie
TRADINGVIEW_SESSION_ID_SIGN=your_sessionid_sign_cookie
```

## 获取TradingView Session信息

1. 登录TradingView网站
2. 打开浏览器开发者工具 (F12)
3. 查看Application/Storage → Cookies → tradingview.com
4. 复制`sessionid`和`sessionid_sign`的值

## 注意事项

- **API费用**: Chart-img是付费服务
- **Session有效期**: TradingView session会过期，需要定期更新
- **私有布局**: 只有提供有效session时才能访问私有布局
- **公共布局**: 无需session即可访问公共布局

## 故障排除

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 401 Unauthorized | API Key无效 | 检查CHART_IMG_API_KEY |
| 404 Not Found | Layout ID不存在 | 检查LAYOUT_ID |
| 403 Forbidden | Session过期或无效 | 更新TradingView session信息 |