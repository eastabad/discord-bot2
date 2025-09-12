#!/usr/bin/env python3
"""
模拟完整的TradingView webhook - 包含AI决策按钮
"""
import requests
import json

def send_webhook_with_buttons():
    """发送包含AI决策按钮的webhook消息"""
    
    # 模拟TradingView webhook数据
    webhook_data = {
        "ticker": "TSLA",
        "symbol": "TSLA",  # 添加symbol字段
        "action": "buy",
        "data_type": "signal",
        "timeframe": "15m",
        "timestamp": "2025-08-18T14:35:00.000Z",
        
        # 完整技术指标
        "MAtrend": "bullish",
        "MAtrend2": "bullish",
        "MAtrend3": "neutral",
        "TrendTracer": "bullish", 
        "TrendTracer2": "bullish",
        "AIbandsignal": "bullish_momentum",
        "ratingstatus": "strong_buy",
        "pmaText": "PMA Strong Bullish signals push PMA breakout above resistance, signaling potential upward momentum with strong volume confirmation and sustained buying pressure",
        "MOMOsignal": "bullish",
        "center_trend": "uptrend",
        "wavemarket_state": "impulse_wave",
        "EW_trend": "wave_5_up",
        "RSIHAsignal": "bullish",
        "CVD_state": "accumulation",
        "ADX_state": "trending_strong",
        "squeeze_status": "out_of_squeeze",
        "chopping_status": "trending",
        "risk_level": "medium",
        "stop_loss_level": 240.50,
        "current_price": 245.67,
        "volume": 25678923
    }
    
    print("🚀 发送带AI决策按钮的TradingView webhook...")
    
    # 发送到webhook处理端点 (这会自动创建按钮)
    webhook_url = "http://localhost:5000/webhook/tradingview"
    
    try:
        response = requests.post(webhook_url, json=webhook_data, timeout=15)
        
        if response.status_code == 200:
            print("✅ Webhook发送成功!")
            print("📨 Discord消息已发送，包含AI决策按钮")
            print("\n🎯 测试步骤:")
            print("1. 在Discord查看TSLA交易信号消息")
            print("2. 点击'AI辅助决策'按钮")
            print("3. 验证新的AI模板格式 (Markdown结构)")
            print("4. 检查是否包含:")
            print("   - 📈 市场概况")
            print("   - 🔑 关键交易信号")
            print("   - 📉 趋势分析")
            print("   - 💡 投资建议")
            print("   - ⚠️ 风险提示")
            return True
        else:
            print(f"❌ Webhook发送失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AI决策按钮完整测试")
    print("=" * 50)
    send_webhook_with_buttons()