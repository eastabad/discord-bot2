#!/usr/bin/env python3
"""
完整版Discord机器人 + API服务器
包含TradingView webhook接收和报告生成功能
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from aiohttp import web

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # 减少discord.py的调试输出
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
    
    # 启用channel_cleaner的详细日志
    logging.getLogger('channel_cleaner').setLevel(logging.DEBUG)

# Health server is now integrated into the API server

async def main():
    """主函数 - Discord机器人 + API服务器"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 启动完整版TDbot-tradingview (Discord + API)...")
        
        # 验证必需的环境变量
        required_vars = ['DISCORD_TOKEN', 'GEMINI_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
            sys.exit(1)
        
        logger.info("✅ 环境变量验证通过")
        
        # 导入并创建机器人
        from bot import DiscordBot
        from config import Config
        from api_server import DiscordAPIServer
        
        # 加载配置
        config = Config()
        logger.info("✅ 配置加载完成")
        
        # 创建机器人实例
        bot = DiscordBot(config)
        logger.info("✅ Discord机器人初始化完成")
        
        # 创建API服务器（传递配置）
        api_server = DiscordAPIServer(bot, config)
        logger.info("✅ API服务器初始化完成")
        
        # 启动API服务器（包含健康检查和TradingView webhook）
        api_runner = await api_server.start_server('0.0.0.0', 5000)
        logger.info("✅ API服务器已启动在端口5000")
        
        logger.info("🤖 连接Discord机器人...")
        
        # 确保discord_token存在
        if not config.discord_token:
            logger.error("❌ Discord token 为空")
            sys.exit(1)
        
        # 启动Discord机器人
        await bot.start(config.discord_token)
        
    except KeyboardInterrupt:
        logger.info("⏹️ 收到停止信号，正在关闭...")
    except Exception as e:
        logger.error(f"❌ 启动错误: {e}")
        raise
    finally:
        logger.info("🔚 机器人已关闭")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        sys.exit(1)