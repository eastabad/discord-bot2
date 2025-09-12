"""
频道清理服务模块
自动删除监控频道中的无用消息，保持频道整洁
"""

import asyncio
import logging
import discord
from datetime import datetime, timedelta
import re
from typing import List, Set

class ChannelCleaner:
    """频道清理服务类"""
    
    def __init__(self, bot, config):
        """初始化频道清理服务"""
        self.bot = bot
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 无用消息模式匹配 - 更积极的清理策略
        self.useless_patterns = [
            r'^(测试|test|Test|TEST)$',     # 测试消息
            r'^(hello|hi|你好|Hi|Hello)$',  # 简单问候
            r'^(ok|好的|收到|OK)$',         # 简单确认
            r'^(谢谢|thanks?|thx|Thank)$',  # 简单感谢
            r'^\d+$',                       # 纯数字
            r'^[.,，。!！?？]+$',           # 纯标点符号
            r'^[a-zA-Z]{1,3}$',            # 短字母
            r'spam.*',                      # 垃圾消息
            r'刷屏',                        # 刷屏消息
            r'无聊',                        # 无聊消息
            r'^哈{2,}',                     # 连续哈哈
            r'^呵{2,}',                     # 连续呵呵
            r'^啊{2,}',                     # 连续啊啊
            r'^(lol|lmao|rofl|LOL)+$',      # 网络用语
            r'^\+1$',                       # 单纯的+1
            r'^顶$',                        # 单纯的顶
            r'^沙发$',                      # 单纯的沙发
            r'^(first|第一|First)$',        # 单纯的第一
            r'^[😀-🙏]+$',                  # 纯表情符号
            r'^(好|坏|是|不|yes|no|YES|NO)$', # 单字回复
            r'^(嗯|呃|额|哦|噢|Hmm|hmm)$',   # 语气词
            r'^(。|！|？|\.|!|\?)$',         # 单个标点
        ]
        
        # 保留有用消息模式
        self.useful_patterns = [
            r'[A-Z]{2,5}[,，]\s*\d+[smhdwMy]',     # 股票命令格式 (AAPL, 1d)
            r'CT\s+[A-Z]{2,5}',                    # CT命令格式
            r'OB\s+[A-Z]{2,5}',                    # OB命令格式
            r'RP\s+[A-Z]{2,5}',                    # RP命令格式
            r'预测.*趋势',                         # 预测请求
            r'分析.*图表',                         # 图表分析请求
            r'!vip',                               # VIP管理命令
            r'!quota',                             # 配额查询命令
            r'!help',                              # 帮助命令
            r'!webhook',                           # Webhook命令
            r'!cleanup',                           # 清理命令
            r'!status',                            # 状态命令
            r'@',                                  # 提及消息
            r'https?://',                          # 包含链接
            r'问题',                               # 问题咨询
            r'疑问',                               # 疑问询问
            r'怎么',                               # 操作询问
            r'如何',                               # 方法询问
            r'为什么',                             # 原因询问
            r'什么时候',                           # 时间询问
            r'哪里',                               # 地点询问
            r'谁',                                 # 人物询问
            r'能否',                               # 请求询问
            r'可以',                               # 可能性询问
            r'会不会',                             # 可能性询问
            r'建议',                               # 建议请求
            r'推荐',                               # 推荐请求
            r'意见',                               # 意见征求
            r'看法',                               # 看法征求
        ]
        
        # 清理计划任务状态
        self.cleanup_task = None
        self.is_cleaning = False
        
    async def start_daily_cleanup(self):
        """启动每日清理任务"""
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._daily_cleanup_loop())
            self.logger.info("每日频道清理任务已启动")
    
    async def stop_daily_cleanup(self):
        """停止每日清理任务"""
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.logger.info("每日频道清理任务已停止")
    
    async def _daily_cleanup_loop(self):
        """每日清理循环"""
        while True:
            try:
                # 等待到下一个清理时间 (每天凌晨2点)
                now = datetime.now()
                tomorrow_2am = (now + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)
                wait_seconds = (tomorrow_2am - now).total_seconds()
                
                self.logger.info(f"下次清理时间: {tomorrow_2am}, 等待 {wait_seconds/3600:.1f} 小时")
                await asyncio.sleep(wait_seconds)
                
                # 执行清理
                await self.cleanup_today_messages()
                
            except asyncio.CancelledError:
                self.logger.info("每日清理任务被取消")
                break
            except Exception as e:
                self.logger.error(f"每日清理任务发生错误: {e}")
                # 出错后等待1小时再重试
                await asyncio.sleep(3600)
    
    async def cleanup_today_messages(self):
        """清理所有历史消息"""
        if self.is_cleaning:
            self.logger.warning("清理任务正在进行中，跳过")
            return
        
        self.is_cleaning = True
        try:
            self.logger.info("开始清理所有历史消息")
            
            # 获取监控频道列表
            monitor_channels = self._get_monitor_channels()
            
            total_deleted = 0
            for channel_id in monitor_channels:
                try:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel is None:
                        self.logger.warning(f"找不到频道: {channel_id}")
                        continue
                    
                    deleted_count = await self._cleanup_all_channel_history(channel)
                    total_deleted += deleted_count
                    
                    # 频道间稍作休息，避免API限制
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"清理频道 {channel_id} 时发生错误: {e}")
            
            self.logger.info(f"历史清理完成，共删除 {total_deleted} 条消息")
            
        except Exception as e:
            self.logger.error(f"清理任务发生错误: {e}")
        finally:
            self.is_cleaning = False
    
    async def _cleanup_all_channel_history(self, channel) -> int:
        """清理指定频道的所有历史消息"""
        deleted_count = 0
        
        try:
            self.logger.info(f"开始清理频道 {channel.name} 的所有历史消息")
            
            # 获取所有消息（不限制时间）
            async for message in channel.history(limit=None):
                try:
                    # 跳过置顶消息
                    if message.pinned:
                        continue
                    
                    # 删除所有消息
                    if await self._is_useless_message(message):
                        await message.delete()
                        deleted_count += 1
                        self.logger.debug(f"删除消息: {message.content[:50]}...")
                        
                        # 避免删除过快触发API限制
                        await asyncio.sleep(0.3)
                        
                except discord.NotFound:
                    # 消息已被删除，跳过
                    continue
                except discord.Forbidden:
                    self.logger.warning(f"没有权限删除消息: {message.id}")
                    continue
                except Exception as e:
                    self.logger.error(f"删除消息时发生错误: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"获取频道消息时发生错误: {e}")
        
        self.logger.info(f"频道 {channel.name} 历史清理完成，删除了 {deleted_count} 条消息")
        return deleted_count
    
    async def manual_cleanup_current_channel(self, channel) -> int:
        """清理当前频道的历史消息"""
        if self.is_cleaning:
            self.logger.warning("清理任务正在进行中，跳过")
            return 0
        
        self.is_cleaning = True
        try:
            self.logger.info(f"开始清理当前频道 {channel.name} ({channel.id}) 的历史消息")
            
            # 检查权限
            if hasattr(channel, 'permissions_for'):
                permissions = channel.permissions_for(channel.guild.me)
                can_read = permissions.read_messages
                can_manage = permissions.manage_messages
                
                self.logger.info(f"频道权限 - 读取消息: {can_read}, 管理消息: {can_manage}")
                
                if not can_read or not can_manage:
                    self.logger.warning(f"权限不足，无法清理频道 {channel.name}")
                    return 0
            
            deleted_count = await self._cleanup_all_channel_history(channel)
            self.logger.info(f"当前频道清理完成，删除 {deleted_count} 条消息")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"清理当前频道失败: {e}")
            return 0
        finally:
            self.is_cleaning = False
    
    async def _is_useless_message(self, message) -> bool:
        """判断消息是否为无用消息 - 删除所有消息"""
        # 删除所有消息，包括自己的消息
        return True
    
    def _get_monitor_channels(self) -> List[str]:
        """获取监控频道列表"""
        monitor_channels = []
        
        # 支持多频道配置
        if hasattr(self.config, 'monitor_channel_ids') and self.config.monitor_channel_ids:
            # 检查是否为列表格式
            if isinstance(self.config.monitor_channel_ids, list):
                monitor_channels.extend(self.config.monitor_channel_ids)
                self.logger.debug(f"从列表获取频道: {self.config.monitor_channel_ids}")
            else:
                # 字符串格式: "id1,id2,id3"
                channel_ids = [cid.strip() for cid in self.config.monitor_channel_ids.split(',')]
                monitor_channels.extend(channel_ids)
                self.logger.debug(f"从字符串分割获取频道: {channel_ids}")
        elif hasattr(self.config, 'monitor_channel_id') and self.config.monitor_channel_id:
            # 单频道格式 (向后兼容)
            monitor_channels.append(self.config.monitor_channel_id)
            self.logger.debug(f"从单频道获取: {self.config.monitor_channel_id}")
        
        self.logger.info(f"最终监控频道列表: {monitor_channels}")
        return monitor_channels
    
    async def manual_cleanup(self, channel_id: str | None = None, days: int = 1):
        """手动清理指定频道的所有历史消息"""
        try:
            if channel_id:
                # 清理指定频道
                channel = self.bot.get_channel(int(channel_id))
                if channel is None:
                    self.logger.error(f"找不到频道: {channel_id}")
                    return 0
                
                deleted_count = await self._cleanup_all_channel_history(channel)
                self.logger.info(f"手动清理频道 {channel.name} 完成，删除了 {deleted_count} 条消息")
                return deleted_count
            else:
                # 清理所有监控频道
                monitor_channels = self._get_monitor_channels()
                total_deleted = 0
                
                self.logger.info(f"手动清理开始 - 准备清空所有频道历史: {monitor_channels}")
                if not monitor_channels:
                    self.logger.warning("没有找到监控频道，检查配置")
                    return 0
                
                for cid in monitor_channels:
                    self.logger.info(f"正在处理频道ID: {cid} (类型: {type(cid)})")
                    try:
                        channel_id_int = int(cid.strip())
                        channel = self.bot.get_channel(channel_id_int)
                        if channel:
                            self.logger.info(f"开始清空频道历史: {channel.name} ({channel_id_int})")
                            # 获取权限信息
                            permissions = channel.permissions_for(channel.guild.me)
                            self.logger.info(f"频道权限 - 读取消息: {permissions.read_messages}, 管理消息: {permissions.manage_messages}")
                            
                            deleted_count = await self._cleanup_all_channel_history(channel)
                            total_deleted += deleted_count
                            self.logger.info(f"频道 {channel.name} 历史清空完成，删除 {deleted_count} 条消息")
                            await asyncio.sleep(2)
                        else:
                            self.logger.warning(f"无法获取频道对象: {cid}")
                    except ValueError as e:
                        self.logger.error(f"无效的频道ID: {cid}, 错误: {e}")
                        continue
                    except Exception as e:
                        self.logger.error(f"处理频道 {cid} 时发生错误: {e}")
                        continue
                
                self.logger.info(f"手动清理所有监控频道完成，共删除了 {total_deleted} 条历史消息")
                return total_deleted
                
        except Exception as e:
            self.logger.error(f"手动清理时发生错误: {e}", exc_info=True)
            return 0
    

    
    async def get_cleanup_stats(self) -> dict:
        """获取清理统计信息"""
        stats = {
            'is_running': self.cleanup_task and not self.cleanup_task.done(),
            'is_cleaning': self.is_cleaning,
            'monitor_channels': len(self._get_monitor_channels()),
            'next_cleanup': None
        }
        
        if stats['is_running']:
            now = datetime.now()
            tomorrow_2am = (now + timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)
            if now.hour >= 2:
                stats['next_cleanup'] = tomorrow_2am
            else:
                today_2am = now.replace(hour=2, minute=0, second=0, microsecond=0)
                stats['next_cleanup'] = today_2am
        
        return stats