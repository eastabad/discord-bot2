#!/usr/bin/env python3
"""
本地环境AI模板测试 - 验证修改是否成功
"""
import json
import os
import sys
import requests
from datetime import datetime

def check_template_file():
    """检查AI模板配置文件"""
    print("📁 1. 检查AI模板配置文件...")
    
    template_file = "config/simple_ai_templates.json"
    
    try:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            print(f"✅ 模板文件存在: {template_file}")
            print(f"📊 模板数量: {len(templates)}")
            
            # 显示所有模板类型
            print("📋 可用模板:")
            for key in templates.keys():
                print(f"  - {key}")
            
            # 检查RP模板 (可能叫做report或其他名称)
            rp_template = None
            for key, template in templates.items():
                if 'RP' in key or 'report' in key.lower() or 'Report' in key:
                    rp_template = template
                    print(f"✅ 找到报告模板: {key}")
                    break
            
            if not rp_template:
                # 检查所有模板内容，找包含新格式的
                for key, template in templates.items():
                    if "市场概况" in template and "关键交易信号" in template:
                        rp_template = template
                        print(f"✅ 找到包含新格式的模板: {key}")
                        break
            
            if rp_template:
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
                    print("\n🎉 AI模板格式验证通过!")
                    print("\n📄 模板预览:")
                    print(rp_template[:300] + "...")
                    return True, rp_template
                else:
                    print("\n⚠️  AI模板格式不完整")
                    return False, rp_template
            else:
                print("❌ 未找到报告模板")
                print("💡 现有模板内容:")
                for key, template in templates.items():
                    print(f"\n{key}模板预览:")
                    print(template[:200] + "...")
                return False, None
        else:
            print(f"❌ 模板文件不存在: {template_file}")
            return False, None
            
    except Exception as e:
        print(f"❌ 检查模板文件失败: {e}")
        return False, None

def test_template_engine():
    """测试AI模板引擎"""
    print("\n🔧 2. 测试AI模板引擎...")
    
    try:
        sys.path.append('.')
        from ai_template_engine import AITemplateEngine
        
        # 创建模板引擎实例
        template_engine = AITemplateEngine()
        template_engine.load_simple_templates()
        
        print("✅ AI模板引擎加载成功")
        
        # 模拟测试数据
        test_data = {
            "ticker": "AAPL",
            "symbol": "AAPL",
            "action": "buy",
            "timeframe": "1h",
            "current_price": 189.25,
            "MAtrend": "bullish",
            "MAtrend2": "bullish",
            "ratingstatus": "strong_buy",
            "AIbandsignal": "bullish_momentum",
            "pmaText": "PMA Strong Bullish signals indicate sustained upward momentum",
            "MOMOsignal": "bullish",
            "center_trend": "uptrend",
            "wavemarket_state": "impulse_wave",
            "RSIHAsignal": "bullish"
        }
        
        # 尝试生成不同类型的模板
        template_types = ['RP', 'report', 'Report', 'trading_report']
        
        success = False
        for template_type in template_types:
            try:
                prompt = template_engine.generate_prompt(template_type, test_data)
                if prompt:
                    print(f"✅ 成功生成 {template_type} 模板")
                    print(f"📝 提示长度: {len(prompt)} 字符")
                    
                    # 检查新格式
                    required_sections = [
                        "## 📈 市场概况",
                        "## 🔑 关键交易信号",
                        "## 📉 趋势分析",
                        "## 💡 投资建议",
                        "## ⚠️ 风险提示"
                    ]
                    
                    print(f"\n📋 {template_type}模板格式验证:")
                    all_present = True
                    for section in required_sections:
                        if section in prompt:
                            print(f"✅ {section}")
                        else:
                            print(f"❌ {section} - 缺失")
                            all_present = False
                    
                    if all_present:
                        print(f"\n🎉 {template_type}模板格式完全正确!")
                        print(f"\n📄 生成的提示预览:\n{prompt[:500]}...")
                        success = True
                        break
                    else:
                        print(f"\n⚠️  {template_type}模板格式不完整")
                        
            except Exception as e:
                print(f"⚠️  {template_type}模板生成失败: {e}")
                continue
        
        return success
        
    except ImportError as e:
        print(f"❌ 导入AI模板引擎失败: {e}")
        return False
    except Exception as e:
        print(f"❌ AI模板引擎测试失败: {e}")
        return False

def test_local_services():
    """测试本地服务"""
    print("\n🚀 3. 测试本地服务...")
    
    services = [
        ("API服务", "http://localhost:5000/api/health"),
        ("配置服务", "http://localhost:8081/api/ai-templates-unified"),
        ("AI状态", "http://localhost:5000/api/ai-status")
    ]
    
    results = []
    
    for service_name, url in services:
        try:
            print(f"\n🔍 检查{service_name}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {service_name}正常运行")
                
                if "ai-templates" in url:
                    templates = response.json()
                    print(f"📊 可用模板: {len(templates)}")
                    for key in templates.keys():
                        print(f"  - {key}")
                
                results.append((service_name, True))
            else:
                print(f"⚠️  {service_name}响应异常: {response.status_code}")
                results.append((service_name, False))
                
        except Exception as e:
            print(f"❌ {service_name}连接失败: {e}")
            results.append((service_name, False))
    
    return results

def send_test_message():
    """发送测试消息验证按钮功能"""
    print("\n📡 4. 发送测试消息...")
    
    test_data = {
        "ticker": "NVDA",
        "symbol": "NVDA",
        "action": "buy",
        "data_type": "signal",
        "timeframe": "1h",
        "timestamp": datetime.now().isoformat(),
        
        # 完整技术指标
        "MAtrend": "bullish",
        "MAtrend2": "bullish",
        "MAtrend3": "neutral",
        "TrendTracer": "bullish",
        "TrendTracer2": "bullish",
        "AIbandsignal": "bullish_momentum",
        "ratingstatus": "strong_buy",
        "pmaText": "PMA Strong Bullish signals indicate sustained upward momentum with institutional support and volume confirmation",
        "MOMOsignal": "bullish",
        "center_trend": "uptrend",
        "wavemarket_state": "impulse_wave",
        "EW_trend": "wave_3_up",
        "RSIHAsignal": "bullish",
        "CVD_state": "accumulation",
        "ADX_state": "trending_strong",
        "squeeze_status": "out_of_squeeze",
        "chopping_status": "trending",
        "risk_level": "medium",
        "current_price": 875.42,
        "stop_loss_level": 850.00,
        "volume": 18234567
    }
    
    try:
        webhook_url = "http://localhost:5000/webhook/tradingview"
        response = requests.post(webhook_url, json=test_data, timeout=15)
        
        if response.status_code == 200:
            print("✅ 测试webhook发送成功")
            print("📨 NVDA交易信号已发送到Discord")
            print("\n🎯 验证步骤:")
            print("1. 检查Discord频道中的NVDA交易信号")
            print("2. 点击'AI辅助决策'按钮")
            print("3. 验证AI报告包含新的5个Markdown章节")
            return True
        else:
            print(f"❌ 测试webhook发送失败: {response.status_code}")
            print(f"错误: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送测试消息失败: {e}")
        return False

def main():
    """主测试流程"""
    print("🧪 本地AI模板测试 - 验证修改成功")
    print("=" * 70)
    
    all_tests = [
        ("模板文件检查", lambda: check_template_file()[0]),
        ("模板引擎测试", test_template_engine),
        ("本地服务测试", lambda: all(result[1] for result in test_local_services())),
        ("Discord消息测试", send_test_message)
    ]
    
    results = []
    
    for test_name, test_func in all_tests:
        print(f"\n🔄 执行: {test_name}")
        print("-" * 50)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}执行异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("📊 本地AI模板测试结果汇总:")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15} : {status}")
    
    print("=" * 70)
    print(f"📈 总体结果: {passed}/{total} 通过")
    
    if passed >= 3:  # 至少3个测试通过
        print("\n🎉 AI模板修改测试基本通过!")
        print("\n🎯 Discord验证步骤:")
        print("1. 检查Discord频道是否收到NVDA交易信号")
        print("2. 点击消息下方的'AI辅助决策'按钮")
        print("3. 验证AI分析报告是否包含新的5个章节:")
        print("   - 📈 市场概况")
        print("   - 🔑 关键交易信号")
        print("   - 📉 趋势分析")
        print("   - 💡 投资建议")
        print("   - ⚠️ 风险提示")
        print("\n💡 如果按钮点击后生成的报告包含这些章节，说明修改成功!")
    else:
        print("\n⚠️  部分测试失败，需要检查配置")
    
    return passed >= 3

if __name__ == "__main__":
    main()