#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多AI模型服务管理器
支持 Gemini 2.5 Pro (主), Claude Sonnet 4 (备用1), GPT-4.1 (备用2)
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# 导入Google Gemini (新版统一SDK)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    GENAI_AVAILABLE = False

# 移除旧版SDK，只使用新版统一SDK

@dataclass
class AIModelConfig:
    """AI模型配置"""
    name: str
    provider: str
    model_id: str
    max_tokens: int
    temperature: float
    enabled: bool = True

class MultiAIService:
    """多AI模型服务管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 配置AI模型列表（按新的优先级排序：Account 2 优先）
        self.models = [
            AIModelConfig(
                name="Gemini 2.5 Pro (Account 2)",
                provider="google_alt",
                model_id="gemini-2.5-pro",
                max_tokens=4096,
                temperature=0.7
            ),
            AIModelConfig(
                name="Gemini 2.5 Flash (Account 2)",
                provider="google_alt",
                model_id="gemini-2.5-flash",
                max_tokens=4096,
                temperature=0.7
            ),
            AIModelConfig(
                name="Gemini 2.5 Pro (Account 1)",
                provider="google",
                model_id="gemini-2.5-pro",
                max_tokens=4096,
                temperature=0.7
            ),
            AIModelConfig(
                name="Gemini 2.5 Flash (Account 1)",
                provider="google",
                model_id="gemini-2.5-flash",
                max_tokens=4096,
                temperature=0.7
            ),
            AIModelConfig(
                name="Claude Sonnet 4 (Direct)",
                provider="anthropic",
                model_id="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.7
            )
        ]
        
        # 初始化API密钥
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.gemini_api_key_alt = os.environ.get("GEMINI_API_KEY_2")  # 第二个账户
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        # 初始化Anthropic客户端
        self.anthropic_client = None
        if self.anthropic_api_key:
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
                self.logger.info("✅ Anthropic API直连已配置")
            except ImportError:
                self.logger.warning("⚠️ Anthropic库未安装，跳过直连配置")
        
        # 初始化Gemini客户端 (双账户)
        self.gemini_client = None
        self.gemini_client_alt = None

        self._init_gemini()
        
        # 验证模型可用性
        self._validate_models()
        
        self.logger.info(f"✅ 多AI服务初始化完成，可用模型: {len([m for m in self.models if m.enabled])}")
    
    def _init_gemini(self):
        """初始化Gemini客户端 (双账户支持)"""
        # 初始化第一个账户 (新版SDK)
        if self.gemini_api_key and GENAI_AVAILABLE:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                self.logger.info("✅ Gemini Account 1 初始化成功 (新版SDK)")
            except Exception as e:
                self.logger.error(f"❌ Gemini Account 1 初始化失败: {e}")
                
        # 初始化第二个账户 (新版SDK)
        if self.gemini_api_key_alt and GENAI_AVAILABLE:
            try:
                self.gemini_client_alt = genai.Client(api_key=self.gemini_api_key_alt)
                self.logger.info("✅ Gemini Account 2 初始化成功 (新版SDK)")
            except Exception as e:
                self.logger.error(f"❌ Gemini Account 2 初始化失败: {e}")
                
        # 验证至少有一个Gemini客户端可用
        if not (self.gemini_client or self.gemini_client_alt):
            self.logger.warning("❌ 没有可用的Gemini客户端")
            # 禁用所有Gemini模型
            for model in self.models:
                if model.provider in ["google", "google_alt"]:
                    model.enabled = False
    
    def _validate_models(self):
        """验证模型可用性"""
        # 验证Anthropic直连
        if not self.anthropic_client:
            self.logger.warning("❌ Anthropic直连未配置")
            # 禁用Anthropic直连模型
            for model in self.models:
                if model.provider == "anthropic":
                    model.enabled = False
        else:
            self.logger.info("✅ Anthropic直连已配置")
            
        # 验证Gemini客户端
        available_gemini = sum([
            1 if self.gemini_client else 0,
            1 if self.gemini_client_alt else 0
        ])
        self.logger.info(f"✅ 可用Gemini客户端数量: {available_gemini}")
    
    def generate_report(self, prompt: str, symbol: str = "", context: str = "") -> Dict[str, Any]:
        """
        使用多AI模型生成报告（按优先级尝试）
        
        Args:
            prompt: 分析提示词
            symbol: 股票代码
            context: 额外上下文
        
        Returns:
            包含报告内容和元数据的字典
        """
        errors = []
        
        for i, model in enumerate(self.models):
            if not model.enabled:
                continue
                
            try:
                self.logger.info(f"🤖 尝试使用 {model.name} 生成报告...")
                
                if model.provider == "google":
                    result = self._generate_with_gemini(prompt, model, use_alt_account=False)
                elif model.provider == "google_alt":
                    result = self._generate_with_gemini(prompt, model, use_alt_account=True)
                elif model.provider == "anthropic":
                    result = self._generate_with_anthropic(prompt, model)
                else:
                    continue
                
                if result and result.get('success'):
                    self.logger.info(f"✅ {model.name} 成功生成报告，长度: {len(result['content'])}")
                    return {
                        'success': True,
                        'content': result['content'],
                        'model_used': model.name,
                        'provider': model.provider,
                        'symbol': symbol,
                        'attempt': i + 1,
                        'total_attempts': len([m for m in self.models if m.enabled])
                    }
                else:
                    error_msg = result.get('error', '未知错误') if result else '返回空结果'
                    errors.append(f"{model.name}: {error_msg}")
                    self.logger.warning(f"⚠️ {model.name} 生成失败: {error_msg}")
                    
            except Exception as e:
                error_msg = str(e)
                errors.append(f"{model.name}: {error_msg}")
                self.logger.error(f"❌ {model.name} 调用异常: {e}")
        
        # 所有模型都失败，返回技术分析备用报告
        self.logger.error("❌ 所有AI模型都失败，生成技术分析备用报告")
        return {
            'success': False,
            'content': self._generate_technical_fallback(symbol, prompt),
            'model_used': 'Technical Fallback',
            'provider': 'internal',
            'symbol': symbol,
            'errors': errors,
            'total_attempts': len([m for m in self.models if m.enabled])
        }
    
    def _generate_with_gemini(self, prompt: str, model_config: AIModelConfig, use_alt_account: bool = False) -> Dict[str, Any]:
        """使用Gemini生成内容 (新版SDK + 双账户支持)"""
        # 选择客户端
        if use_alt_account:
            client = self.gemini_client_alt
            account_name = "Account 2"
        else:
            client = self.gemini_client
            account_name = "Account 1"
            
        if not client:
            return {'success': False, 'error': f'Gemini {account_name} 客户端未初始化'}
            
        try:
            max_retries = 2
            
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"使用 {account_name} 新版SDK，模型: {model_config.model_id}")
                    
                    # 按照官方文档格式调用
                    response = client.models.generate_content(
                        model=model_config.model_id,
                        contents=prompt
                    )
                    
                    if response and response.text:
                        return {
                            'success': True,
                            'content': response.text,
                            'account': account_name,
                            'sdk': 'new',
                            'model': model_config.model_id
                        }
                    else:
                        if attempt < max_retries - 1:
                            self.logger.warning(f"{account_name} 新版SDK响应为空，重试 {attempt + 1}/{max_retries}")
                            continue
                            
                except Exception as e:
                    error_str = str(e)
                    self.logger.warning(f"{account_name} 新版SDK尝试 {attempt + 1} 失败: {error_str}")
                    
                    if "500" in error_str or "INTERNAL" in error_str.upper():
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(2)
                            continue
                    elif "quota" in error_str.lower() or "429" in error_str:
                        break  # 配额用完，不重试
                        
            return {'success': False, 'error': f'{account_name} 新版SDK失败'}
            
        except Exception as e:
            return {'success': False, 'error': f'{account_name} 调用异常: {str(e)}'}
    
    def _generate_with_anthropic(self, prompt: str, model_config: AIModelConfig) -> Dict[str, Any]:
        """使用Anthropic直连生成内容"""
        if not self.anthropic_client:
            return {'success': False, 'error': 'Anthropic客户端未初始化'}
            
        try:
            # 构建系统提示和用户提示
            system_prompt = "你是一个专业的股票技术分析师，擅长解读技术指标和市场趋势，能够生成结构化的中文交易分析报告。"
            
            # 调用Anthropic API
            response = self.anthropic_client.messages.create(
                model=model_config.model_id,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # 提取内容
            if response and response.content and len(response.content) > 0:
                # Anthropic返回的是一个content list，通常第一个是text块
                content_block = response.content[0]
                if hasattr(content_block, 'text'):
                    return {'success': True, 'content': content_block.text}
                else:
                    return {'success': False, 'error': '响应内容格式异常'}
            else:
                return {'success': False, 'error': '未收到有效响应'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_with_openrouter(self, prompt: str, model_config: AIModelConfig) -> Dict[str, Any]:
        """使用OpenRouter生成内容"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://discord-trading-bot.replit.app",
                "X-Title": "Discord Trading Bot"
            }
            
            # 构建消息格式
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的股票技术分析师，擅长解读技术指标和市场趋势，能够生成结构化的中文交易分析报告。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            data = {
                "model": model_config.model_id,
                "messages": messages,
                "temperature": model_config.temperature,
                "max_tokens": model_config.max_tokens,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    return {'success': True, 'content': content}
                else:
                    return {'success': False, 'error': '响应中未找到有效内容'}
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        error_msg += f": {error_detail['error'].get('message', '未知错误')}"
                except:
                    pass
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_technical_fallback(self, symbol: str, prompt: str) -> str:
        """生成技术分析备用报告"""
        return f"""## 📈 {symbol} 技术分析报告
        
⚠️ **系统提示**: 当前AI分析服务暂时不可用，以下为基于技术指标的基础分析报告。

## 🔑 关键交易信号
基于最新的技术指标数据，当前检测到以下关键信号：
- 系统正在分析多个时间框架的技术指标
- 建议关注主要趋势线和支撑阻力位
- 请结合实时市场数据进行综合判断

## 📉 趋势分析
**趋势总结**: 建议查看最新的技术指标组合分析
**当前波动**: 关注成交量和价格行为的配合情况
**市场状态**: 请结合多个技术指标进行综合评估

## 💡 投资建议
由于AI分析服务暂时不可用，建议：
1. 密切关注技术指标的实时变化
2. 结合基本面分析进行投资决策  
3. 设置合理的止损止盈位置
4. 控制仓位规模，管理风险

## ⚠️ 风险提示
- 技术分析存在滞后性，请结合多种分析方法
- 市场变化迅速，建议实时监控
- 投资有风险，请根据个人风险承受能力决策
- 本报告仅供参考，不构成投资建议

---
*系统将自动尝试恢复AI分析功能，请稍后重试*"""
    
    def get_status(self) -> Dict[str, Any]:
        """获取多AI服务状态"""
        return {
            'models': [
                {
                    'name': model.name,
                    'provider': model.provider,
                    'model_id': model.model_id,
                    'enabled': model.enabled,
                    'status': 'available' if model.enabled else 'unavailable'
                }
                for model in self.models
            ],
            'total_models': len(self.models),
            'available_models': len([m for m in self.models if m.enabled]),
            'gemini_configured': bool(self.gemini_api_key),
            'openrouter_configured': bool(self.openrouter_api_key)
        }

# 全局实例
multi_ai_service = None

def get_multi_ai_service():
    """获取多AI服务实例（单例模式）"""
    global multi_ai_service
    if multi_ai_service is None:
        multi_ai_service = MultiAIService()
    return multi_ai_service