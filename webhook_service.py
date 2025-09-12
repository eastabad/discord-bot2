"""
个人Webhook服务
为每个Discord用户分配独立的Webhook URL，处理TradingView Alert消息
"""
import asyncio
import io
import json
import logging
import re
import secrets
import string
from datetime import datetime
from typing import Dict, Optional, Tuple

import discord
from discord.ext import commands
from models import UserWebhook, UserWebhookMessage, get_db_session
from parsing_engine import get_parsing_engine
from ai_template_engine import get_template_engine
from poc_analyzer import get_poc_analyzer


class TradingAlertView(discord.ui.View):
    """交易信号交互式按钮视图"""
    
    def __init__(self, alert_data: dict, symbol: str, timeframe: str, alert_id: int, bot):
        super().__init__(timeout=3600)  # 1小时超时
        self.alert_data = alert_data
        self.symbol = symbol
        self.timeframe = timeframe
        self.alert_id = alert_id
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @discord.ui.button(label='Get Chart', emoji='📈', style=discord.ButtonStyle.gray)
    async def get_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        """获取图表按钮处理"""
        try:
            # 检查交互是否仍然有效
            if interaction.response.is_done():
                self.logger.warning("交互已经响应过，可能是重复点击")
                return
                
            # 立即给用户反馈，避免3秒超时
            await interaction.response.send_message("📊 图表正在生成中，请稍候...", ephemeral=True)
            
            # 检查必需参数
            if not self.symbol:
                await interaction.followup.send("❌ 无法获取图表：缺少股票代码信息")
                return
            
            # 使用机器人的现有图表服务
            try:
                # 直接使用bot的图表服务实例
                chart_service = self.bot.chart_service
                
                # 调用原有的get_chart方法
                timeframe = self.timeframe or '15m'
                self.logger.info(f"请求图表: {self.symbol} {timeframe}")
                
                chart_data = await chart_service.get_chart(self.symbol, timeframe)
                
                if chart_data:
                    # 成功获取图表数据，发送为文件
                    try:
                        chart_file = discord.File(
                            io.BytesIO(chart_data), 
                            filename=f"{self.symbol}_{timeframe}.png"
                        )
                        
                        # 获取美国东部时间
                        from datetime import datetime
                        import pytz
                        
                        et_tz = pytz.timezone('US/Eastern')
                        current_et = datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 创建embed，将图片嵌入其中
                        embed = discord.Embed(
                            title=f"📊 {self.symbol} {timeframe} Chart",
                            description=f"生成时间：美国东部时间 {current_et}",
                            color=0x1f8b4c
                        )
                        
                        # 将图片设置为embed的图片
                        embed.set_image(url=f"attachment://{self.symbol}_{timeframe}.png")
                        
                        self.logger.info(f"准备发送图表文件: {self.symbol} {timeframe}, 大小: {len(chart_data)} bytes")
                        await interaction.followup.send(embed=embed, file=chart_file)
                        self.logger.info(f"✅ 成功发送图表到Discord: {self.symbol} {timeframe}")
                        
                    except discord.errors.HTTPException as http_error:
                        self.logger.error(f"Discord HTTP错误: {http_error}")
                        try:
                            await interaction.followup.send(f"❌ 图表发送失败: Discord服务器错误")
                        except discord.errors.NotFound:
                            self.logger.warning("交互已过期，无法发送HTTP错误消息")
                    except Exception as send_error:
                        self.logger.error(f"图表发送异常: {send_error}")
                        try:
                            await interaction.followup.send(f"❌ 图表发送失败: {send_error}")
                        except discord.errors.NotFound:
                            self.logger.warning("交互已过期，无法发送发送错误消息")
                else:
                    try:
                        await interaction.followup.send(f"❌ 无法获取 {self.symbol} {timeframe} 图表，请稍后重试")
                    except discord.errors.NotFound:
                        self.logger.warning("交互已过期，无法发送图表获取失败消息")
                    
            except Exception as chart_error:
                self.logger.error(f"图表服务调用失败: {chart_error}")
                try:
                    await interaction.followup.send(f"❌ 获取 {self.symbol} 图表时发生错误，请稍后重试")
                except discord.errors.NotFound:
                    self.logger.warning("交互已过期，无法发送图表错误消息")
                
        except Exception as e:
            self.logger.error(f"处理图表按钮失败: {e}")
            try:
                await interaction.followup.send("❌ 获取图表失败，请稍后重试")
            except discord.errors.NotFound:
                # 交互已过期，记录错误但不重复发送
                self.logger.warning("交互已过期，无法发送错误消息")
    
    @discord.ui.button(label='AI Decision', emoji='⚛️', style=discord.ButtonStyle.gray)
    async def ai_analysis(self, interaction: discord.Interaction, button: discord.ui.Button):
        """AI分析按钮处理"""
        try:
            # 检查交互是否仍然有效
            if interaction.response.is_done():
                self.logger.warning("AI分析交互已经响应过，可能是重复点击")
                return
                
            await interaction.response.send_message("🤖 正在生成AI分析报告，请稍候...", ephemeral=True)
            
            # 使用解析引擎处理数据
            from simple_config_engine import process_with_simple_config
            parsing_results = process_with_simple_config(self.alert_data)
            
            # 使用AI模板引擎生成报告
            from simple_ai_template import get_simple_ai_template_engine
            template_engine = get_simple_ai_template_engine()
            ai_prompt = template_engine.substitute_variables('RP', self.alert_data)
            
            # 调用AI服务生成报告
            from multi_ai_service import get_multi_ai_service
            multi_ai = get_multi_ai_service()
            
            # 生成AI报告
            report = await self.generate_ai_report_async(multi_ai, ai_prompt)
            
            if report:
                # 创建Discord embed格式的AI报告
                embed = self.create_ai_report_embed(report)
                try:
                    await interaction.followup.send(embed=embed)
                except discord.errors.NotFound:
                    self.logger.warning("交互已过期，AI报告生成完成但无法发送")
            else:
                try:
                    await interaction.followup.send("❌ AI分析生成失败，请稍后重试")
                except discord.errors.NotFound:
                    self.logger.warning("交互已过期，无法发送AI分析失败消息")
                
        except Exception as e:
            self.logger.error(f"处理AI分析按钮失败: {e}")
            try:
                await interaction.followup.send("❌ AI分析失败，请稍后重试")
            except discord.errors.NotFound:
                self.logger.warning("交互已过期，无法发送AI分析错误消息")
    
    @discord.ui.button(label='Order Block', emoji='🔲', style=discord.ButtonStyle.gray)
    async def get_ob_chart(self, interaction: discord.Interaction, button: discord.ui.Button):
        """获取Order Block图表按钮处理"""
        try:
            # 检查交互是否仍然有效
            if interaction.response.is_done():
                self.logger.warning("交互已经响应过，可能是重复点击")
                return
                
            # 立即给用户反馈，避免3秒超时
            await interaction.response.send_message("🔲 Order Block图表正在生成中，请稍候...", ephemeral=True)
            
            # 检查必需参数
            if not self.symbol:
                await interaction.followup.send("❌ 无法获取Order Block图表：缺少股票代码信息")
                return
            
            # 使用机器人的现有图表服务，但调用OB布局
            try:
                # 直接使用bot的图表服务实例
                chart_service = self.bot.chart_service
                
                # 调用OB图表方法
                timeframe = self.timeframe or '15m'
                self.logger.info(f"请求Order Block图表: {self.symbol} {timeframe}")
                
                # 使用OB专用的图表生成方法
                chart_data = await chart_service.get_ob_chart(self.symbol, timeframe)
                
                if chart_data:
                    # 成功获取图表数据，发送为文件
                    try:
                        chart_file = discord.File(
                            io.BytesIO(chart_data), 
                            filename=f"{self.symbol}_{timeframe}_OB.png"
                        )
                        
                        # 获取美国东部时间
                        from datetime import datetime
                        import pytz
                        
                        et_tz = pytz.timezone('US/Eastern')
                        current_et = datetime.now(et_tz).strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 创建embed，将图片嵌入其中
                        embed = discord.Embed(
                            title=f"🔲 {self.symbol} {timeframe} Order Block Chart",
                            description=f"生成时间：美国东部时间 {current_et}\n📊 Order Block + MoneyFlow + Volume图表",
                            color=0x9932cc  # 紫色，区别于普通图表
                        )
                        
                        # 将图片设置为embed的图片
                        embed.set_image(url=f"attachment://{self.symbol}_{timeframe}_OB.png")
                        
                        self.logger.info(f"准备发送OB图表文件: {self.symbol} {timeframe}, 大小: {len(chart_data)} bytes")
                        await interaction.followup.send(embed=embed, file=chart_file)
                        self.logger.info(f"✅ 成功发送Order Block图表到Discord: {self.symbol} {timeframe}")
                        
                    except discord.errors.HTTPException as http_error:
                        self.logger.error(f"Discord HTTP错误: {http_error}")
                        try:
                            await interaction.followup.send(f"❌ Order Block图表发送失败: Discord服务器错误")
                        except discord.errors.NotFound:
                            self.logger.warning("交互已过期，无法发送HTTP错误消息")
                    except Exception as send_error:
                        self.logger.error(f"OB图表发送异常: {send_error}")
                        try:
                            await interaction.followup.send(f"❌ Order Block图表发送失败: {send_error}")
                        except discord.errors.NotFound:
                            self.logger.warning("交互已过期，无法发送发送错误消息")
                else:
                    try:
                        await interaction.followup.send(f"❌ 无法获取 {self.symbol} {timeframe} Order Block图表，请稍后重试")
                    except discord.errors.NotFound:
                        self.logger.warning("交互已过期，无法发送图表获取失败消息")
                    
            except Exception as chart_error:
                self.logger.error(f"Order Block图表服务调用失败: {chart_error}")
                try:
                    await interaction.followup.send(f"❌ 获取 {self.symbol} Order Block图表时发生错误，请稍后重试")
                except discord.errors.NotFound:
                    self.logger.warning("交互已过期，无法发送图表错误消息")
                
        except Exception as e:
            self.logger.error(f"处理Order Block图表按钮失败: {e}")
            try:
                await interaction.followup.send("❌ 获取Order Block图表失败，请稍后重试")
            except discord.errors.NotFound:
                # 交互已过期，记录错误但不重复发送
                self.logger.warning("交互已过期，无法发送错误消息")
    
    @discord.ui.button(label='TradeNow', emoji='💵', style=discord.ButtonStyle.gray)
    async def execute_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        """执行交易按钮处理"""
        try:
            await interaction.response.defer()
            
            # 检查用户是否配置了TradersPost
            user_id = str(interaction.user.id)
            
            from models import TradersPostConfig
            db = get_db_session()
            try:
                config = db.query(TradersPostConfig).filter(
                    TradersPostConfig.user_id == user_id,
                    TradersPostConfig.is_active == True
                ).first()
                
                if not config:
                    # 引导用户设置TradersPost配置
                    guide_embed = discord.Embed(
                        title="⚡ 配置TradersPost交易执行",
                        description="您还未配置TradersPost webhook，需要先设置才能执行自动交易",
                        color=0xffa500
                    )
                    guide_embed.add_field(
                        name="🔧 设置步骤",
                        value="1. 使用命令 `!traderspost set <您的webhook_url>`\n" +
                              "2. 示例: `!traderspost set https://api.traderspost.io/v1/webhooks/YOUR_KEY`\n" +
                              "3. 设置完成后即可使用交易执行功能",
                        inline=False
                    )
                    guide_embed.add_field(
                        name="📋 其他命令",
                        value="`!traderspost info` - 查看当前配置\n" +
                              "`!traderspost delete` - 删除配置",
                        inline=False
                    )
                    await interaction.followup.send(embed=guide_embed)
                    return
                
                traderspost_url = config.webhook_url
            
                # 发送原始JSON到TradersPost
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        traderspost_url,
                        json=self.alert_data,
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        if response.status == 200:
                            success_embed = discord.Embed(
                                title="⚡ 交易执行成功",
                                description=f"已发送 {self.symbol} 交易信号到TradersPost",
                                color=0x00ff00
                            )
                            success_embed.add_field(
                                name="📊 交易详情",
                                value=f"股票: {self.symbol}\n" +
                                      f"操作: {self.alert_data.get('action', '未知')}\n",
                                inline=True
                            )
                            await interaction.followup.send(embed=success_embed)
                        else:
                            error_text = await response.text()
                            
                            # 针对404错误给出更明确的指导
                            if response.status == 404:
                                error_embed = discord.Embed(
                                    title="❌ TradersPost Webhook失效",
                                    description="您的webhook URL已失效或不存在",
                                    color=0xff0000
                                )
                                error_embed.add_field(
                                    name="🔧 解决步骤",
                                    value="1. 登录TradersPost控制面板\n" +
                                          "2. 重新生成webhook URL\n" +
                                          "3. 使用 `!traderspost set <新的URL>` 更新配置",
                                    inline=False
                                )
                                error_embed.add_field(
                                    name="💡 提示",
                                    value="确保URL格式为: `https://api.traderspost.io/v1/webhooks/YOUR_REAL_KEY`",
                                    inline=False
                                )
                                await interaction.followup.send(embed=error_embed)
                            else:
                                await interaction.followup.send(f"❌ TradersPost执行失败\n错误码: {response.status}\n详情: {error_text[:200]}")
                        
            finally:
                db.close()
                        
        except Exception as e:
            self.logger.error(f"处理交易执行按钮失败: {e}")
            await interaction.followup.send("❌ 交易执行失败，请检查TradersPost配置")
    
    async def generate_ai_report_async(self, multi_ai, prompt: str) -> Optional[str]:
        """异步生成AI报告 (增强错误处理)"""
        try:
            # 使用多AI服务生成报告，增加超时保护
            import asyncio
            result = await asyncio.wait_for(
                asyncio.to_thread(multi_ai.generate_report, prompt, self.symbol),
                timeout=60.0  # 60秒超时
            )
            
            if result and result.get('success'):
                return result.get('content', '报告生成失败')
            elif result and result.get('errors'):
                # 记录所有AI模型的错误
                self.logger.error(f"所有AI模型都失败: {result.get('errors')}")
                return result.get('content', '报告生成失败，但提供了备用内容')
            else:
                return None
                
        except asyncio.TimeoutError:
            self.logger.error("AI报告生成超时")
            return None
        except Exception as e:
            self.logger.error(f"生成AI报告失败: {e}")
            return None
    
    def split_long_message(self, text: str, max_length: int = 2000) -> list:
        """分割长消息"""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current = ""
        
        for line in text.split('\n'):
            if len(current + line + '\n') <= max_length:
                current += line + '\n'
            else:
                if current:
                    parts.append(current.strip())
                    current = line + '\n'
                else:
                    # 单行太长，强制分割
                    while len(line) > max_length:
                        parts.append(line[:max_length])
                        line = line[max_length:]
                    current = line + '\n'
        
        if current:
            parts.append(current.strip())
        
        return parts
    
    def create_ai_report_embed(self, report: str) -> discord.Embed:
        """创建AI报告的Discord embed格式"""
        try:
            # 清理AI报告内容，去掉固定的头部文本
            cleaned_report = self._clean_ai_report_content(report)
            
            # 限制描述长度
            description = cleaned_report[:4000] if len(cleaned_report) > 4000 else cleaned_report
            
            embed = discord.Embed(
                title=f"🤖 AI辅助决策报告 - {self.symbol}",
                description=description,
                color=0x0066cc,  # 蓝色
                timestamp=datetime.now()
            )
            
            # 不再添加时间框架、风险等级、交易方向等字段
            
            # 设置footer为TD AIassistant-报告生成时间（美国东部时间）
            est_time = self._get_est_time()
            embed.set_footer(text=f"TD AIassistant-{est_time}")
            
            return embed
            
        except Exception as e:
            self.logger.error(f"创建AI报告embed失败: {e}")
            # 回退到基础embed
            cleaned_report = self._clean_ai_report_content(report)
            est_time = self._get_est_time()
            return discord.Embed(
                title=f"🤖 AI辅助决策报告 - {self.symbol}",
                description=cleaned_report[:4000] if len(cleaned_report) > 4000 else cleaned_report,
                color=0x0066cc  # 蓝色
            )
    
    def _clean_ai_report_content(self, report: str) -> str:
        """清理AI报告内容，去掉固定的头部和尾部文本"""
        if not report:
            return report
        
        # 去掉常见的固定头部文本
        patterns_to_remove = [
            r"AI辅助决策报告\s*-\s*[A-Z]+\s*",  # 移除"AI辅助决策报告 - MSTR"
            r"好的，这是一份根据您提供的原始信号生成的[A-Z]+中文交易决策报告。\s*",
            r"好的，这是一份根据您提供的信号生成的.*?中文交易决策报告。\s*", 
            r"好的，这是一份根据您提供的信号和要求生成的.*?中文交易决策报告。\s*",
            r"好的，这是一份根据您提供的[A-Z]+交易信号生成的.*?中文交易决策报告。\s*",  # 新增：处理"MSTR交易信号"变体
            r"好的，这是一份根据您提供的格式和要求生成的.*?中文交易.*?报告.*?。\s*",
            r"这是一份基于您提供的数据生成的.*?分析报告。\s*",
            r"基于您提供的信息，我为您生成了以下.*?分析报告：\s*",
            r"^\s*---\s*",  # 移除开头的分隔线
            r"^\s*---\s*\n"  # 移除开头的分隔线加换行
        ]
        
        cleaned_report = report
        for pattern in patterns_to_remove:
            cleaned_report = re.sub(pattern, "", cleaned_report, flags=re.IGNORECASE | re.DOTALL)
        
        # 去掉开头和结尾的多余空行和分隔符
        cleaned_report = re.sub(r"^[\s\-]*\n*", "", cleaned_report)
        cleaned_report = re.sub(r"\n*[\s\-]*$", "", cleaned_report)
        
        # 处理重复的股票代码交易决策报告标题，只保留第一个
        title_pattern = r"([A-Z]+\s*(?:\([^)]+\))?\s*交易决策报告\s*[\,，]?\s*)"
        matches = list(re.finditer(title_pattern, cleaned_report))
        
        if len(matches) > 1:
            for match in reversed(matches[1:]):
                start, end = match.span()
                cleaned_report = cleaned_report[:start] + cleaned_report[end:]
        
        # 清理格式问题：移除不必要的HTML标签风格格式和逗号
        cleaned_report = re.sub(r"交易决策报告,\s*", "交易决策报告\n\n", cleaned_report)
        cleaned_report = re.sub(r"趋势概况,\s*", "## 📈 趋势概况\n", cleaned_report)  
        cleaned_report = re.sub(r"交易方向：", "\n## 📊 交易方向：", cleaned_report)
        
        # 修复HTML样式标签为简洁格式
        cleaned_report = re.sub(r'<span style="color:green;">(.*?)</span>', r'**\1**', cleaned_report)
        cleaned_report = re.sub(r'<span style="color:red;">(.*?)</span>', r'**\1**', cleaned_report)
        
        # 确保合理的换行和段落分隔
        cleaned_report = re.sub(r",\s*\n", "\n", cleaned_report)  # 移除行尾逗号
        cleaned_report = re.sub(r"\n{3,}", "\n\n", cleaned_report)  # 限制连续换行
        
        return cleaned_report.strip()
    
    def _get_est_time(self) -> str:
        """获取美国东部时间"""
        try:
            import pytz
            from datetime import datetime
            
            # 获取美国东部时区
            est_tz = pytz.timezone('US/Eastern')
            now = datetime.now(est_tz)
            
            # 格式化时间：MM/DD/YYYY HH:MM:SS AM/PM
            time_str = now.strftime("%m/%d/%Y %I:%M:%S %p")
            return time_str
            
        except Exception as e:
            self.logger.warning(f"获取美国东部时间失败: {e}")
            # 回退到UTC时间
            now = datetime.utcnow()
            time_str = now.strftime("%m/%d/%Y %I:%M:%S %p UTC")
            return time_str

    def get_traderspost_webhook_url(self, user_id: int) -> Optional[str]:
        """获取用户的TradersPost webhook URL"""
        try:
            db = get_db_session()
            from models import TradersPostConfig
            
            # 从数据库获取用户的TradersPost配置
            config = db.query(TradersPostConfig).filter(
                TradersPostConfig.user_id == str(user_id),
                TradersPostConfig.is_active == True
            ).first()
            
            db.close()
            
            if config:
                return config.webhook_url
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"获取TradersPost URL失败: {e}")
            return None


class PersonalWebhookService:
    """个人Webhook服务类"""
    
    def __init__(self, bot, base_domain: str = None):
        self.bot = bot
        # 使用环境变量中的域名，如果没有则使用默认值
        import os
        self.base_domain = base_domain or os.environ.get("DOMAIN", "tvdata.tdindicator.top")
        self.logger = logging.getLogger(__name__)
    
    def generate_webhook_secret(self) -> str:
        """生成随机的webhook密钥"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(16))
    
    def create_user_webhook(self, user_id: str, username: str) -> Tuple[bool, str]:
        """
        为用户创建个人Webhook
        返回: (成功标志, secret_token_or_error_message)
        """
        try:
            db = get_db_session()
            
            # 检查用户是否已有webhook
            existing_webhook = db.query(UserWebhook).filter(
                UserWebhook.user_id == user_id
            ).first()
            
            if existing_webhook:
                if existing_webhook.is_active:
                    db.close()
                    return True, existing_webhook.webhook_secret
                else:
                    # 重新激活已有的webhook
                    existing_webhook.is_active = True
                    existing_webhook.updated_at = datetime.now()
                    db.commit()
                    db.close()
                    return True, existing_webhook.webhook_secret
            
            # 生成新的webhook
            webhook_secret = self.generate_webhook_secret()
            webhook_url = f"https://{self.base_domain}/webhook/tradingview/{user_id}/{webhook_secret}"
            
            # 创建数据库记录
            new_webhook = UserWebhook(
                user_id=user_id,
                username=username,
                webhook_secret=webhook_secret,
                webhook_url=webhook_url,
                is_active=True
            )
            
            db.add(new_webhook)
            db.commit()
            db.close()
            
            self.logger.info(f"为用户 {username} ({user_id}) 创建个人webhook: {webhook_url}")
            return True, webhook_secret
            
        except Exception as e:
            self.logger.error(f"创建用户webhook失败: {e}")
            return False, str(e)
    
    def deactivate_user_webhook(self, user_id: str) -> Tuple[bool, str]:
        """
        停用用户的webhook
        返回: (成功标志, 错误信息)
        """
        try:
            db = get_db_session()
            
            webhook = db.query(UserWebhook).filter(
                UserWebhook.user_id == user_id
            ).first()
            
            if not webhook:
                db.close()
                return False, "未找到您的webhook配置"
            
            webhook.is_active = False
            webhook.updated_at = datetime.now()
            db.commit()
            db.close()
            
            self.logger.info(f"停用用户 {user_id} 的webhook")
            return True, ""
            
        except Exception as e:
            self.logger.error(f"停用用户webhook失败: {e}")
            return False, str(e)
    
    def validate_webhook_request(self, user_id: str, secret: str) -> Tuple[bool, str]:
        """
        验证webhook请求
        返回: (是否有效, 用户名)
        """
        try:
            db = get_db_session()
            
            webhook = db.query(UserWebhook).filter(
                UserWebhook.user_id == user_id,
                UserWebhook.webhook_secret == secret,
                UserWebhook.is_active == True
            ).first()
            
            if webhook:
                # 更新最后使用时间和消息计数
                webhook.last_used = datetime.now()
                webhook.message_count += 1
                db.commit()
                username = webhook.username
                db.close()
                return True, username
            else:
                db.close()
                return False, ""
                
        except Exception as e:
            self.logger.error(f"验证webhook请求失败: {e}")
            return False, ""
    
    def process_tradingview_alert(self, user_id: str, secret: str, alert_data: Dict) -> Tuple[bool, str]:
        """
        处理TradingView Alert消息
        返回: (成功标志, 错误信息)
        """
        try:
            # 验证请求
            is_valid, username = self.validate_webhook_request(user_id, secret)
            if not is_valid:
                return False, "Webhook验证失败"
            
            # 使用解析引擎处理数据
            parsing_engine = get_parsing_engine()
            parsed_results = parsing_engine.parse_data(alert_data)
            summary_text = parsing_engine.get_parsed_summary(alert_data)
            
            # 使用POC分析器处理POC字段 (传入完整的alert_data)
            poc_analyzer = get_poc_analyzer()
            poc_data = poc_analyzer.parse_poc_data(alert_data)
            
            # 添加解析结果到alert数据中
            enhanced_alert_data = alert_data.copy()
            enhanced_alert_data.update(parsed_results)
            enhanced_alert_data.update(poc_data)
            enhanced_alert_data['analysis_summary'] = summary_text
            
            # 解析alert数据
            raw_message = json.dumps(alert_data) if isinstance(alert_data, dict) else str(alert_data)
            symbol, timeframe = self.parse_alert_data(alert_data)
            
            # 格式化消息（使用增强的数据）
            processed_message = self.format_alert_message(enhanced_alert_data, symbol, timeframe)
            
            # 保存到数据库
            db = get_db_session()
            alert_record = UserWebhookMessage(
                user_id=user_id,
                webhook_secret=secret,
                symbol=symbol,
                timeframe=timeframe,
                alert_message=raw_message,
                processed_message=processed_message,
                is_sent=False
            )
            db.add(alert_record)
            db.commit()
            alert_id = alert_record.id
            db.close()
            
            # 发送到Discord用户（使用增强数据的embed格式）
            success = self.send_trading_alert_to_user(user_id, enhanced_alert_data, symbol, timeframe, alert_id)
            
            return success, "" if success else "发送消息失败"
            
        except Exception as e:
            self.logger.error(f"处理TradingView Alert失败: {e}")
            return False, str(e)
    
    def parse_alert_data(self, alert_data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """
        从alert数据中解析股票代码和时间框架
        返回: (symbol, timeframe)
        """
        try:
            symbol = None
            timeframe = None
            
            # 尝试从不同字段解析
            if isinstance(alert_data, dict):
                # 常见的TradingView字段
                symbol = alert_data.get('ticker') or alert_data.get('symbol')
                timeframe = alert_data.get('interval') or alert_data.get('timeframe')
            
            # 如果是字符串格式，尝试解析
            elif isinstance(alert_data, str):
                # 查找类似 "AAPL 15m" 的模式
                pattern = r'([A-Z]{1,5})\s*(\d+[mhd]|\w+)'
                match = re.search(pattern, alert_data)
                if match:
                    symbol = match.group(1)
                    timeframe = match.group(2)
            
            return symbol, timeframe
            
        except Exception as e:
            self.logger.error(f"解析Alert数据失败: {e}")
            return None, None
    
    def format_alert_message(self, alert_data: Dict, symbol: Optional[str], timeframe: Optional[str]) -> str:
        """
        格式化Alert消息为Discord友好格式 - 支持做多/做空/退出信号
        """
        try:
            # 解析数据
            if isinstance(alert_data, str):
                try:
                    alert_data = json.loads(alert_data)
                except:
                    # 如果不是JSON，保持原始字符串
                    pass
            
            # 提取信号信息
            signal_type = ""
            price = ""
            message = ""
            
            if isinstance(alert_data, dict):
                signal_type = (alert_data.get('action') or 
                             alert_data.get('signal') or 
                             alert_data.get('side') or
                             alert_data.get('direction', ''))
                
                price = alert_data.get('close') or alert_data.get('price') or alert_data.get('current_price')
                message = alert_data.get('message') or alert_data.get('text') or alert_data.get('alert_message', '')
            
            # 判断信号类型并设置样式
            signal_emoji = "⚡"
            signal_color = "🔵"
            signal_title = "交易信号"
            
            signal_lower = str(signal_type).lower()
            if any(word in signal_lower for word in ['buy', 'long', '做多', 'bullish', 'enter_long', 'bull']):
                signal_emoji = "📈"
                signal_color = "🟢"
                signal_title = "做多信号"
            elif any(word in signal_lower for word in ['sell', 'short', '做空', 'bearish', 'enter_short', 'bear']):
                signal_emoji = "📉"
                signal_color = "🔴"
                signal_title = "做空信号"
            elif any(word in signal_lower for word in ['exit', 'close', '退出', '平仓', 'exit_long', 'exit_short', 'flat']):
                signal_emoji = "🚪"
                signal_color = "🟡"
                signal_title = "退出信号"
            elif signal_type:
                signal_title = f"交易信号: {signal_type}"
            
            # 构建格式化消息
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            formatted_msg = f"{signal_color} **{signal_title}** {signal_emoji}\n"
            formatted_msg += f"⏰ **{timestamp}**\n"
            formatted_msg += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # 交易基础信息
            if symbol:
                formatted_msg += f"📊 **标的:** {symbol}\n"
            if timeframe:
                formatted_msg += f"⏱️ **周期:** {timeframe}\n"
            if price:
                if isinstance(price, (int, float)):
                    formatted_msg += f"💰 **价格:** ${price:.2f}\n"
                else:
                    formatted_msg += f"💰 **价格:** {price}\n"
            
            # 操作信号
            if signal_type:
                formatted_msg += f"{signal_emoji} **操作:** {signal_type.upper()}\n"
            
            # 详细消息
            if message:
                formatted_msg += f"\n📝 **详情:**\n{message}\n"
            
            # 技术指标信息（如果有）
            if isinstance(alert_data, dict):
                indicators = alert_data.get('indicators', {})
                if indicators and isinstance(indicators, dict):
                    formatted_msg += f"\n📊 **技术指标:**\n"
                    for key, value in indicators.items():
                        formatted_msg += f"• {key}: {value}\n"
                
                # 置信度
                confidence = alert_data.get('confidence')
                if confidence:
                    formatted_msg += f"\n🎯 **置信度:** {confidence}\n"
                
                # 建议
                recommendation = alert_data.get('recommendation')
                if recommendation:
                    formatted_msg += f"💡 **建议:** {recommendation}\n"
                
                # 止损止盈信息
                stop_loss = alert_data.get('stop_loss') or alert_data.get('sl')
                take_profit = alert_data.get('take_profit') or alert_data.get('tp')
                
                if stop_loss or take_profit:
                    formatted_msg += f"\n🎯 **风控设置:**\n"
                    if stop_loss:
                        formatted_msg += f"• 止损: {stop_loss}\n"
                    if take_profit:
                        formatted_msg += f"• 止盈: {take_profit}\n"
            
            formatted_msg += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
            formatted_msg += f"🤖 **TDbot Trading Alert**"
            
            return formatted_msg
            
        except Exception as e:
            self.logger.error(f"格式化Alert消息失败: {e}")
            # 简化的错误格式
            return f"🚨 **TradingView Alert**\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📝 {str(alert_data)[:500]}"
    
    def create_trading_embed(self, formatted_message: str) -> dict:
        """
        根据格式化消息创建Discord embed，匹配JavaScript代码的格式
        """
        try:
            # 从格式化消息中提取信息（这里需要解析原始alert数据）
            # 由于消息已经格式化，我们需要从process_personal_webhook_alert传递原始数据
            # 暂时创建一个基础的embed格式
            
            current_date = datetime.now()
            est_date = current_date.strftime('%m/%d/%Y')  # 美国日期格式
            est_time = current_date.strftime('%I:%M:%S %p')  # 12小时制时间
            
            # 默认embed结构
            embed_data = {
                "title": "Trading Signal",
                "description": formatted_message,
                "color": 65280,  # 绿色 (0x00FF00)
                "thumbnail": {
                    "url": "https://via.placeholder.com/80"  # 基础方法保持placeholder
                },
                "fields": [],
                "timestamp": current_date.isoformat(),
                "footer": {
                    "text": f"TD AIassistant • {est_date} • {est_time}"
                }
            }
            
            return embed_data
            
        except Exception as e:
            self.logger.error(f"创建trading embed失败: {e}")
            # 回退到简单格式
            return {
                "title": "TradingView Alert",
                "description": formatted_message,
                "color": 65535,  # 青色
                "timestamp": datetime.now().isoformat()
            }
    
    def create_trading_embed_from_data(self, alert_data: dict, symbol: str = None, timeframe: str = None) -> dict:
        """
        直接从alert数据创建Discord embed，完全匹配JavaScript格式
        支持新增的supply/demand/referencePrice字段和美国东部时间显示
        """
        try:
            # 获取美国东部时间
            import pytz
            est_tz = pytz.timezone('US/Eastern')
            current_est = datetime.now(est_tz)
            timestamp = current_est.isoformat()
            
            # 提取关键数据
            ticker = symbol or alert_data.get('ticker') or alert_data.get('symbol') or 'Unknown'
            action = alert_data.get('action', 'buy').lower()
            sentiment = alert_data.get('sentiment', 'bullish').lower()
            
            # 判断信号类型
            if sentiment == 'flat':
                signal_type = 'ExitShort' if action == 'buy' else 'ExitLong'
                color = 16776960  # 黄色 (0xFFFF00)
                emoji = '🟨'
            else:
                signal_type = 'Long' if action == 'buy' else 'Short'
                color = 65280 if action == 'buy' else 16711680  # 绿色或红色
                emoji = '🟩' if action == 'buy' else '🟥'
            
            # 提取其他数据
            extras = alert_data.get('extras', {})
            osc_rating = float(extras.get('oscrating', 0))
            trend_rating = float(extras.get('trendrating', 0))
            rating = int(osc_rating + trend_rating)
            
            take_profit = alert_data.get('takeProfit', {}).get('limitPrice', 'N/A')
            stop_loss = alert_data.get('stopLoss', {}).get('stopPrice', 'N/A')
            timeframe_value = timeframe or extras.get('timeframe', 'N/A')
            indicator = extras.get('indicator', 'N/A')
            quantity = alert_data.get('quantity')
            position = f"{quantity}%" if quantity else 'N/A'
            
            # 风险星级
            risk = extras.get('risk')
            risk_stars = self.risk_to_stars(risk) if risk else 'N/A'
            
            # 新增字段：供需区和参考价格 (多层级提取)
            # 从顶级、data层、extras层多个位置尝试提取
            data_level = alert_data.get('data', {}) if isinstance(alert_data.get('data'), dict) else {}
            
            last_supply_text = (alert_data.get('lastSupplyText') or 
                              data_level.get('lastSupplyText') or 
                              extras.get('lastSupplyText'))
            last_demand_text = (alert_data.get('lastDemandText') or 
                              data_level.get('lastDemandText') or 
                              extras.get('lastDemandText'))
            reference_price = (alert_data.get('referencePrice') or 
                             data_level.get('referencePrice') or 
                             extras.get('referencePrice'))
            
            # 构建描述
            if sentiment == 'flat':
                description = f"**Action**: {signal_type}\n**Ticker**: {ticker}\n**Indicator**: `{indicator}` {emoji}"
            else:
                description = f"**Action**: {signal_type}\n**Ticker**: {ticker}\n**Price**: Market Price\n**Rating**: `{rating}` {emoji}\n**Position**: `{position}`\n**Risk**: `{risk_stars}`"
            
            # 美东时间 - 修复为美国东部时间
            est_date = current_est.strftime('%m/%d/%Y')
            est_time = current_est.strftime('%I:%M:%S %p')
            
            # 构建字段 - 添加新的供需区字段
            if sentiment == 'flat':
                fields = [
                    {"name": "Timeframe", "value": timeframe_value, "inline": True},
                    {"name": "Indicator", "value": indicator, "inline": False}
                ]
            else:
                fields = [
                    {"name": "Take Profit", "value": f"${take_profit}", "inline": True},
                    {"name": "Stop Loss", "value": f"${stop_loss}", "inline": True},
                    {"name": "Timeframe", "value": timeframe_value, "inline": True},
                    {"name": "Indicator", "value": indicator, "inline": False}
                ]
                
                # 添加新的供需区字段
                if last_supply_text:
                    fields.append({"name": "Nearest Supply", "value": str(last_supply_text), "inline": True})
                if last_demand_text:
                    fields.append({"name": "Nearest Demand", "value": str(last_demand_text), "inline": True})
                if reference_price:
                    fields.append({"name": "Reference Price", "value": f"${reference_price}", "inline": True})
                
                # 添加Order Block信息字段
                ob_data = (alert_data.get('obData') or 
                          data_level.get('obData') or 
                          extras.get('obData'))
                if ob_data:
                    fields.append({"name": "Order Block Info", "value": str(ob_data), "inline": False})
                
                # 添加POC相关信息 (放在OB信息下面，排成两行)
                poc_analyzer = get_poc_analyzer()
                poc_data = poc_analyzer.parse_poc_data(alert_data)
                poc_formatted = poc_analyzer.format_poc_info_for_embed(poc_data)
                if poc_formatted:
                    fields.append({"name": "POC Analysis", "value": poc_formatted, "inline": False})
                
                # 移除时间字段，将在footer中显示
            
            # 获取ticker logo
            logo_url = self.get_ticker_logo(ticker)
            
            # 构建最终embed，添加footer
            embed_data = {
                "title": f"{signal_type} Signal for {ticker}",
                "description": description,
                "color": color,
                "thumbnail": {
                    "url": logo_url
                },
                "fields": fields,
                "timestamp": timestamp,
                "footer": {
                    "text": f"TD AIassistant • {est_date} • {est_time}"
                }
            }
            
            return embed_data
            
        except Exception as e:
            self.logger.error(f"从数据创建trading embed失败: {e}")
            # 回退格式
            return {
                "title": f"Trading Signal for {symbol or 'Unknown'}",
                "description": str(alert_data),
                "color": 65535,
                "timestamp": datetime.now().isoformat()
            }
    
    def risk_to_stars(self, risk_value):
        """
        将风险值转换为星级显示
        """
        if not risk_value:
            return 'N/A'
        
        try:
            risk = float(risk_value)
            if risk <= 1:
                return '⭐'
            elif risk <= 2:
                return '⭐⭐'
            elif risk <= 3:
                return '⭐⭐⭐'
            elif risk <= 4:
                return '⭐⭐⭐⭐'
            else:
                return '⭐⭐⭐⭐⭐'
        except:
            return 'N/A'
    
    def get_ticker_logo(self, ticker: str) -> str:
        """
        获取股票代码对应的logo URL
        优先使用logo.dev新平台API，失败时使用备用logo源
        """
        if not ticker:
            return "https://via.placeholder.com/80"
        
        try:
            ticker_upper = ticker.upper()
            
            # 方案1: 尝试logo.dev API (新平台)
            logo_url = f"https://img.logo.dev/ticker/{ticker_upper}?token=pk_ezLKIu-XSp2aKlPx2HnIBw&format=png&retina=true"
            
            # logo.dev API不支持HEAD请求，直接尝试GET请求验证
            import requests
            try:
                response = requests.get(logo_url, timeout=5, stream=True)
                if response.status_code == 200:
                    # 检查是否为有效的图片内容
                    content_type = response.headers.get('content-type', '')
                    if content_type.startswith('image/'):
                        self.logger.info(f"logo.dev API成功获取 {ticker} logo")
                        return logo_url
                    else:
                        self.logger.warning(f"logo.dev API返回非图片内容 for {ticker}: {content_type}")
                else:
                    self.logger.warning(f"logo.dev API返回 {response.status_code} for {ticker}")
            except Exception as e:
                self.logger.warning(f"logo.dev API无法访问 for {ticker}: {e}")
            
            # 方案2: 使用Clearbit Logos (免费备用方案)
            clearbit_url = f"https://logo.clearbit.com/{self.get_company_domain(ticker_upper)}"
            try:
                response = requests.head(clearbit_url, timeout=3)
                if response.status_code == 200:
                    return clearbit_url
            except:
                pass
            
            # 方案3: 使用Financial Modeling Prep (如果有其他API密钥)
            # fmp_url = f"https://financialmodelingprep.com/image-stock/{ticker_upper}.png"
            
            # 方案4: 预设的知名股票logo映射
            known_logos = {
                'AAPL': 'https://logo.clearbit.com/apple.com',
                'TSLA': 'https://logo.clearbit.com/tesla.com', 
                'NVDA': 'https://logo.clearbit.com/nvidia.com',
                'MSFT': 'https://logo.clearbit.com/microsoft.com',
                'GOOGL': 'https://logo.clearbit.com/google.com',
                'AMZN': 'https://logo.clearbit.com/amazon.com',
                'META': 'https://logo.clearbit.com/meta.com',
                'NFLX': 'https://logo.clearbit.com/netflix.com',
                'AMD': 'https://logo.clearbit.com/amd.com',
                'INTC': 'https://logo.clearbit.com/intel.com',
                'CRM': 'https://logo.clearbit.com/salesforce.com',
                'ORCL': 'https://logo.clearbit.com/oracle.com',
                'IBM': 'https://logo.clearbit.com/ibm.com',
                'PYPL': 'https://logo.clearbit.com/paypal.com',
                'ADBE': 'https://logo.clearbit.com/adobe.com',
                'ZM': 'https://logo.clearbit.com/zoom.us'
            }
            
            if ticker_upper in known_logos:
                return known_logos[ticker_upper]
            
            # 最终备用方案：美观的placeholder
            return f"https://ui-avatars.com/api/?name={ticker_upper}&size=80&background=random&color=fff&format=png"
            
        except Exception as e:
            self.logger.error(f"获取ticker logo失败 {ticker}: {e}")
            return "https://via.placeholder.com/80"
    
    def get_company_domain(self, ticker: str) -> str:
        """
        根据ticker获取公司域名 (用于Clearbit API)
        """
        domain_mapping = {
            'AAPL': 'apple.com',
            'TSLA': 'tesla.com',
            'NVDA': 'nvidia.com', 
            'MSFT': 'microsoft.com',
            'GOOGL': 'google.com',
            'GOOG': 'google.com',
            'AMZN': 'amazon.com',
            'META': 'meta.com',
            'NFLX': 'netflix.com',
            'AMD': 'amd.com',
            'INTC': 'intel.com',
            'CRM': 'salesforce.com',
            'ORCL': 'oracle.com',
            'IBM': 'ibm.com',
            'PYPL': 'paypal.com',
            'ADBE': 'adobe.com',
            'ZM': 'zoom.us',
            'BABA': 'alibaba.com',
            'UBER': 'uber.com',
            'SPOT': 'spotify.com',
            'TWTR': 'twitter.com',
            'SNAP': 'snapchat.com'
        }
        
        return domain_mapping.get(ticker, f"{ticker.lower()}.com")
    
    def send_trading_alert_to_user(self, user_id: str, alert_data: dict, symbol: str, timeframe: str, alert_id: int) -> bool:
        """
        发送格式化的交易Alert到Discord用户，匹配JavaScript格式
        """
        try:
            # 异步处理交易alert发送
            async def send_trading_message_async():
                try:
                    # 获取用户
                    user = self.bot.get_user(int(user_id))
                    if not user:
                        try:
                            user = await self.bot.fetch_user(int(user_id))
                        except Exception as e:
                            self.logger.error(f"无法获取用户 {user_id}: {e}")
                            return False
                    
                    if not user:
                        self.logger.error(f"未找到用户: {user_id}")
                        return False
                    
                    # 创建交易embed，完全匹配JavaScript格式
                    embed_data = self.create_trading_embed_from_data(alert_data, symbol, timeframe)
                    embed = discord.Embed.from_dict(embed_data)
                    
                    # 创建交互式按钮
                    view = TradingAlertView(alert_data, symbol, timeframe, alert_id, self.bot)
                    
                    # 发送私信带按钮
                    try:
                        await user.send(embed=embed, view=view)
                        
                        # 更新数据库状态
                        db = get_db_session()
                        alert_record = db.query(UserWebhookMessage).filter(
                            UserWebhookMessage.id == alert_id
                        ).first()
                        if alert_record:
                            alert_record.is_sent = True
                            alert_record.sent_at = datetime.now()
                            db.commit()
                        db.close()
                        
                        self.logger.info(f"成功发送交易Alert到用户 {user_id}")
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"发送交易Alert私信失败: {e}")
                        
                        # 记录发送错误
                        db = get_db_session()
                        alert_record = db.query(UserWebhookMessage).filter(
                            UserWebhookMessage.id == alert_id
                        ).first()
                        if alert_record:
                            alert_record.send_error = str(e)
                            db.commit()
                        db.close()
                        
                        return False
                        
                except Exception as e:
                    self.logger.error(f"发送交易Alert异步处理失败: {e}")
                    return False
            
            # 异步执行发送
            import asyncio
            if self.bot.loop and self.bot.loop.is_running():
                task = asyncio.create_task(send_trading_message_async())
                return True  # 立即返回，异步处理
            else:
                return asyncio.run(send_trading_message_async())
            
        except Exception as e:
            self.logger.error(f"发送交易Alert到用户失败: {e}")
            return False
    
    def send_alert_to_user(self, user_id: str, message: str, alert_id: int) -> bool:
        """
        发送Alert消息到Discord用户
        """
        try:
            # 完整的异步处理流程
            async def send_message_async():
                try:
                    # 首先尝试get_user（从缓存获取）
                    user = self.bot.get_user(int(user_id))
                    
                    # 如果缓存中没有，尝试fetch_user（从API获取）
                    if not user:
                        try:
                            user = await self.bot.fetch_user(int(user_id))
                        except Exception as e:
                            self.logger.error(f"无法获取用户 {user_id}: {e}")
                            return False
                    
                    if not user:
                        self.logger.error(f"未找到用户: {user_id}")
                        return False
                    
                    # 解析消息中的交易数据来创建正确的embed格式
                    embed_data = self.create_trading_embed(message)
                    embed = discord.Embed.from_dict(embed_data)
                    
                    # 发送私信
                    try:
                        await user.send(embed=embed)
                        
                        # 更新数据库状态
                        db = get_db_session()
                        alert_record = db.query(UserWebhookMessage).filter(
                            UserWebhookMessage.id == alert_id
                        ).first()
                        if alert_record:
                            alert_record.is_sent = True
                            alert_record.sent_at = datetime.now()
                            db.commit()
                        db.close()
                        
                        self.logger.info(f"成功发送Alert到用户 {user_id}")
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"发送私信失败: {e}")
                        
                        # 记录发送错误
                        db = get_db_session()
                        alert_record = db.query(UserWebhookMessage).filter(
                            UserWebhookMessage.id == alert_id
                        ).first()
                        if alert_record:
                            alert_record.send_error = str(e)
                            db.commit()
                        db.close()
                        
                        return False
                        
                except Exception as e:
                    self.logger.error(f"发送消息异步处理失败: {e}")
                    return False
            
            # 异步执行发送
            import asyncio
            if self.bot.loop and self.bot.loop.is_running():
                # 如果事件循环正在运行，创建任务
                task = asyncio.create_task(send_message_async())
                return True  # 立即返回，异步处理
            else:
                # 如果事件循环没有运行，同步执行
                return asyncio.run(send_message_async())
            
        except Exception as e:
            self.logger.error(f"发送Alert到用户失败: {e}")
            return False
    
    def get_user_webhook_stats(self, user_id: str) -> Dict:
        """
        获取用户webhook统计信息
        """
        try:
            db = get_db_session()
            
            # 获取webhook信息
            webhook = db.query(UserWebhook).filter(
                UserWebhook.user_id == user_id
            ).first()
            
            if not webhook:
                db.close()
                return {"exists": False}
            
            # 获取消息统计
            total_messages = db.query(UserWebhookMessage).filter(
                UserWebhookMessage.user_id == user_id
            ).count()
            
            sent_messages = db.query(UserWebhookMessage).filter(
                UserWebhookMessage.user_id == user_id,
                UserWebhookMessage.is_sent == True
            ).count()
            
            db.close()
            
            return {
                "exists": True,
                "active": webhook.is_active,
                "webhook_url": webhook.webhook_url,
                "total_messages": total_messages,
                "sent_messages": sent_messages,
                "message_count": webhook.message_count,
                "last_used": webhook.last_used.isoformat() if webhook.last_used else None,
                "created_at": webhook.created_at.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取用户webhook统计失败: {e}")
            return {"exists": False, "error": str(e)}
    
    def get_user_webhook_info(self, user_id: str) -> Tuple[bool, Dict]:
        """
        获取用户Webhook信息
        返回: (成功标志, webhook_info_or_error)
        """
        try:
            db = get_db_session()
            
            webhook = db.query(UserWebhook).filter(
                UserWebhook.user_id == user_id,
                UserWebhook.is_active == True
            ).first()
            
            if not webhook:
                db.close()
                return False, "您尚未创建个人Webhook"
            
            # 获取消息统计
            message_count = db.query(UserWebhookMessage).filter(
                UserWebhookMessage.user_id == user_id
            ).count()
            
            # 获取最后一条消息时间
            last_message = db.query(UserWebhookMessage).filter(
                UserWebhookMessage.user_id == user_id
            ).order_by(UserWebhookMessage.received_at.desc()).first()
            
            webhook_info = {
                'user_id': webhook.user_id,
                'username': webhook.username,
                'secret_token': webhook.webhook_secret,
                'webhook_url': webhook.webhook_url,
                'created_at': webhook.created_at.isoformat(),
                'updated_at': webhook.updated_at.isoformat(),
                'message_count': message_count,
                'last_message_at': last_message.received_at.isoformat() if last_message else None,
                'is_active': webhook.is_active
            }
            
            db.close()
            return True, webhook_info
            
        except Exception as e:
            self.logger.error(f"获取用户Webhook信息失败: {e}")
            return False, str(e)
    
    def delete_user_webhook(self, user_id: str) -> Tuple[bool, str]:
        """
        删除用户的Webhook
        返回: (成功标志, 错误信息)
        """
        try:
            db = get_db_session()
            
            # 查找用户的webhook
            webhook = db.query(UserWebhook).filter(
                UserWebhook.user_id == user_id
            ).first()
            
            if not webhook:
                db.close()
                return False, "未找到您的Webhook配置"
            
            # 删除相关的消息记录
            db.query(UserWebhookMessage).filter(
                UserWebhookMessage.user_id == user_id
            ).delete()
            
            # 删除webhook记录
            db.delete(webhook)
            db.commit()
            db.close()
            
            self.logger.info(f"删除用户 {user_id} 的webhook及相关消息")
            return True, ""
            
        except Exception as e:
            self.logger.error(f"删除用户Webhook失败: {e}")
            return False, str(e)
