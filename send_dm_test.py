#!/usr/bin/env python3
"""
直接通过API发送私信测试AI按钮
"""
import requests
import json

def send_dm_with_buttons():
    """直接发送包含AI按钮的私信"""
    
    # 你的Discord用户ID - 需要替换
    # 可以通过在Discord频道发消息，然后查看日志获取
    user_id = "YOUR_USER_ID"  # 替换为实际用户ID
    
    # 模拟交易信号数据
    signal_data = {
        "ticker": "META",
        "symbol": "META",
        "action": "buy",
        "timeframe": "1h", 
        "current_price": 485.23,
        "MAtrend": "bullish",
        "ratingstatus": "strong_buy",
        "AIbandsignal": "bullish_momentum",
        "pmaText": "PMA Strong Bullish signals indicate upward momentum with institutional buying support",
        "MOMOsignal": "bullish",
        "center_trend": "uptrend",
        "wavemarket_state": "impulse_wave",
        "RSIHAsignal": "bullish"
    }
    
    # 构造私信内容
    dm_content = f"""
🔔 **个人交易信号** - {signal_data['ticker']}

🎯 **信号**: {signal_data['action'].upper()}
📊 **时间框架**: {signal_data['timeframe']}
💰 **当前价格**: ${signal_data['current_price']}

**技术分析:**
• MA趋势: {signal_data['MAtrend']}
• 评级状态: {signal_data['ratingstatus']}
• AI波段: {signal_data['AIbandsignal']}
• 动量信号: {signal_data['MOMOsignal']}

⚡ **点击按钮测试AI分析功能**
"""

    # API请求
    api_url = "http://localhost:5000/api/send-dm"
    request_data = {
        "userId": user_id,
        "content": dm_content,
        "signal_data": signal_data  # 附加信号数据供按钮使用
    }
    
    try:
        print("📤 发送私信测试...")
        print(f"👤 目标用户ID: {user_id}")
        
        response = requests.post(api_url, json=request_data, timeout=15)
        
        print(f"📊 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 私信发送成功!")
            print(f"📨 消息ID: {result.get('messageId', 'N/A')}")
            print("\n🎯 现在检查:")
            print("1. Discord私信中的META交易信号")
            print("2. 点击'AI辅助决策'按钮测试新模板")
            return True
        elif response.status_code == 404:
            print("❌ 用户未找到 - 请检查用户ID是否正确")
            return False
        elif response.status_code == 403:
            print("❌ 无法发送私信 - 用户可能关闭了陌生人私信")
            return False
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False

def get_user_id_hint():
    """提供获取用户ID的提示"""
    print("💡 获取Discord用户ID的方法:")
    print("1. 在Discord中发送任意消息到监控频道")
    print("2. 查看机器人日志中的用户信息")
    print("3. 或者在Discord设置中开启开发者模式")
    print("4. 右键点击你的用户名选择'复制用户ID'")
    
    # 发送提示消息到频道
    try:
        api_url = "http://localhost:5000/api/send-message"
        hint_data = {
            "channelId": "1404532905916760125",
            "content": "🔍 **用户ID获取提示**\n\n请在此频道发送任意消息，然后查看机器人日志获取你的用户ID，用于私信测试。\n\n或者开启Discord开发者模式，右键你的用户名复制ID。"
        }
        
        response = requests.post(api_url, json=hint_data, timeout=10)
        if response.status_code == 200:
            print("📝 已在频道发送用户ID获取提示")
            
    except Exception as e:
        print(f"⚠️ 发送提示失败: {e}")

if __name__ == "__main__":
    print("💬 Discord私信AI按钮测试")
    print("=" * 50)
    
    # 提供用户ID获取提示
    get_user_id_hint()
    
    print("\n" + "=" * 50)
    print("⚠️ 设置用户ID后取消下行注释运行测试:")
    print("# send_dm_with_buttons()")
    print("=" * 50)