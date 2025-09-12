#!/usr/bin/env python3
"""
自动检测用户ID并发送私信测试
"""
import requests
import json
import time

def find_and_test_dm():
    """自动检测最近消息的用户ID并发送测试私信"""
    
    # 首先发送一个标识消息，让用户响应
    print("📢 发送用户识别消息...")
    
    api_url = "http://localhost:5000/api/send-message"
    identify_data = {
        "channelId": "1404532905916760125",
        "content": "🆔 **用户ID自动识别**\n\n请在此消息下方发送任意回复（如: 'test' 或 '测试'），我将自动获取你的用户ID并发送私信测试。\n\n⏰ 请在30秒内回复..."
    }
    
    try:
        response = requests.post(api_url, json=identify_data, timeout=10)
        if response.status_code == 200:
            print("✅ 识别消息已发送到频道")
            print("⏳ 等待用户回复以获取用户ID...")
            
            # 等待一段时间让用户回复
            time.sleep(5)
            
            # 这里应该从Discord事件或日志中获取用户ID
            # 由于无法直接访问Discord事件，我们提供手动输入选项
            print("\n💡 请提供你的Discord用户ID以继续测试")
            print("获取方法:")
            print("1. 在Discord设置中开启'开发者模式'")
            print("2. 右键点击你的用户名")
            print("3. 选择'复制用户ID'")
            
            return None
            
    except Exception as e:
        print(f"❌ 发送识别消息失败: {e}")
        return None

def send_personal_dm_test(user_id):
    """发送个人交易信号私信测试"""
    
    # 构造个人交易信号
    signal_data = {
        "ticker": "AAPL",
        "symbol": "AAPL",
        "action": "buy",
        "data_type": "personal_signal",
        "timeframe": "1h",
        "timestamp": "2025-08-18T14:35:00.000Z",
        
        # 技术指标
        "MAtrend": "bullish",
        "MAtrend2": "bullish",
        "MAtrend3": "neutral",
        "TrendTracer": "bullish",
        "AIbandsignal": "bullish_momentum",
        "ratingstatus": "strong_buy",
        "pmaText": "PMA Strong Bullish signals push price above key resistance with volume confirmation",
        "MOMOsignal": "bullish",
        "center_trend": "uptrend",
        "wavemarket_state": "impulse_wave",
        "RSIHAsignal": "bullish",
        
        # 价格信息
        "current_price": 189.25,
        "stop_loss_level": 185.50,
        "target_price": 195.00,
        "volume": 45678923,
        
        # 个人信号特有字段
        "signal_source": "personal_webhook",
        "confidence_level": "high",
        "risk_level": "medium"
    }
    
    # 私信内容
    dm_content = f"""
🔔 **个人交易信号** - {signal_data['ticker']}

🎯 **操作**: {signal_data['action'].upper()}
📊 **时间框架**: {signal_data['timeframe']}  
💰 **当前价格**: ${signal_data['current_price']}
🛡️ **止损**: ${signal_data['stop_loss_level']}
🎯 **目标**: ${signal_data['target_price']}

**技术分析摘要:**
• MA趋势: {signal_data['MAtrend']}
• 评级状态: {signal_data['ratingstatus']}
• AI波段信号: {signal_data['AIbandsignal']}
• 动量指标: {signal_data['MOMOsignal']}
• 中枢趋势: {signal_data['center_trend']}

**PMA分析:**
{signal_data['pmaText']}

⚡ **点击下方按钮进行AI分析和交易操作**

---
🔐 个人信号 | 置信度: {signal_data['confidence_level']} | 风险: {signal_data['risk_level']}
"""

    # 发送私信
    api_url = "http://localhost:5000/api/send-dm"
    dm_data = {
        "userId": user_id,
        "content": dm_content,
        "signal_data": signal_data,  # 附加信号数据供按钮使用
        "message_type": "personal_trading_signal"
    }
    
    try:
        print(f"📤 发送个人交易信号私信到用户 {user_id}...")
        
        response = requests.post(api_url, json=dm_data, timeout=15)
        
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 个人交易信号私信发送成功!")
            print(f"📨 消息ID: {result.get('messageId', 'N/A')}")
            print("\n🎯 现在检查Discord私信:")
            print("1. 收到AAPL个人交易信号")
            print("2. 点击'AI辅助决策'按钮")
            print("3. 验证AI报告使用新的模板格式:")
            print("   - 📈 市场概况")
            print("   - 🔑 关键交易信号") 
            print("   - 📉 趋势分析")
            print("   - 💡 投资建议")
            print("   - ⚠️ 风险提示")
            print("4. 测试其他按钮功能")
            return True
        elif response.status_code == 404:
            print("❌ 用户未找到")
            print("💡 请确认用户ID正确且用户在服务器中")
            return False
        elif response.status_code == 403:
            print("❌ 无法发送私信")
            print("💡 用户可能关闭了接收陌生人私信的设置")
            return False
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

if __name__ == "__main__":
    print("💬 发送个人交易信号私信测试")
    print("=" * 60)
    
    # 使用提供的用户ID直接发送测试
    user_id = "1145170623354638418"
    print(f"🆔 使用用户ID: {user_id}")
    
    # 发送个人交易信号私信测试
    send_personal_dm_test(user_id)
    
    print("=" * 60)