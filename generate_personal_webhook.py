#!/usr/bin/env python3
"""
为用户生成专用webhook并发送测试交易信号
"""
import requests
import json
import uuid
from datetime import datetime

class PersonalWebhookGenerator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.base_url = "http://localhost:5000"
        self.secret = str(uuid.uuid4())[:16]  # 生成16位随机secret
        self.webhook_url = f"{self.base_url}/webhook/tradingview/{self.user_id}/{self.secret}"
    
    def generate_webhook_info(self):
        """生成webhook信息"""
        webhook_info = {
            "user_id": self.user_id,
            "secret": self.secret,
            "webhook_url": self.webhook_url,
            "generated_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        print("🔗 个人webhook已生成:")
        print(f"👤 用户ID: {self.user_id}")
        print(f"🔐 Secret: {self.secret}")
        print(f"📡 Webhook URL: {self.webhook_url}")
        print(f"⏰ 生成时间: {webhook_info['generated_at']}")
        
        return webhook_info
    
    def send_test_signal(self, test_data):
        """发送测试交易信号"""
        print(f"\n📡 发送测试信号到个人webhook...")
        print(f"📊 测试数据: {test_data['ticker']} {test_data['action']}")
        
        try:
            response = requests.post(
                self.webhook_url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            print(f"📈 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 个人webhook测试成功!")
                print(f"📨 信号已发送到Discord私信")
                print(f"⏱️ 处理时间: {result.get('timestamp', 'N/A')}")
                return True, result
            else:
                print(f"❌ Webhook发送失败: {response.status_code}")
                print(f"错误详情: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 发送异常: {e}")
            return False, None

def main():
    """主函数"""
    print("🔗 个人webhook生成器")
    print("=" * 60)
    
    # 用户ID
    user_id = "1145170623354638418"
    
    # 创建webhook生成器
    generator = PersonalWebhookGenerator(user_id)
    
    # 生成webhook信息
    webhook_info = generator.generate_webhook_info()
    
    # 准备测试交易数据
    test_trading_signal = {
        "ticker": "MSTR",
        "symbol": "MSTR",  # 添加symbol字段确保解析成功
        "action": "sell",
        "quantity": 120,
        "data_type": "personal_signal",
        "timeframe": "15m",
        "timestamp": datetime.now().isoformat(),
        
        # 从data字段中提取的技术指标
        "CVDsignal": "cvdBelowMA",
        "choppiness": 46.4125643135,
        "adxValue": 35.341643694,
        "BBPsignal": "bullpower",
        "RSIHAsignal": "BearishHA", 
        "SQZsignal": "no squeeze",
        "choppingrange_signal": "no chopping",
        "rsi_state_trend": "Bearish",
        "center_trend": "Strong Bearish",
        "adaptive_timeframe_1": "60",
        "adaptive_timeframe_2": "240",
        "MAtrend": "-1",
        "MAtrend_timeframe1": "-1", 
        "MAtrend_timeframe2": "1",
        "MOMOsignal": "bearishmomo",
        "Middle_smooth_trend": "Bearish +",
        "TrendTracersignal": "-1",
        "TrendTracerHTF": "-1",
        "pmaText": "PMA Bearish",
        "trend_change_volatility_stop": 336.46,
        "AIbandsignal": "red downtrend",
        "HTFwave_signal": "Bearish",
        "wavemarket_state": "Short Strong",
        "ewotrend_state": "Strong Bearish",
        
        # 价格信息
        "current_price": 330.25,  # 估算当前价格
        "stop_loss_price": 332.72,
        "take_profit_price": 322.79,
        
        # 额外信息
        "indicator": "WaveMatrix shortStrongSignal",
        "oscrating": 90,
        "trendrating": 100,
        "risk": 1,
        
        # 个人信号标识
        "signal_source": "personal_webhook",
        "confidence_level": "high"
    }
    
    print("\n" + "=" * 60)
    print("📊 测试交易信号详情:")
    print("=" * 60)
    print(f"股票代码: {test_trading_signal['ticker']}")
    print(f"操作类型: {test_trading_signal['action'].upper()}")
    print(f"数量: {test_trading_signal['quantity']}")
    print(f"当前价格: ${test_trading_signal['current_price']}")
    print(f"止损价格: ${test_trading_signal['stop_loss_price']}")
    print(f"止盈价格: ${test_trading_signal['take_profit_price']}")
    print(f"风险等级: {test_trading_signal['risk']}")
    print(f"中枢趋势: {test_trading_signal['center_trend']}")
    print(f"波浪状态: {test_trading_signal['wavemarket_state']}")
    print(f"AI波段: {test_trading_signal['AIbandsignal']}")
    
    # 发送测试信号
    print("\n" + "=" * 60)
    success, result = generator.send_test_signal(test_trading_signal)
    
    if success:
        print("\n🎉 个人webhook测试完成!")
        print("\n🎯 验证步骤:")
        print("1. 检查Discord私信中的MSTR交易信号")
        print("2. 点击'AI辅助决策'按钮")
        print("3. 验证AI报告包含新的5个Markdown章节:")
        print("   📈 市场概况")
        print("   🔑 关键交易信号")
        print("   📉 趋势分析") 
        print("   💡 投资建议")
        print("   ⚠️ 风险提示")
        print("4. 检查bearish信号的解析是否正确")
        print("5. 验证止损止盈价格是否显示")
        
        print(f"\n📋 保存此webhook信息:")
        print(f"Webhook URL: {generator.webhook_url}")
        print(f"Secret: {generator.secret}")
        print("此URL可用于TradingView发送实际交易信号")
        
    else:
        print("\n❌ 个人webhook测试失败")
        print("请检查服务状态或数据格式")
    
    return success

if __name__ == "__main__":
    main()