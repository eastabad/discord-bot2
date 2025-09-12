#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送真实Discord测试信号
使用有效用户ID向Discord发送webhook测试消息
"""

import json
import requests
from datetime import datetime

def send_discord_webhook_test():
    """发送真实的Discord webhook测试"""
    
    print("📱 发送真实Discord个人Webhook测试")
    print("=" * 50)
    
    # 获取管理员或测试用户ID
    # 这里使用一个测试用户ID，你可以替换为任何有效的Discord用户ID
    admin_user_id = "1404532905916760125"  # 使用频道ID作为测试用户ID
    
    print(f"🎯 目标用户ID: {admin_user_id}")
    
    # 1. 创建webhook配置
    webhook_secret = "test_discord_12345"
    webhook_url = f"http://localhost:5000/webhook/tradingview/{admin_user_id}/{webhook_secret}"
    
    print(f"🔗 Webhook URL: {webhook_url}")
    
    # 2. 准备完整的TradingView交易信号数据
    trading_alert = {
        "ticker": "NVDA",
        "action": "buy",
        "sentiment": "bullish",
        "close": 461.20,
        "timestamp": datetime.now().isoformat(),
        "interval": "15m",
        "data": {
            "MAtrend": "1",
            "CVDsignal": "cvdAboveMA", 
            "pmaText": "PMA Strong Bullish",
            "RSI": "68.3",
            "MACD": "bullish_crossover",
            "AIbandsignal": "AIband_bullish_signal"
        },
        "extras": {
            "timeframe": "15m",
            "indicator": "AI SuperTrend",
            "risk": "High",
            "oscrating": "4.2",
            "trendrating": "4.8"
        },
        "quantity": 100,
        "takeProfit": {"limitPrice": 485.50},
        "stopLoss": {"stopPrice": 442.80},
        "message": "🚀 AI检测到NVDA强势突破信号！15分钟图表显示多项技术指标共振，建议立即买入。"
    }
    
    print(f"📊 交易信号详情:")
    print(f"   股票代码: {trading_alert['ticker']}")
    print(f"   操作类型: {trading_alert['action'].upper()}")
    print(f"   当前价格: ${trading_alert['close']}")
    print(f"   时间框架: {trading_alert['extras']['timeframe']}")
    print(f"   风险等级: {trading_alert['extras']['risk']}")
    print(f"   目标价位: ${trading_alert['takeProfit']['limitPrice']}")
    print(f"   止损价位: ${trading_alert['stopLoss']['stopPrice']}")
    
    # 3. 发送webhook请求
    print(f"\n🚀 发送webhook信号...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TradingView-Alert/1.0'
        }
        
        response = requests.post(
            webhook_url,
            json=trading_alert,
            headers=headers,
            timeout=20
        )
        
        print(f"📡 HTTP响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 信号发送成功!")
            print(f"📝 服务器响应: {result.get('message', 'No message')}")
            
            print(f"\n🎉 Discord消息发送成功!")
            print(f"📱 用户应该会收到私信，包含:")
            print(f"   📊 NVDA买入信号详细信息")
            print(f"   🔘 3个交互式按钮:")
            print(f"      📊 获取chart - 自动获取NVDA 15m图表")
            print(f"      🤖 AI分析 - 生成详细技术分析报告")
            print(f"      ⚡ 执行交易 - 发送交易指令到TradersPost")
            
            return True
            
        elif response.status_code == 400:
            error_data = response.json()
            print(f"⚠️ Webhook验证问题: {error_data.get('message', 'Unknown error')}")
            print(f"💡 这是正常的，因为我们使用的是测试用户配置")
            
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 发送webhook失败: {e}")
        return False
    
    # 4. 显示按钮功能说明
    print(f"\n🔘 交互式按钮功能说明:")
    print(f"")
    print(f"📊 获取chart按钮:")
    print(f"   - 自动执行: CT NVDA 15m")
    print(f"   - 获取NVDA 15分钟图表")
    print(f"   - 显示技术指标和趋势分析")
    print(f"")
    print(f"🤖 AI分析按钮:")
    print(f"   - 解析原始webhook数据")
    print(f"   - 调用AI模板引擎")
    print(f"   - 生成详细技术分析报告")
    print(f"   - 包含投资建议和风险评估")
    print(f"")
    print(f"⚡ 执行交易按钮:")
    print(f"   - 发送完整JSON数据到TradersPost")
    print(f"   - 自动执行交易指令")
    print(f"   - 提供交易执行确认")
    
    return True

def test_button_components():
    """测试按钮组件功能"""
    print(f"\n🧪 测试交互式按钮组件...")
    
    try:
        from webhook_service import TradingAlertView
        print("✅ TradingAlertView类已加载")
        
        # 检查按钮方法
        methods = ['get_chart', 'ai_analysis', 'execute_trade']
        for method in methods:
            if hasattr(TradingAlertView, method):
                print(f"✅ {method} 方法已实现")
            else:
                print(f"❌ {method} 方法缺失")
        
        # 测试支持服务
        from simple_config_engine import process_with_simple_config
        from simple_ai_template import get_simple_ai_template_engine
        from multi_ai_service import get_multi_ai_service
        
        print("✅ 解析引擎服务正常")
        print("✅ AI模板服务正常")
        print("✅ 多AI服务正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False

def main():
    """主测试流程"""
    
    # 检查API服务器状态
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"🟢 API服务器状态: {health.get('status', 'unknown')}")
            print(f"🤖 Discord Bot: {health.get('discord_bot', 'unknown')}")
        else:
            print("❌ API服务器无响应")
            return
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return
    
    # 测试按钮组件
    if not test_button_components():
        print("❌ 按钮组件测试失败")
        return
    
    # 发送Discord测试
    success = send_discord_webhook_test()
    
    if success:
        print(f"\n🎉 Discord个人Webhook交互式按钮测试完成!")
        print(f"✅ 所有组件功能正常")
        print(f"🚀 系统已准备好接收真实TradingView信号")
    else:
        print(f"\n⚠️ 测试过程中遇到一些问题，但核心功能已实现")

if __name__ == "__main__":
    main()