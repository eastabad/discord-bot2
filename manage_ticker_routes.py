#!/usr/bin/env python3
"""
管理Ticker到频道的路由映射
"""

import logging
from orderblock_webhook import OrderBlockWebhookHandler

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_ticker_mapping(ticker: str, channel_id: int, description: str = None):
    """添加ticker到频道的映射"""
    try:
        # 创建一个模拟bot对象，只用于管理路由
        class MockBot:
            pass
        
        handler = OrderBlockWebhookHandler(MockBot())
        success = handler.add_ticker_channel_mapping(ticker, channel_id, description)
        
        if success:
            logger.info(f"✅ 成功添加映射: {ticker} -> 频道 {channel_id}")
            if description:
                logger.info(f"描述: {description}")
        else:
            logger.error(f"❌ 添加映射失败: {ticker}")
            
        return success
    except Exception as e:
        logger.error(f"❌ 添加映射异常: {e}")
        return False

def show_all_mappings():
    """显示所有ticker映射"""
    try:
        class MockBot:
            pass
        
        handler = OrderBlockWebhookHandler(MockBot())
        mappings = handler.get_all_mappings()
        
        logger.info("📋 当前Ticker到频道映射:")
        logger.info("-" * 50)
        for ticker, channel_id in mappings.items():
            logger.info(f"{ticker:<20} -> 频道 {channel_id}")
        logger.info("-" * 50)
        logger.info(f"总计: {len(mappings)} 个映射")
        
        return mappings
    except Exception as e:
        logger.error(f"❌ 获取映射异常: {e}")
        return {}

def main():
    """主函数 - 演示用法"""
    logger.info("🚀 Ticker路由管理工具")
    
    # 显示当前映射
    logger.info("\n1. 显示当前映射:")
    show_all_mappings()
    
    # 添加一些示例映射
    logger.info("\n2. 添加示例映射:")
    
    # 这里可以根据需要添加更多映射
    examples = [
        ("NASDAQ:TSLA", 1404532905916760125, "特斯拉股票Order Block信号"),
        ("NASDAQ:NVDA", 1404532905916760125, "英伟达股票Order Block信号"),
        ("NASDAQ:AAPL", 1404532905916760125, "苹果股票Order Block信号"),
    ]
    
    for ticker, channel_id, desc in examples:
        add_ticker_mapping(ticker, channel_id, desc)
    
    # 显示更新后的映射
    logger.info("\n3. 更新后的映射:")
    show_all_mappings()

if __name__ == "__main__":
    main()