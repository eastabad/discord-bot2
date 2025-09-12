# Order Block 专用 Webhook 使用指南

## 概述

系统现在支持专门的Order Block信号webhook，可以接收TradingView发送的Order Block事件并自动路由到对应的Discord频道。

## Webhook地址

```
POST http://localhost:5000/webhook/orderblock
```

**生产环境地址:**
```
POST https://your-domain.com/webhook/orderblock
```

## 支持的JSON格式

根据你提供的TradingView脚本，系统接收以下JSON格式：

```json
{
  "ticker": "NASDAQ:TSLA",
  "timeframe": "15m", 
  "event": "New Bullish OB Formed",
  "price": "344.86",
  "bullish_ob": "344.86 - 344.04",
  "bearish_ob": "N/A"
}
```

## 支持的事件类型

1. **New Bullish OB Formed** - 新看涨Order Block形成
2. **New Bearish OB Formed** - 新看跌Order Block形成  
3. **Price Entering Bullish OB** - 价格进入看涨Order Block
4. **Price Entering Bearish OB** - 价格进入看跌Order Block

## Ticker到频道路由

系统使用ticker到频道的映射表来决定信号发送到哪个Discord频道：

### 当前默认映射
- `NASDAQ:TSLA` → 频道 1404532905916760125
- `NASDAQ:NVDA` → 频道 1404532905916760125  
- `NASDAQ:AAPL` → 频道 1404532905916760125
- `NASDAQ:MSFT` → 频道 1404532905916760125
- `NASDAQ:GOOGL` → 频道 1404532905916760125
- `NYSE:SPY` → 频道 1404532905916760125
- `NASDAQ:QQQ` → 频道 1404532905916760125

### 管理路由映射

使用管理工具添加新的ticker映射：

```bash
python manage_ticker_routes.py
```

## Discord消息格式

Order Block信号在Discord中显示为彩色embed消息，包含：

- **标题**: 🟢/🔴 TICKER Order Block Alert
- **事件类型**: 具体的Order Block事件
- **当前价格**: $价格
- **看涨Order Block**: 如果存在
- **看跌Order Block**: 如果存在  
- **时间框架**: 15m, 1h, 4h等
- **发生时间**: 美国东部时间

### 颜色编码
- 🟢 **绿色**: New Bullish OB Formed
- 🔴 **红色**: New Bearish OB Formed
- 📈 **深绿**: Price Entering Bullish OB
- 📉 **深红**: Price Entering Bearish OB

## TradingView脚本集成

在你的TradingView脚本中使用以下webhook URL：

```javascript
// 在TradingView Pine脚本中设置webhook
// Webhook URL: https://your-domain.com/webhook/orderblock

// JSON消息格式
string json_message = '{' +
 '\"ticker\": \"' + syminfo.tickerid + '\",' +
 '\"timeframe\": \"' + timeframe.period + '\",' +
 '\"event\": \"' + event_type + '\",' +
 '\"price\": \"' + str.tostring(close, '#.##') + '\",' +
 '\"bullish_ob\": \"' + bull_ob_range + '\",' +
 '\"bearish_ob\": \"' + bear_ob_range + '\"' +
 '}'
```

## 测试

运行测试脚本验证功能：

```bash
python test_orderblock_webhook.py
```

## 数据库

系统自动创建`ticker_channel_mappings`表来存储路由映射：

- `ticker`: 股票代码 (例如: NASDAQ:TSLA)
- `channel_id`: Discord频道ID
- `description`: 映射描述
- `is_active`: 是否激活
- `created_at`: 创建时间

## 故障排除

1. **检查webhook地址是否正确**
2. **验证JSON格式是否符合要求**
3. **确认ticker在路由表中存在**
4. **检查Discord频道ID是否有效**
5. **查看系统日志获取错误详情**

## 日志监控

系统日志会显示：
- 收到的Order Block信号
- 路由到的频道
- 发送状态
- 任何错误信息

示例日志：
```
2025-08-26 23:44:35,948 - Order Block信号已发送到频道 1404532905916760125: NASDAQ:TSLA - New Bullish OB Formed
```