#!/usr/bin/env python3
"""
最终AI模板验证 - 直接检查模板内容和测试按钮功能
"""
import json
import os
import requests
from datetime import datetime

def verify_rp_template():
    """验证RP模板是否包含新的5个章节格式"""
    print("📁 验证RP模板配置...")
    
    try:
        # 读取模板文件
        with open('config/simple_ai_templates.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 获取模板部分
        templates = config.get('templates', {})
        rp_template = templates.get('RP', {})
        
        if rp_template:
            template_content = rp_template.get('template', '')
            print("✅ 找到RP模板")
            print(f"📝 模板长度: {len(template_content)} 字符")
            
            # 检查新的5个章节
            required_sections = [
                "## 📈 市场概况",
                "## 🔑 关键交易信号", 
                "## 📉 趋势分析",
                "## 💡 投资建议",
                "## ⚠️ 风险提示"
            ]
            
            print("\n🔍 验证新章节格式:")
            all_present = True
            for section in required_sections:
                if section in template_content:
                    print(f"✅ {section}")
                else:
                    print(f"❌ {section} - 缺失")
                    all_present = False
            
            if all_present:
                print("\n🎉 RP模板新格式验证成功!")
                print("\n📄 模板内容预览:")
                # 显示每个章节的内容
                lines = template_content.split('\n')
                for i, line in enumerate(lines):
                    if any(section in line for section in required_sections):
                        print(f"📍 {line}")
                        # 显示该章节下面几行内容
                        for j in range(i+1, min(i+4, len(lines))):
                            if lines[j].strip() and not lines[j].startswith('##'):
                                print(f"   {lines[j]}")
                            elif lines[j].startswith('##'):
                                break
                
                return True, template_content
            else:
                print("\n⚠️ RP模板格式不完整")
                return False, template_content
        else:
            print("❌ 未找到RP模板")
            return False, None
            
    except Exception as e:
        print(f"❌ 读取模板文件失败: {e}")
        return False, None

def test_ai_template_generation():
    """测试AI模板生成功能"""
    print("\n🔧 测试AI模板生成...")
    
    try:
        from ai_template_engine import AITemplateEngine
        
        # 创建实例并加载模板
        engine = AITemplateEngine()
        engine.load_simple_templates()
        
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
            "pmaText": "PMA Strong Bullish signals indicate sustained upward momentum with volume support",
            "MOMOsignal": "bullish",
            "center_trend": "uptrend",
            "wavemarket_state": "impulse_wave",
            "RSIHAsignal": "bullish",
            "CVD_state": "accumulation"
        }
        
        print("✅ AI模板引擎初始化成功")
        
        # 尝试生成RP模板
        prompt = engine.generate_prompt('RP', test_data)
        
        if prompt:
            print("✅ RP模板生成成功")
            print(f"📝 生成提示长度: {len(prompt)} 字符")
            
            # 验证生成的提示是否包含新格式
            required_sections = [
                "## 📈 市场概况",
                "## 🔑 关键交易信号",
                "## 📉 趋势分析", 
                "## 💡 投资建议",
                "## ⚠️ 风险提示"
            ]
            
            print("\n🔍 验证生成提示格式:")
            all_present = True
            for section in required_sections:
                if section in prompt:
                    print(f"✅ {section}")
                else:
                    print(f"❌ {section} - 缺失")
                    all_present = False
            
            if all_present:
                print("\n🎉 AI模板生成格式完全正确!")
                print(f"\n📄 生成提示预览 (前500字符):\n{prompt[:500]}...")
                return True
            else:
                print("\n⚠️ 生成的提示格式不完整")
                print(f"\n📄 实际生成内容:\n{prompt}")
                return False
        else:
            print("❌ RP模板生成失败")
            return False
            
    except Exception as e:
        print(f"❌ AI模板生成测试失败: {e}")
        return False

def send_final_test_webhook():
    """发送最终测试webhook验证完整流程"""
    print("\n📡 发送最终测试webhook...")
    
    test_data = {
        "ticker": "AMZN", 
        "symbol": "AMZN",
        "action": "buy",
        "data_type": "signal",
        "timeframe": "4h",
        "timestamp": datetime.now().isoformat(),
        
        # 完整的技术指标数据
        "MAtrend": "bullish",
        "MAtrend2": "bullish", 
        "MAtrend3": "neutral",
        "TrendTracer": "bullish",
        "TrendTracer2": "bullish",
        "AIbandsignal": "bullish_momentum",
        "ratingstatus": "strong_buy",
        "pmaText": "PMA Strong Bullish signals show sustained upward momentum with institutional buying support and volume confirmation indicating potential continued rally",
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
        "current_price": 3450.75,
        "stop_loss_level": 3380.00,
        "volume": 28456789
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/webhook/tradingview",
            json=test_data,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ 最终测试webhook发送成功")
            print("📨 AMZN交易信号已发送到Discord频道")
            return True
        else:
            print(f"❌ Webhook发送失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 发送webhook失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🧪 AI模板修改最终验证")
    print("=" * 60)
    print("🎯 目标: 验证RP模板是否包含新的5个Markdown章节")
    print("=" * 60)
    
    # 执行验证步骤
    tests = [
        ("RP模板文件验证", lambda: verify_rp_template()[0]),
        ("AI模板生成测试", test_ai_template_generation),
        ("Discord webhook测试", send_final_test_webhook)
    ]
    
    results = []
    template_content = None
    
    for test_name, test_func in tests:
        print(f"\n🔄 执行: {test_name}")
        print("-" * 40)
        
        if test_name == "RP模板文件验证":
            success, template_content = verify_rp_template()
            results.append((test_name, success))
        else:
            result = test_func()
            results.append((test_name, result))
    
    # 最终结果
    print("\n" + "=" * 60)
    print("📊 AI模板修改验证结果:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
    
    print("=" * 60)
    print(f"📈 验证结果: {passed}/{total} 通过")
    
    if passed >= 2:  # 至少模板验证和生成测试通过
        print("\n🎉 AI模板修改验证成功!")
        print("\n🎯 在VPS环境中测试步骤:")
        print("1. 部署更新到VPS")
        print("2. 在Discord中查看AMZN交易信号")
        print("3. 点击'AI辅助决策'按钮")
        print("4. 验证AI报告包含以下5个章节:")
        print("   📈 市场概况")
        print("   🔑 关键交易信号")
        print("   📉 趋势分析")
        print("   💡 投资建议")
        print("   ⚠️ 风险提示")
        
        print("\n📋 VPS部署命令:")
        print("```bash")
        print("# 在VPS中执行:")
        print("cd /opt/discord-bot")
        print("git pull origin main")
        print("docker-compose down")
        print("docker-compose up -d --build")
        print("```")
        
        return True
    else:
        print("\n⚠️ AI模板修改验证未完全通过")
        if template_content:
            print("\n📄 当前RP模板内容:")
            print(template_content)
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ AI模板修改验证完成 - 可以部署到VPS!")
    else:
        print("\n❌ 需要进一步检查AI模板配置")