#!/usr/bin/env python3
"""
Order Block专用Webhook系统
接收OB信号并根据ticker路由到对应频道
"""

import json
import logging
import discord
from datetime import datetime
import pytz
from typing import Dict, Optional, List
import os
import io
from orderblock_config_manager import SimpleOrderBlockConfig
from chart_service import ChartService

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 移除数据库模型，改用配置文件管理

class OrderBlockWebhookHandler:
    """Order Block Webhook处理器"""
    
    def __init__(self, bot, config=None):
        self.bot = bot
        self.logger = logging.getLogger(f"{__name__}.OrderBlockWebhookHandler")
        
        # 使用配置文件管理器
        self.config_manager = SimpleOrderBlockConfig("/app/orderblock_routes.conf")
        
        # 初始化图表服务
        self.chart_service = ChartService(config) if config else None
        if not self.chart_service:
            self.logger.warning("图表服务未初始化，Order Block信号将不包含图表")
        
        # 硬编码备用默认频道ID（如果配置文件中未设置）
        self.fallback_default_channel_id = 1404532905916760125
    
    def get_channels_for_ticker(self, ticker: str) -> List[int]:
        """获取ticker对应的所有频道ID列表，支持交易所前缀匹配"""
        try:
            # 重新加载配置以获取最新数据
            self.config_manager.reload_config()
            
            # 先尝试完整ticker匹配
            channel_ids = self.config_manager.get_channels_for_ticker(ticker)
            
            if channel_ids:
                self.logger.info(f"找到完整ticker映射: {ticker} -> {channel_ids}")
                return channel_ids
            
            # 如果没有找到，尝试提取不带交易所前缀的ticker
            # 例如: BATS:META -> META, NYSE:AAPL -> AAPL
            if ':' in ticker:
                base_ticker = ticker.split(':', 1)[1]
                channel_ids = self.config_manager.get_channels_for_ticker(base_ticker)
                
                if channel_ids:
                    self.logger.info(f"找到基础ticker映射: {ticker} -> {base_ticker} -> {channel_ids}")
                    return channel_ids
            
            # 如果还是没有配置，使用默认频道
            default_channels = self.config_manager.get_default_channels()
            if default_channels:
                self.logger.warning(f"未找到ticker {ticker} 的频道映射，使用配置的默认频道: {default_channels}")
                return default_channels
            else:
                self.logger.warning(f"未找到ticker {ticker} 的频道映射，使用备用默认频道: {self.fallback_default_channel_id}")
                return [self.fallback_default_channel_id]
            
        except Exception as e:
            self.logger.error(f"获取ticker映射失败: {e}")
            default_channel = self.config_manager.get_default_channel()
            if default_channel:
                return [default_channel]
            else:
                return [self.fallback_default_channel_id]
    
    def set_ticker_channel_mappings(self, ticker: str, channel_ids: List[int], description: str = None) -> bool:
        """设置ticker到多个频道的映射"""
        try:
            # 使用配置文件管理器设置映射
            self.config_manager.set_ticker_channels(ticker, channel_ids)
            self.config_manager.save_config()
            
            self.logger.info(f"设置ticker映射: {ticker} -> {channel_ids}")
            return True
            
        except Exception as e:
            self.logger.error(f"设置ticker映射失败: {e}")
            return False
    
    def add_ticker_channel_mapping(self, ticker: str, channel_id: int, description: str = None) -> bool:
        """添加ticker到单个频道的映射"""
        try:
            # 使用配置文件管理器添加映射
            self.config_manager.add_channel_to_ticker(ticker, channel_id)
            self.config_manager.save_config()
            
            self.logger.info(f"添加ticker映射: {ticker} -> {channel_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加ticker映射失败: {e}")
            return False
    
    def get_all_mappings(self) -> Dict[str, List[int]]:
        """获取所有ticker映射"""
        try:
            # 重新加载配置
            self.config_manager.reload_config()
            
            # 获取所有路由映射
            return self.config_manager.get_routes()
            
        except Exception as e:
            self.logger.error(f"获取所有映射失败: {e}")
            return {}
    
    async def process_orderblock_signal(self, data: dict) -> bool:
        """处理Order Block信号"""
        try:
            # 解析数据
            ticker = data.get('ticker', '')
            timeframe = data.get('timeframe', '')
            event = data.get('event', '')
            price = data.get('price', '')
            bullish_ob = data.get('bullish_ob', 'N/A')
            bearish_ob = data.get('bearish_ob', 'N/A')
            poc_summary = data.get('poc_summary', 'N/A')
            
            if not ticker or not event:
                self.logger.warning("Order Block信号缺少必要字段")
                return False
            
            chart_filename = None
            
            if self.chart_service and ticker and timeframe:
                try:
                    self.logger.info(f"正在获取 {ticker} {timeframe} 的OB图表...")
                    chart_bytes = await self.chart_service.get_ob_chart(ticker, timeframe)
                    
                    if chart_bytes:
                        chart_image = io.BytesIO(chart_bytes)
                        chart_filename = f"ob_chart_{ticker}_{timeframe}.png"
                        self.logger.info(f"成功获取 {ticker} {timeframe} 的OB图表")
                    else:
                        self.logger.warning(f"未能获取 {ticker} {timeframe} 的OB图表")
                        
                except Exception as chart_error:
                    self.logger.error(f"获取OB图表失败: {chart_error}")
            
            # 创建Discord embed
            embed = self.create_orderblock_embed(
                ticker, timeframe, event, price, bullish_ob, bearish_ob, poc_summary
            )
            
            # 如果有图表，设置图片
            # 然后获取目标频道列表
            channel_ids = self.get_channels_for_ticker(ticker)
            if not channel_ids:
                self.logger.error(f"未找到ticker {ticker}的频道映射")
                return False
            if chart_image and chart_filename:
                # 使用正确的Discord embed图片设置方式
                # 确保图片和信息在同一个消息中正确显示
                embed.set_image(url=f"attachment://{chart_filename}")

            
            # 发送到所有映射的频道
            success_count = 0
            for channel_id in channel_ids:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if not channel:
                        self.logger.error(f"无法找到频道 {channel_id}")
                        continue
                    
                    # 发送消息（带图表或不带图表）
                    if chart_image and chart_filename:
                        try:
                            # 重置BytesIO position
                            chart_image.seek(0)
                            
                            # 创建文件对象
                            file = discord.File(chart_image, filename=chart_filename)
                            
                            # 确保embed中的图片URL正确
                            # 重新设置图片URL，确保与文件名完全匹配
                            embed.set_image(url=f"attachment://{chart_filename}")
                            
                            # 发送embed和文件
                            await channel.send(embed=embed, file=file)
                            self.logger.info(f"Order Block信号和图表已发送到频道 {channel_id}: {ticker} - {event}")
                            
                        except Exception as send_error:
                            self.logger.error(f"发送带图表的消息失败: {send_error}")
                            # 回退到只发送文本
                            await channel.send(embed=embed)
                            self.logger.info(f"Order Block信号（无图表）已发送到频道 {channel_id}: {ticker} - {event}")
                    else:
                        await channel.send(embed=embed)
                        self.logger.info(f"Order Block信号已发送到频道 {channel_id}: {ticker} - {event}")
                    
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"发送Order Block信号到频道 {channel_id} 失败: {e}")
            
            if success_count > 0:
                self.logger.info(f"Order Block信号成功发送到 {success_count}/{len(channel_ids)} 个频道")
                return True
            else:
                self.logger.error(f"Order Block信号发送失败，所有频道都无法访问")
                return False
            
        except Exception as e:
            self.logger.error(f"处理Order Block信号失败: {e}")
            return False
    
    def create_orderblock_embed(self, ticker: str, timeframe: str, event: str, 
                               price: str, bullish_ob: str, bearish_ob: str, poc_summary: str) -> discord.Embed:
        """创建Order Block Discord embed"""
        
        # 根据事件类型选择颜色和emoji
        color_map = {
            "New Bullish OB Formed": 0x00ff00,  # 绿色
            "New Bearish OB Formed": 0xff0000,  # 红色
            "Price Entering Bullish OB": 0x00aa00,  # 深绿色
            "Price Entering Bearish OB": 0xaa0000,  # 深红色
        }
        
        emoji_map = {
            "New Bullish OB Formed": "🟢",
            "New Bearish OB Formed": "🔴", 
            "Price Entering Bullish OB": "📈",
            "Price Entering Bearish OB": "📉"
        }
        
        color = color_map.get(event, 0x9932cc)  # 默认紫色
        emoji = emoji_map.get(event, "🔲")
        
        # 获取美国东部时间
        et_tz = pytz.timezone('US/Eastern')
        current_et = datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建embed
        embed = discord.Embed(
            title=f"{emoji} {ticker} Order Block Alert",
            description=f"**{event}**\nTimeframe: {timeframe}",
            color=color,
            timestamp=datetime.now()
        )
        
        # 添加价格信息
        embed.add_field(
            name="💰 Current Price",
            value=f"${price}",
            inline=True
        )
        
        # 添加OB信息
        if bullish_ob != "N/A":
            embed.add_field(
                name="🟢 Bullish Order Block",
                value=bullish_ob,
                inline=True
            )
        
        if bearish_ob != "N/A":
            embed.add_field(
                name="🔴 Bearish Order Block", 
                value=bearish_ob,
                inline=True
            )
        
        # 添加POC信息
        if poc_summary != "N/A":
            # 将POC信息分成三行，让排版更美观
            poc_lines = poc_summary.split('; ')
            if len(poc_lines) >= 6:
                # 解析POC信息
                poc_dict = {}
                for line in poc_lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        poc_dict[key.strip()] = value.strip()
                
                # 构建三行显示格式，标签加粗
                daily_line = f"**Daily:** {poc_dict.get('Daily POC', 'N/A')} | **Prev Daily:** {poc_dict.get('Prev DailyPOC', 'N/A')}"
                weekly_line = f"**Weekly:** {poc_dict.get('Weekly POC', 'N/A')} | **Prev Weekly:** {poc_dict.get('Prev Weekly POC', 'N/A')}"
                monthly_line = f"**Monthly:** {poc_dict.get('Monthly POC', 'N/A')} | **Prev Monthly:** {poc_dict.get('Prev Monthly POC', 'N/A')}"
                
                embed.add_field(
                    name="🎯 POC Summary",
                    value=f"{daily_line}\n{weekly_line}\n{monthly_line}",
                    inline=False
                )
            else:
                # 如果格式不标准，直接显示
                embed.add_field(
                    name="🎯 POC Summary",
                    value=poc_summary,
                    inline=False
                )
        
        # 添加时间信息
        embed.add_field(
            name="🕐 Time",
            value=f"US Eastern Time {current_et}",
            inline=False
        )
        
        embed.set_footer(text="TD AIassistant Order Block MoneyFlow system")
        
        return embed
    
    def get_all_ticker_mappings(self) -> List[Dict]:
        """获取所有ticker映射"""
        try:
            # 重新加载配置
            self.config_manager.reload_config()
            
            result = []
            routes = self.config_manager.get_routes()
            
            for ticker, channel_ids in routes.items():
                for channel_id in channel_ids:
                    result.append({
                        'ticker': ticker,
                        'channel_id': channel_id,
                        'description': f'{ticker} 路由配置',
                        'created_at': None  # 配置文件不保存创建时间
                    })
            
            return result
            
        except Exception as e:
            self.logger.error(f"获取所有映射失败: {e}")
            return []
    
    def remove_ticker_mappings(self, ticker: str) -> bool:
        """删除ticker的所有映射"""
        try:
            # 使用配置文件管理器删除ticker
            success = self.config_manager.remove_ticker(ticker)
            if success:
                self.config_manager.save_config()
                self.logger.info(f"删除ticker {ticker}的映射")
            else:
                self.logger.warning(f"ticker {ticker} 不存在")
            
            return success
            
        except Exception as e:
            self.logger.error(f"删除ticker映射失败: {e}")
            return False

def init_config():
    """初始化配置文件"""
    try:
        manager = SimpleOrderBlockConfig("/opt/discord-bot/orderblock_routes.conf")
        logger.info("Order Block配置文件系统初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"初始化配置文件失败: {e}")
        return False

if __name__ == "__main__":
    # 初始化配置文件
    init_config()
    print("Order Block Webhook系统初始化完成")