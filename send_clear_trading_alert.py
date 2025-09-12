#!/usr/bin/env python3
"""
发送清晰的交易提醒信号供用户点击AI决策按钮
"""
import requests
import json
from datetime import datetime

def send_clear_mstr_alert():
    """发送清晰的MSTR交易提醒"""
    print("📨 发送清晰的MSTR交易提醒...")
    
    # 准备完整的MSTR信号数据
    mstr_alert = {
        "ticker": "MSTR",
        "symbol": "MSTR", 
        "action": "sell",
        "data_type": "signal",
        "timeframe": "15m",
        "timestamp": datetime.now().isoformat(),
        "quantity": 120,
        
        # 关键技术指标
        "center_trend": "Strong Bearish",
        "wavemarket_state": "Short Strong", 
        "AIbandsignal": "red downtrend",
        "RSIHAsignal": "BearishHA",
        "MOMOsignal": "bearishmomo",
        "MAtrend": "-1",
        "TrendTracersignal": "-1",
        "pmaText": "PMA Bearish divergence signals potential downward pressure with institutional selling pressure",
        "CVDsignal": "cvdBelowMA",
        "adxValue": 35.34,
        "choppiness": 46.41,
        "risk_level": "high",
        
        # 价格信息
        "current_price": 330.25,
        "stop_loss_level": 332.72,
        "take_profit_level": 322.79,
        
        # 评级信息
        "ratingstatus": "strong_sell",
        "oscrating": 90,
        "trendrating": 100,
        
        # 完整的解析数据
        "parsed_summary": "MA趋势: 看跌 | 中枢趋势: Strong Bearish | 波浪状态: Short Strong | AI波段: red downtrend | RSI HA: BearishHA | 动量: bearishmomo | PMA: Bearish | CVD: cvdBelowMA",
        
        # 原始body数据保持兼容性
        "body": {
            "symbol": "MSTR",
            "action": "sell",
            "quantity": 120,
            "center_trend": "Strong Bearish",
            "wavemarket_state": "Short Strong",
            "AIbandsignal": "red downtrend",
            "RSIHAsignal": "BearishHA", 
            "MOMOsignal": "bearishmomo",
            "MAtrend": "-1",
            "pmaText": "PMA Bearish divergence signals potential downward pressure with institutional selling pressure",
            "stopLoss": {"stopPrice": 332.72},
            "takeProfit": {"limitPrice": 322.79},
            "extras": {
                "indicator": "WaveMatrix shortStrongSignal",
                "timeframe": "15m",
                "oscrating": 90,
                "trendrating": 100,
                "risk": 1
            }
        }
    }
    
    # 发送到TradingView webhook端点
    webhook_url = "http://localhost:5000/webhook/tradingview"
    
    try:
        response = requests.post(
            webhook_url,
            json=mstr_alert,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MSTR交易提醒发送成功!")
            print(f"📊 信号: {mstr_alert['ticker']} {mstr_alert['action'].upper()}")
            print(f"💰 价格: ${mstr_alert['current_price']}")
            print(f"📉 趋势: {mstr_alert['center_trend']}")
            print(f"🌊 波浪: {mstr_alert['wavemarket_state']}")
            print(f"⏱️ 时间: {result.get('timestamp', 'N/A')}")
            
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def send_user_dm_alert():
    """发送用户私信提醒"""
    print("\n💬 发送私信交易提醒...")
    
    user_id = "1145170623354638418"
    
    dm_message = f"""
🚨 **MSTR交易信号** 

📈 **股票**: MSTR
🎯 **操作**: SELL (卖出)
📦 **数量**: 120股
💰 **当前价格**: $330.25

**价格目标:**
🛡️ 止损: $332.72
🎯 止盈: $322.79

**技术分析:**
📉 中枢趋势: Strong Bearish
🌊 波浪状态: Short Strong
🤖 AI波段: red downtrend
📊 RSI HA: BearishHA
⚡ 动量信号: bearishmomo

**评级:**
🔴 总体评级: Strong Sell
📊 振荡评级: 90/100
📈 趋势评级: 100/100

⚠️ **高风险信号** - 建议谨慎操作

👆 **点击下方'AI辅助决策'按钮获取详细分析报告**
"""

    # 发送私信
    api_url = "http://localhost:5000/api/send-dm"
    dm_data = {
        "userId": user_id,
        "content": dm_message
    }
    
    try:
        response = requests.post(api_url, json=dm_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 私信提醒发送成功!")
            print(f"📨 消息ID: {result.get('messageId', 'N/A')}")
            return True
        else:
            print(f"❌ 私信发送失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 私信发送异常: {e}")
        return False

def main():
    """主函数"""
    print("📢 发送MSTR交易提醒供用户测试AI决策按钮")
    print("=" * 60)
    
    # 发送频道信号
    channel_success = send_clear_mstr_alert()
    
    # 发送私信提醒
    dm_success = send_user_dm_alert()
    
    print("\n" + "=" * 60)
    
    if channel_success or dm_success:
        print("🎉 MSTR交易提醒已发送!")
        print("\n📱 请检查:")
        if channel_success:
            print("✅ Discord频道 - 查看MSTR交易信号")
        if dm_success:
            print("✅ Discord私信 - 查看详细交易提醒")
            
        print("\n🎯 测试步骤:")
        print("1. 在Discord中找到MSTR交易信号")
        print("2. 点击'AI辅助决策'按钮")
        print("3. 验证新的5章节AI报告格式:")
        print("   📈 市场概况")
        print("   🔑 关键交易信号")
        print("   📉 趋势分析")
        print("   💡 投资建议") 
        print("   ⚠️ 风险提示")
        
        return True
    else:
        print("❌ 交易提醒发送失败")
        return False

if __name__ == "__main__":
    main()