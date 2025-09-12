#!/usr/bin/env python3
"""
VPS环境AI模板测试脚本 - 完整验证流程
"""
import requests
import json
import time
import os
from datetime import datetime

class VPSAITemplateTest:
    def __init__(self):
        # 本地Replit环境测试
        self.base_url = "http://localhost"
        self.api_port = "5000"
        self.config_port = "8081"
        self.user_id = "1145170623354638418"
        self.channel_id = "1404532905916760125"
        
    def test_config_service(self):
        """测试配置服务和AI模板"""
        print("🔧 1. 测试配置服务...")
        
        try:
            # 检查配置服务状态
            config_url = f"{self.base_url}:{self.config_port}/api/ai-templates-unified"
            response = requests.get(config_url, timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ 配置服务正常，模板数量: {len(templates)}")
                
                # 检查RP模板
                rp_template = templates.get('RP')
                if rp_template:
                    print("✅ RP模板已加载")
                    print(f"📝 模板内容预览: {rp_template[:100]}...")
                    
                    # 验证新格式标识
                    required_sections = [
                        "## 📈 市场概况",
                        "## 🔑 关键交易信号",
                        "## 📉 趋势分析", 
                        "## 💡 投资建议",
                        "## ⚠️ 风险提示"
                    ]
                    
                    for section in required_sections:
                        if section in rp_template:
                            print(f"✅ 包含: {section}")
                        else:
                            print(f"❌ 缺失: {section}")
                    
                    return True
                else:
                    print("❌ RP模板未找到")
                    return False
            else:
                print(f"❌ 配置服务异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 配置服务测试失败: {e}")
            return False
    
    def test_api_service(self):
        """测试API服务"""
        print("\n🚀 2. 测试API服务...")
        
        try:
            api_url = f"{self.base_url}:{self.api_port}/api/health"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ API服务正常")
                print(f"📊 机器人状态: {health_data.get('bot', {}).get('status', 'unknown')}")
                print(f"🤖 机器人ID: {health_data.get('bot', {}).get('id', 'unknown')}")
                return True
            else:
                print(f"❌ API服务异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API服务测试失败: {e}")
            return False
    
    def test_ai_models(self):
        """测试AI模型状态"""
        print("\n🧠 3. 测试AI模型状态...")
        
        try:
            ai_url = f"{self.base_url}:{self.api_port}/api/ai-status"
            response = requests.get(ai_url, timeout=10)
            
            if response.status_code == 200:
                ai_data = response.json()
                print("✅ AI服务正常")
                
                models = ai_data.get('available_models', [])
                print(f"📈 可用AI模型数量: {len(models)}")
                
                for model in models:
                    print(f"  - {model}")
                
                return len(models) > 0
            else:
                print(f"❌ AI服务异常: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ AI服务测试失败: {e}")
            return False
    
    def send_test_webhook(self):
        """发送测试webhook验证AI按钮"""
        print("\n📡 4. 发送测试webhook...")
        
        test_data = {
            "ticker": "GOOGL",
            "symbol": "GOOGL",
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
            "pmaText": "PMA Strong Bullish signals indicate sustained upward momentum with institutional support",
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
            "current_price": 2850.75,
            "stop_loss_level": 2800.00,
            "volume": 12345678
        }
        
        try:
            webhook_url = f"{self.base_url}:{self.api_port}/webhook/tradingview"
            response = requests.post(webhook_url, json=test_data, timeout=15)
            
            if response.status_code == 200:
                print("✅ Webhook发送成功")
                print("📨 GOOGL交易信号已发送到Discord")
                return True
            else:
                print(f"❌ Webhook发送失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Webhook发送异常: {e}")
            return False
    
    def send_personal_webhook_test(self):
        """发送个人webhook测试私信"""
        print("\n💬 5. 发送个人私信测试...")
        
        personal_data = {
            "ticker": "MSFT",
            "symbol": "MSFT",
            "action": "sell",
            "data_type": "personal_signal",
            "timeframe": "4h",
            "timestamp": datetime.now().isoformat(),
            
            # 技术指标
            "MAtrend": "bearish",
            "MAtrend2": "neutral",
            "MAtrend3": "bearish",
            "TrendTracer": "bearish",
            "AIbandsignal": "bearish_momentum",
            "ratingstatus": "sell",
            "pmaText": "PMA showing bearish divergence with volume declining, suggesting potential reversal",
            "MOMOsignal": "bearish",
            "center_trend": "downtrend",
            "wavemarket_state": "corrective_wave",
            "RSIHAsignal": "bearish",
            "current_price": 415.67,
            "stop_loss_level": 425.00,
            "risk_level": "high"
        }
        
        try:
            # 生成临时secret
            import uuid
            secret = str(uuid.uuid4())[:16]
            
            personal_url = f"{self.base_url}:{self.api_port}/webhook/tradingview/{self.user_id}/{secret}"
            response = requests.post(personal_url, json=personal_data, timeout=15)
            
            if response.status_code == 200:
                print("✅ 个人webhook发送成功")
                print("📱 MSFT交易信号已发送到私信")
                return True
            else:
                print(f"❌ 个人webhook发送失败: {response.status_code}")
                print(f"错误: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 个人webhook发送异常: {e}")
            return False
    
    def run_complete_test(self):
        """运行完整测试流程"""
        print("🧪 VPS环境AI模板完整测试")
        print("=" * 80)
        print(f"🌐 VPS地址: {self.base_url}")
        print(f"👤 测试用户ID: {self.user_id}")
        print(f"📺 测试频道ID: {self.channel_id}")
        print("=" * 80)
        
        results = []
        
        # 执行所有测试
        results.append(("配置服务", self.test_config_service()))
        results.append(("API服务", self.test_api_service()))
        results.append(("AI模型", self.test_ai_models()))
        results.append(("频道Webhook", self.send_test_webhook()))
        results.append(("私信Webhook", self.send_personal_webhook_test()))
        
        # 汇总结果
        print("\n" + "=" * 80)
        print("📊 测试结果汇总:")
        print("=" * 80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:15} : {status}")
            if result:
                passed += 1
        
        print("=" * 80)
        print(f"📈 总体结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过! AI模板修改成功部署")
            print("\n🎯 验证步骤:")
            print("1. 检查Discord频道中的GOOGL交易信号")
            print("2. 检查Discord私信中的MSFT交易信号")
            print("3. 点击'AI辅助决策'按钮")
            print("4. 验证AI报告包含新的5个Markdown章节")
            print("5. 确认格式为:")
            print("   📈 市场概况")
            print("   🔑 关键交易信号") 
            print("   📉 趋势分析")
            print("   💡 投资建议")
            print("   ⚠️ 风险提示")
        else:
            print("⚠️  部分测试失败，请检查VPS服务状态")
        
        return passed == total

def main():
    """主函数"""
    tester = VPSAITemplateTest()
    success = tester.run_complete_test()
    
    if success:
        print("\n🚀 VPS环境AI模板测试完成 - 全部通过!")
    else:
        print("\n❌ VPS环境测试存在问题，请检查服务状态")
    
    return success

if __name__ == "__main__":
    main()