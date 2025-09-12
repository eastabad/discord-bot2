#!/usr/bin/env python3
"""
创建个人webhook并发送MSTR测试信号
"""
import requests
import json
import uuid
import sqlite3
import os
from datetime import datetime

class PersonalWebhookManager:
    def __init__(self, user_id):
        self.user_id = user_id
        self.base_url = "http://localhost:5000"
        self.secret = str(uuid.uuid4())[:16]
        self.webhook_url = f"{self.base_url}/webhook/tradingview/{self.user_id}/{self.secret}"
        
    def register_webhook_in_db(self):
        """在数据库中注册webhook"""
        try:
            # 使用环境变量中的数据库连接
            import os
            database_url = os.environ.get('DATABASE_URL')
            
            if database_url:
                # PostgreSQL连接
                import psycopg2
                from urllib.parse import urlparse
                
                parsed_url = urlparse(database_url)
                conn = psycopg2.connect(
                    host=parsed_url.hostname,
                    port=parsed_url.port,
                    database=parsed_url.path[1:],
                    user=parsed_url.username,
                    password=parsed_url.password
                )
                
                cursor = conn.cursor()
                
                # 检查表是否存在，如果不存在则创建
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS personal_webhooks (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        secret VARCHAR(50) NOT NULL,
                        webhook_url TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT true,
                        UNIQUE(user_id, secret)
                    )
                """)
                
                # 插入webhook记录
                cursor.execute("""
                    INSERT INTO personal_webhooks (user_id, secret, webhook_url) 
                    VALUES (%s, %s, %s) 
                    ON CONFLICT (user_id, secret) DO UPDATE SET 
                    webhook_url = EXCLUDED.webhook_url,
                    created_at = CURRENT_TIMESTAMP
                """, (self.user_id, self.secret, self.webhook_url))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                print("✅ Webhook已注册到数据库")
                return True
                
        except Exception as e:
            print(f"⚠️ 数据库注册失败 (继续测试): {e}")
            return False
    
    def create_mstr_test_signal(self):
        """创建MSTR测试信号数据"""
        return {
            # 基础信息
            "ticker": "MSTR",
            "symbol": "MSTR",
            "action": "sell",
            "quantity": 120,
            "timeframe": "15m",
            "timestamp": datetime.now().isoformat(),
            
            # 原始data字段映射到顶级
            "CVDsignal": "cvdBelowMA",
            "choppiness": "46.4125643135",
            "adxValue": "35.341643694", 
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
            "trend_change_volatility_stop": "336.46",
            "AIbandsignal": "red downtrend",
            "HTFwave_signal": "Bearish",
            "wavemarket_state": "Short Strong",
            "ewotrend_state": "Strong Bearish",
            
            # 价格信息
            "current_price": 330.25,
            "stop_price": 332.72,
            "limit_price": 322.79,
            
            # 额外信息
            "indicator": "WaveMatrix shortStrongSignal",
            "oscrating": 90,
            "trendrating": 100,
            "risk": 1,
            
            # 兼容字段
            "body": {
                "symbol": "MSTR",
                "action": "sell",
                "quantity": 120,
                "CVDsignal": "cvdBelowMA",
                "choppiness": "46.4125643135",
                "adxValue": "35.341643694",
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
                "trend_change_volatility_stop": "336.46",
                "AIbandsignal": "red downtrend",
                "HTFwave_signal": "Bearish",
                "wavemarket_state": "Short Strong",
                "ewotrend_state": "Strong Bearish",
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
    
    def send_personal_webhook_test(self):
        """发送个人webhook测试"""
        print("🔗 个人webhook信息:")
        print(f"👤 用户ID: {self.user_id}")
        print(f"🔐 Secret: {self.secret}")
        print(f"📡 Webhook URL: {self.webhook_url}")
        
        # 注册到数据库
        self.register_webhook_in_db()
        
        # 创建测试信号
        test_signal = self.create_mstr_test_signal()
        
        print(f"\n📊 MSTR测试信号:")
        print(f"📈 股票: {test_signal['ticker']}")
        print(f"🎯 操作: {test_signal['action'].upper()}")
        print(f"📦 数量: {test_signal['quantity']}")
        print(f"💰 当前价: ${test_signal['current_price']}")
        print(f"🛡️ 止损: ${test_signal['stop_price']}")
        print(f"🎯 止盈: ${test_signal['limit_price']}")
        print(f"📉 中枢趋势: {test_signal['center_trend']}")
        print(f"🌊 波浪状态: {test_signal['wavemarket_state']}")
        print(f"🤖 AI波段: {test_signal['AIbandsignal']}")
        
        # 发送webhook
        print(f"\n📡 发送到个人webhook...")
        
        try:
            response = requests.post(
                self.webhook_url,
                json=test_signal,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 个人webhook测试成功!")
                print(f"📨 MSTR信号已发送到Discord私信")
                
                return True, result
            else:
                print(f"❌ Webhook发送失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                # 尝试解决常见问题
                if response.status_code == 400:
                    print("\n🔧 尝试简化数据格式...")
                    simplified_signal = {
                        "ticker": "MSTR",
                        "action": "sell", 
                        "quantity": 120,
                        "body": {
                            "symbol": "MSTR",
                            "action": "sell",
                            "center_trend": "Strong Bearish",
                            "wavemarket_state": "Short Strong",
                            "AIbandsignal": "red downtrend",
                            "pmaText": "PMA Bearish"
                        }
                    }
                    
                    response2 = requests.post(
                        self.webhook_url,
                        json=simplified_signal,
                        headers={'Content-Type': 'application/json'},
                        timeout=20
                    )
                    
                    if response2.status_code == 200:
                        print("✅ 简化版本发送成功!")
                        return True, response2.json()
                
                return False, None
                
        except Exception as e:
            print(f"❌ 发送异常: {e}")
            return False, None

def main():
    """主函数"""
    print("🧪 个人webhook创建和MSTR测试")
    print("=" * 70)
    
    user_id = "1145170623354638418"
    
    # 创建webhook管理器
    webhook_manager = PersonalWebhookManager(user_id)
    
    # 执行测试
    success, result = webhook_manager.send_personal_webhook_test()
    
    print("\n" + "=" * 70)
    
    if success:
        print("🎉 个人webhook和MSTR测试完成!")
        print("\n🎯 验证步骤:")
        print("1. 检查Discord私信收到MSTR卖出信号")
        print("2. 点击'AI辅助决策'按钮")
        print("3. 验证AI报告包含新的5个章节:")
        print("   📈 市场概况")
        print("   🔑 关键交易信号")
        print("   📉 趋势分析")
        print("   💡 投资建议")
        print("   ⚠️ 风险提示")
        print("4. 检查bearish信号解析")
        print("5. 验证价格信息显示")
        
        print(f"\n📋 保存webhook信息供未来使用:")
        print(f"URL: {webhook_manager.webhook_url}")
        print(f"Secret: {webhook_manager.secret}")
        
        return True
    else:
        print("❌ 个人webhook测试失败")
        print("💡 可能需要检查PersonalWebhookService的验证逻辑")
        return False

if __name__ == "__main__":
    main()