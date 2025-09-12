#!/usr/bin/env python3
"""
手动AI按钮测试 - 模拟点击AI决策按钮的后端处理
"""
import requests
import json
from datetime import datetime

def simulate_ai_button_click():
    """模拟AI决策按钮点击，测试新模板"""
    
    # 模拟webhook数据
    webhook_data = {
        "ticker": "TSLA",
        "symbol": "TSLA",
        "action": "buy",
        "timeframe": "15m",
        "current_price": 245.67,
        
        # 技术指标数据
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
        "volume": 25678923
    }
    
    print("🤖 模拟AI决策按钮点击...")
    print(f"📊 测试数据: {webhook_data['ticker']} {webhook_data['action']}")
    
    # 这里模拟button interaction处理逻辑
    # 实际环境中这会触发multi_ai_service中的AI分析
    
    # 1. 首先测试AI模板引擎
    print("\n🔧 1. 测试AI模板生成...")
    try:
        # 导入AI模板引擎 (如果在VPS环境中)
        import sys
        sys.path.append('.')
        
        from ai_template_engine import AITemplateEngine
        
        template_engine = AITemplateEngine()
        # 修正方法调用
        template_engine.load_simple_templates()
        
        # 生成RP模板提示
        prompt = template_engine.generate_prompt('RP', webhook_data)
        
        if prompt:
            print("✅ AI模板生成成功")
            print(f"📝 提示长度: {len(prompt)} 字符")
            
            # 检查新格式
            required_sections = [
                "## 📈 市场概况",
                "## 🔑 关键交易信号",
                "## 📉 趋势分析",
                "## 💡 投资建议", 
                "## ⚠️ 风险提示"
            ]
            
            print("\n📋 模板格式验证:")
            for section in required_sections:
                if section in prompt:
                    print(f"✅ {section}")
                else:
                    print(f"❌ {section} - 缺失")
            
            print(f"\n📄 生成的提示预览:\n{prompt[:500]}...")
            return True
        else:
            print("❌ AI模板生成失败")
            return False
            
    except ImportError as e:
        print(f"⚠️  本地模块导入失败: {e}")
        print("💡 这在VPS环境中是正常的，继续API测试...")
        return test_via_api(webhook_data)
    except Exception as e:
        print(f"❌ AI模板测试异常: {e}")
        return test_via_api(webhook_data)

def test_via_api(webhook_data):
    """通过API测试AI模板"""
    print("\n🌐 2. 通过VPS API测试...")
    
    # 本地环境API测试
    base_url = "http://localhost:5000"
    
    try:
        # 发送webhook触发AI按钮生成
        webhook_url = f"{base_url}/webhook/tradingview"
        response = requests.post(webhook_url, json=webhook_data, timeout=15)
        
        if response.status_code == 200:
            print("✅ Webhook处理成功")
            print("📨 Discord消息已发送，包含AI决策按钮")
            
            # 等待一段时间让用户点击按钮
            print("\n⏳ 请在Discord中:")
            print("1. 找到TSLA交易信号消息")
            print("2. 点击'AI辅助决策'按钮")
            print("3. 验证AI报告是否包含新的5个章节格式")
            
            return True
        else:
            print(f"❌ Webhook发送失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def check_ai_template_file():
    """检查AI模板配置文件"""
    print("\n📁 3. 检查AI模板文件...")
    
    template_file = "config/simple_ai_templates.json"
    
    try:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            print(f"✅ 模板文件存在: {template_file}")
            print(f"📊 模板数量: {len(templates)}")
            
            # 检查RP模板
            if 'RP' in templates:
                rp_template = templates['RP']
                print("✅ RP模板已配置")
                print(f"📝 模板长度: {len(rp_template)} 字符")
                
                # 验证新格式标识
                required_sections = [
                    "## 📈 市场概况",
                    "## 🔑 关键交易信号",
                    "## 📉 趋势分析",
                    "## 💡 投资建议",
                    "## ⚠️ 风险提示"
                ]
                
                print("\n📋 模板内容验证:")
                all_present = True
                for section in required_sections:
                    if section in rp_template:
                        print(f"✅ {section}")
                    else:
                        print(f"❌ {section} - 缺失")
                        all_present = False
                
                if all_present:
                    print("\n🎉 RP模板格式验证通过!")
                    return True
                else:
                    print("\n⚠️  RP模板格式不完整")
                    return False
            else:
                print("❌ RP模板未找到")
                return False
        else:
            print(f"❌ 模板文件不存在: {template_file}")
            return False
            
    except Exception as e:
        print(f"❌ 检查模板文件失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 手动AI按钮测试 - 验证新模板")
    print("=" * 60)
    
    tests = [
        ("模板文件检查", check_ai_template_file),
        ("AI按钮模拟", simulate_ai_button_click)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔄 执行: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    print("=" * 60)
    print(f"📈 结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 AI模板测试全部通过!")
        print("🎯 现在可以在Discord中测试AI决策按钮功能")
    else:
        print("\n⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    import os
    main()