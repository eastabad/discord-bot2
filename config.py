"""
配置管理模块
用于加载和验证Discord Bot的配置信息
"""
import os
import logging
from typing import List, Optional

class Config:
    """Discord Bot配置类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 加载.env文件
        self._load_env_file()
        
        # 必需配置
        self.discord_token = os.getenv('DISCORD_TOKEN')
        
        # 频道配置
        monitor_ids = os.getenv('MONITOR_CHANNEL_IDS') or os.getenv('MONITOR_CHANNEL_ID', '')
        self.monitor_channel_ids = [id.strip() for id in monitor_ids.split(',') if id.strip()]
        
        report_ids = os.getenv('REPORT_CHANNEL_IDS') or os.getenv('REPORT_CHANNEL_ID', '')
        self.report_channel_ids = [id.strip() for id in report_ids.split(',') if id.strip()]
        
        chart_ids = os.getenv('CHART_CHANNEL_IDS') or os.getenv('CHART_CHANNEL_ID', '')
        self.chart_channel_ids = [id.strip() for id in chart_ids.split(',') if id.strip()]
        
        # API密钥
        self.chart_img_api_key = os.getenv('CHART_IMG_API_KEY')
        self.layout_id = os.getenv('LAYOUT_ID', '2051')
        self.ob_layout_id = os.getenv('OB_LAYOUT_ID', '2052')  # OB命令专用布局ID
        
        # TradingView配置 (Chart-img API会话信息，可选)
        self.tv_session = os.getenv('TRADINGVIEW_SESSION')  # 兼容性保留
        self.tradingview_session_id = os.getenv('TRADINGVIEW_SESSION_ID')
        self.tradingview_session_id_sign = os.getenv('TRADINGVIEW_SESSION_ID_SIGN')
        
        # 调试信息
        if self.tradingview_session_id:
            self.logger.info(f'TradingView Session ID已配置 (长度: {len(self.tradingview_session_id)})')
        if self.tradingview_session_id_sign:
            self.logger.info(f'TradingView Session Sign已配置 (长度: {len(self.tradingview_session_id_sign)})')
        
        # 可选配置
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.database_url = os.getenv('DATABASE_URL')
        
        # AI API密钥
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
        # 系统配置
        self.request_limit = int(os.getenv('REQUEST_LIMIT', '5'))
        self.enable_vip = os.getenv('ENABLE_VIP', 'false').lower() == 'true'
        self.enable_chart_cleanup = os.getenv('ENABLE_CHART_CLEANUP', 'true').lower() == 'true'
        
        # 可选配置
        self.log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.webhook_timeout = int(os.getenv('WEBHOOK_TIMEOUT', '30'))
        self.command_prefix = os.getenv('COMMAND_PREFIX', '!')
        
        # 验证必需配置
        self._validate_config()
        
    def _load_env_file(self):
        """加载.env文件"""
        env_file = '.env'
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            self.logger.info('成功加载.env文件')
        
    def _validate_config(self):
        """验证配置"""
        errors = []
        
        if not self.discord_token:
            errors.append('DISCORD_TOKEN未设置')
            
        # WEBHOOK_URL是可选的，只有设置了才验证格式
        if self.webhook_url and not self.webhook_url.startswith(('http://', 'https://')):
            errors.append('WEBHOOK_URL必须是有效的HTTP(S) URL')
            
        if not self.monitor_channel_ids:
            errors.append('MONITOR_CHANNEL_IDS或MONITOR_CHANNEL_ID未设置')
            
        if self.max_retries < 1:
            errors.append('MAX_RETRIES必须大于0')
            
        if self.webhook_timeout < 1:
            errors.append('WEBHOOK_TIMEOUT必须大于0')
            
        if errors:
            error_msg = '配置验证失败:\n' + '\n'.join(f'- {error}' for error in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        self.logger.info('配置验证通过')
        
    def get_summary(self) -> dict:
        """获取配置摘要（隐藏敏感信息）"""
        return {
            'discord_token': '***已设置***' if self.discord_token else '未设置',
            'webhook_url': self._mask_url(self.webhook_url) if self.webhook_url else '未设置',
            'log_level': self.log_level,
            'max_retries': self.max_retries,
            'webhook_timeout': self.webhook_timeout,
            'command_prefix': self.command_prefix
        }
        
    def _mask_url(self, url: str) -> str:
        """掩码URL中的敏感信息"""
        if not url:
            return url
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            # 掩码主机名中间部分
            if parsed.hostname:
                hostname = parsed.hostname
                if len(hostname) > 6:
                    masked_hostname = hostname[:3] + '***' + hostname[-3:]
                else:
                    masked_hostname = '***'
                
                return f"{parsed.scheme}://{masked_hostname}{parsed.path}"
            
            return url[:10] + '***' + url[-5:] if len(url) > 15 else '***'
            
        except Exception:
            return '***URL***'

# 全局配置实例
config = None

def get_config() -> Config:
    """获取配置实例（单例模式）"""
    global config
    if config is None:
        config = Config()
    return config

def load_config() -> Config:
    """重新加载配置"""
    global config
    config = Config()
    return config