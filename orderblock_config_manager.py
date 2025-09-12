#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的OrderBlock配置管理器
重新实现，确保多频道正确加载
"""

import os
import logging
from typing import Dict, List, Optional

# 设置日志
logger = logging.getLogger(__name__)

class SimpleOrderBlockConfig:
    """简化的OrderBlock配置管理器"""
    
    def __init__(self, config_file: str = "/opt/discord-bot/orderblock_routes.conf"):
        self.config_file = config_file
        self.routes: Dict[str, List[int]] = {}
        self.default_channels: List[int] = []
        
        logger.info(f"初始化SimpleOrderBlockConfig，配置文件: {self.config_file}")
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        logger.info("开始加载配置文件...")
        
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"配置文件不存在: {self.config_file}")
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            logger.info(f"配置文件行数: {len(lines)}")
            
            # 清空现有配置
            self.routes.clear()
            self.default_channels.clear()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                logger.debug(f"处理第{line_num}行: {line}")
                
                # 解析配置行
                if '=' in line:
                    key, value_str = line.split('=', 1)
                    key = key.strip()
                    value_str = value_str.strip()
                    
                    if not key or not value_str:
                        logger.warning(f"第{line_num}行格式错误: {line}")
                        continue
                    
                    # 处理默认频道配置
                    if key == 'DEFAULT_CHANNEL':
                        self._parse_default_channels(value_str, line_num)
                        continue
                    
                    # 解析ticker路由频道ID列表
                    self._parse_ticker_routes(key, value_str, line_num)
            
            logger.info(f"配置加载完成:")
            logger.info(f"  默认频道: {self.default_channels}")
            logger.info(f"  路由数量: {len(self.routes)}")
            
            # 验证配置
            self._validate_config()
            
        except Exception as e:
            logger.error(f"加载配置文件时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _parse_default_channels(self, value_str: str, line_num: int) -> None:
        """解析默认频道配置"""
        logger.debug(f"解析默认频道: {value_str}")
        
        default_channel_ids = []
        for channel_str in value_str.split(','):
            channel_str = channel_str.strip()
            if channel_str:
                try:
                    channel_id = int(channel_str)
                    default_channel_ids.append(channel_id)
                    logger.debug(f"  添加默认频道: {channel_id}")
                except ValueError:
                    logger.warning(f"第{line_num}行无效的默认频道ID: {channel_str}")
        
        self.default_channels = default_channel_ids
        logger.info(f"加载默认频道: {self.default_channels}")
    
    def _parse_ticker_routes(self, ticker: str, value_str: str, line_num: int) -> None:
        """解析ticker路由配置"""
        logger.debug(f"解析ticker路由 {ticker}: {value_str}")
        
        channel_ids = []
        for channel_str in value_str.split(','):
            channel_str = channel_str.strip()
            if channel_str:
                try:
                    channel_id = int(channel_str)
                    channel_ids.append(channel_id)
                    logger.debug(f"  添加频道: {channel_id}")
                except ValueError:
                    logger.warning(f"第{line_num}行无效的频道ID: {channel_str}")
        
        if channel_ids:
            self.routes[ticker] = channel_ids
            logger.info(f"加载路由: {ticker} -> {channel_ids}")
        else:
            logger.warning(f"第{line_num}行没有有效频道ID: {line}")
    
    def _validate_config(self) -> None:
        """验证配置"""
        logger.info("开始验证配置...")
        
        # 验证默认频道
        if not self.default_channels:
            logger.warning("未配置默认频道")
        else:
            logger.info(f"默认频道验证通过: {len(self.default_channels)} 个")
        
        # 验证路由配置
        for ticker, channels in self.routes.items():
            if len(channels) == 0:
                logger.warning(f"ticker {ticker} 没有配置频道")
            elif len(channels) == 1:
                logger.warning(f"ticker {ticker} 只配置了1个频道: {channels}")
            else:
                logger.info(f"ticker {ticker} 配置了 {len(channels)} 个频道: {channels}")
        
        logger.info("配置验证完成")
    
    def get_channels_for_ticker(self, ticker: str) -> List[int]:
        """获取ticker对应的频道列表"""
        if ticker in self.routes:
            channels = self.routes[ticker]
            logger.info(f"找到ticker {ticker} 的频道映射: {channels}")
            return channels
        else:
            logger.info(f"未找到ticker {ticker} 的频道映射，使用默认频道: {self.default_channels}")
            return self.default_channels.copy()
    
    def get_all_routes(self) -> Dict[str, List[int]]:
        """获取所有路由配置"""
        return self.routes.copy()
    
    def get_default_channels(self) -> List[int]:
        """获取默认频道"""
        return self.default_channels.copy()
    
    def reload_config(self) -> None:
        """重新加载配置"""
        logger.info("重新加载配置文件...")
        self.load_config()

def test_simple_config():
    """测试简化配置管理器"""
    print("🧪 测试简化配置管理器")
    print("=" * 50)
    
    try:
        # 创建配置管理器实例
        config = SimpleOrderBlockConfig()
        
        print(f"✅ 配置管理器创建成功")
        print(f"📊 默认频道: {config.default_channels}")
        print(f"📊 路由数量: {len(config.routes)}")
        
        # 测试特定ticker
        test_tickers = ['AAPL', 'NYSE:AAPL', 'NASDAQ:TSLA']
        print(f"\n🧪 测试特定ticker:")
        for ticker in test_tickers:
            channels = config.get_channels_for_ticker(ticker)
            print(f"   {ticker}: {len(channels)} 个频道 -> {channels}")
        
        # 显示所有路由
        print(f"\n📋 所有路由:")
        for ticker, channels in list(config.routes.items())[:5]:  # 显示前5个
            print(f"   {ticker}: {len(channels)} 个频道 -> {channels}")
        
        if len(config.routes) > 5:
            print(f"   ... 还有 {len(config.routes) - 5} 个路由")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 测试配置管理器
    test_simple_config()
