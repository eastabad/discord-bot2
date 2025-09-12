# OB Command Implementation Test Guide

## Overview
OB命令已成功实现，允许用户请求使用替代布局(OB Layout ID: 2052)的股票图表。

## Implementation Details

### 1. OB Command Detection
- **Function**: `has_ob_command()` in `bot.py`
- **Pattern Support**: 
  - `OB AAPL,15m` (space-separated)
  - `OB,AAPL,15m` (comma-separated)
- **Case Insensitive**: Yes
- **Regex Patterns**:
  ```python
  r'OB\s+[A-Z][A-Z:]*[A-Z][,，]\s*\d+[smhdwMy]'    # OB AAPL,15m
  r'OB[,，]\s*[A-Z][A-Z:]*[A-Z][,，]\s*\d+[smhdwMy]'  # OB,AAPL,15m
  ```

### 2. OB Chart Processing
- **Function**: `handle_ob_chart_request()` in `bot.py`
- **Features**:
  - Rate limiting (3 requests/day per user)
  - VIP exemption support
  - Private message delivery
  - Request logging
  - Error handling with retry mechanisms

### 3. Chart Service Integration
- **Function**: `get_ob_chart()` in `chart_service.py`
- **API Endpoint**: `https://api.chart-img.com/v2/tradingview/layout-chart/2052`
- **Layout ID**: Uses `OB_LAYOUT_ID=2052` from configuration
- **Features**:
  - Same symbol normalization as CT command
  - Exchange detection and mapping
  - TradingView session support
  - 180-second timeout
  - Comprehensive error logging

### 4. Message Formatting
- **Success Message**: `format_ob_success_message()`
- **DM Content**: `format_ob_dm_content()`
- **File Naming**: `{symbol}_{timeframe}_OB.png`

### 5. Channel Cleanup Protection
- **Pattern Added**: `r'OB\s+[A-Z]{2,5}'` in `channel_cleaner.py`
- **Purpose**: Prevents OB commands from being deleted during cleanup

## Testing Commands

### Valid OB Commands:
```
OB AAPL,1h
OB TSLA,15m
OB NVDA,4h
OB,MSFT,1d
OB GOOGL,1w
```

### Supported Timeframes:
- Minutes: 1m, 5m, 15m, 30m
- Hours: 1h, 2h, 4h, 6h, 12h
- Days: 1d
- Weeks: 1w
- Months: 1M

## Configuration
- **Layout ID**: IoT1qwuk (alternative layout for OB command) ✅ CONFIGURED
- **Primary Layout**: Gc320R2h (for CT command) ✅ CONFIGURED
- **API Key**: Uses same CHART_IMG_API_KEY as CT command ✅ CONFIGURED
- **Session Support**: Uses same TradingView session credentials ✅ CONFIGURED

## Expected User Experience
1. User sends: `OB AAPL,1h`
2. Bot adds ⏳ reaction
3. Bot processes request with rate limiting check
4. Bot generates chart using layout 2052
5. Bot sends chart to user's DM
6. Bot updates channel with success message and remaining quota
7. Bot changes reaction to ✅

## Logging
- Request type: "ob_chart"
- Log entries include symbol, timeframe, and layout ID
- Error logging for API failures and timeouts
- Success logging with image size information

## Integration Status
✅ Command detection implemented
✅ Request handler created
✅ Chart service OB method added
✅ Message formatting functions added
✅ Channel cleanup protection added
✅ Configuration support verified
✅ Rate limiting integrated
✅ Private message delivery
✅ Error handling complete

## Ready for Testing
The OB command is fully implemented and ready for user testing in Discord channels.