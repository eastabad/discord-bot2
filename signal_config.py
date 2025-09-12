#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SignalMapping:
    """信号映射配置"""
    signal_type: str
    signal_value: str
    chinese_description: str
    created_at: str = ""
    updated_at: str = ""

@dataclass
class AITemplate:
    """AI模板配置"""
    template_name: str
    command_type: str  # CT, RP, IMAGE, PREDICT
    template_content: str
    description: str = ""
    created_at: str = ""
    updated_at: str = ""

class SignalConfigManager:
    """信号配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.signal_mappings_file = os.path.join(config_dir, "signal_mappings.json")
        self.ai_templates_file = os.path.join(config_dir, "ai_templates.json")
        
        # 确保配置目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 初始化默认配置
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """初始化默认配置"""
        # 初始化默认信号映射
        if not os.path.exists(self.signal_mappings_file):
            default_mappings = [
                # CVD信号映射
                SignalMapping("CVDsignal", "cvdAboveMA", "CVD 高于移动平均线 (买压增加，资金流入)"),
                SignalMapping("CVDsignal", "cvdBelowMA", "CVD 低于移动平均线 (卖压增加，资金流出)"),
                
                # PMA信号映射
                SignalMapping("pmaText", "PMA Strong Bullish", "PMA 强烈看涨"),
                SignalMapping("pmaText", "PMA Bullish", "PMA 看涨"),
                SignalMapping("pmaText", "PMA Trendless", "PMA 无明确趋势"),
                SignalMapping("pmaText", "PMA Bearish", "PMA 看跌"),
                SignalMapping("pmaText", "PMA Strong Bearish", "PMA 强烈看跌"),
                
                # 趋势信号映射
                SignalMapping("trendSignal", "STRONG_BULLISH", "强烈看涨趋势"),
                SignalMapping("trendSignal", "BULLISH", "看涨趋势"),
                SignalMapping("trendSignal", "NEUTRAL", "中性趋势"),
                SignalMapping("trendSignal", "BEARISH", "看跌趋势"),
                SignalMapping("trendSignal", "STRONG_BEARISH", "强烈看跌趋势"),
                
                # 信号强度映射
                SignalMapping("signalStrength", "VERY_STRONG", "非常强"),
                SignalMapping("signalStrength", "STRONG", "强"),
                SignalMapping("signalStrength", "MODERATE", "中等"),
                SignalMapping("signalStrength", "WEAK", "弱"),
                SignalMapping("signalStrength", "VERY_WEAK", "非常弱"),
                
                # 交易信号映射
                SignalMapping("signal", "BUY", "买入信号"),
                SignalMapping("signal", "SELL", "卖出信号"),
                SignalMapping("signal", "HOLD", "持有信号"),
                SignalMapping("signal", "WAIT", "等待信号"),
            ]
            
            self.save_signal_mappings(default_mappings)
        
        # 初始化默认AI模板
        if not os.path.exists(self.ai_templates_file):
            default_templates = [
                AITemplate(
                    template_name="图表分析模板",
                    command_type="CT",
                    template_content="""请分析这张股票图表，提供以下信息：
1. 技术指标分析
2. 趋势判断
3. 关键支撑阻力位
4. 交易建议
5. 风险评估

图表数据：{chart_data}
当前价格：{current_price}
技术指标：{technical_indicators}""",
                    description="用于图表请求的AI分析模板"
                ),
                
                AITemplate(
                    template_name="报告生成模板",
                    command_type="RP",
                    template_content="""基于以下数据生成详细的股票分析报告：

股票代码：{ticker}
当前价格：{current_price}
历史数据：{historical_data}
技术指标：{technical_indicators}
市场情绪：{market_sentiment}

请提供：
1. 执行摘要
2. 技术分析
3. 基本面分析
4. 投资建议
5. 风险提示
6. 目标价格预测""",
                    description="用于报告请求的AI分析模板"
                ),
                
                AITemplate(
                    template_name="图像分析模板",
                    command_type="IMAGE",
                    template_content="""请分析这张图像中的技术分析内容：

图像内容：{image_description}
分析要点：
1. 识别图表类型和时间框架
2. 分析价格走势和模式
3. 识别技术指标信号
4. 评估支撑阻力位
5. 提供交易观点

请用专业的技术分析语言描述您的发现。""",
                    description="用于图像分析的AI模板"
                ),
                
                AITemplate(
                    template_name="预测分析模板",
                    command_type="PREDICT",
                    template_content="""基于以下数据进行股票价格预测：

股票代码：{ticker}
历史价格数据：{price_data}
技术指标：{indicators}
市场环境：{market_conditions}
新闻情绪：{news_sentiment}

预测要求：
1. 短期预测（1-7天）
2. 中期预测（1-4周）
3. 长期预测（1-3个月）
4. 关键价格区间
5. 概率评估
6. 风险因素""",
                    description="用于价格预测的AI模板"
                )
            ]
            
            self.save_ai_templates(default_templates)
    
    def load_signal_mappings(self) -> Dict[str, Dict[str, str]]:
        """加载信号映射配置"""
        try:
            with open(self.signal_mappings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换为嵌套字典格式
            mappings = {}
            for item in data:
                signal_type = item['signal_type']
                if signal_type not in mappings:
                    mappings[signal_type] = {}
                mappings[signal_type][item['signal_value']] = item['chinese_description']
            
            return mappings
        except Exception as e:
            print(f"加载信号映射失败: {e}")
            return {}
    
    def save_signal_mappings(self, mappings: list):
        """保存信号映射配置"""
        try:
            # 添加时间戳
            current_time = datetime.now().isoformat()
            for mapping in mappings:
                if not mapping.created_at:
                    mapping.created_at = current_time
                mapping.updated_at = current_time
            
            # 转换为字典列表
            data = [asdict(mapping) for mapping in mappings]
            
            with open(self.signal_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 信号映射配置已保存到 {self.signal_mappings_file}")
        except Exception as e:
            print(f"❌ 保存信号映射失败: {e}")
    
    def load_ai_templates(self) -> Dict[str, str]:
        """加载AI模板配置"""
        try:
            with open(self.ai_templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 转换为字典格式 {command_type: template_content}
            templates = {}
            for item in data:
                templates[item['command_type']] = item['template_content']
            
            return templates
        except Exception as e:
            print(f"加载AI模板失败: {e}")
            return {}
    
    def save_ai_templates(self, templates: list):
        """保存AI模板配置"""
        try:
            # 添加时间戳
            current_time = datetime.now().isoformat()
            for template in templates:
                if not template.created_at:
                    template.created_at = current_time
                template.updated_at = current_time
            
            # 转换为字典列表
            data = [asdict(template) for template in templates]
            
            with open(self.ai_templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ AI模板配置已保存到 {self.ai_templates_file}")
        except Exception as e:
            print(f"❌ 保存AI模板失败: {e}")
    
    def translate_signal(self, signal_type: str, signal_value: str) -> str:
        """将信号值翻译为中文描述"""
        mappings = self.load_signal_mappings()
        
        if signal_type in mappings and signal_value in mappings[signal_type]:
            return mappings[signal_type][signal_value]
        
        # 如果没找到映射，返回原值
        return signal_value
    
    def get_ai_template(self, command_type: str) -> str:
        """获取指定命令类型的AI模板"""
        templates = self.load_ai_templates()
        return templates.get(command_type, "")
    
    def add_signal_mapping(self, signal_type: str, signal_value: str, chinese_description: str):
        """添加新的信号映射"""
        try:
            # 加载现有映射
            with open(self.signal_mappings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 添加新映射
            new_mapping = SignalMapping(
                signal_type=signal_type,
                signal_value=signal_value,
                chinese_description=chinese_description,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            data.append(asdict(new_mapping))
            
            # 保存
            with open(self.signal_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 添加信号映射: {signal_type}.{signal_value} -> {chinese_description}")
        except Exception as e:
            print(f"❌ 添加信号映射失败: {e}")
    
    def update_ai_template(self, command_type: str, template_content: str, description: str = ""):
        """更新AI模板"""
        try:
            # 加载现有模板
            with open(self.ai_templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 查找并更新模板
            updated = False
            for item in data:
                if item['command_type'] == command_type:
                    item['template_content'] = template_content
                    if description:
                        item['description'] = description
                    item['updated_at'] = datetime.now().isoformat()
                    updated = True
                    break
            
            # 如果没找到，添加新模板
            if not updated:
                new_template = AITemplate(
                    template_name=f"{command_type}模板",
                    command_type=command_type,
                    template_content=template_content,
                    description=description,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                data.append(asdict(new_template))
            
            # 保存
            with open(self.ai_templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 更新AI模板: {command_type}")
        except Exception as e:
            print(f"❌ 更新AI模板失败: {e}")

# 全局配置管理器实例
signal_config_manager = SignalConfigManager()

def translate_webhook_data(webhook_data: dict) -> dict:
    """翻译webhook数据中的信号为中文"""
    translated_data = webhook_data.copy()
    
    # 遍历数据，查找需要翻译的字段
    for key, value in webhook_data.items():
        if isinstance(value, str):
            # 尝试翻译常见的信号字段
            if key in ['CVDsignal', 'pmaText', 'trendSignal', 'signalStrength', 'signal', 'obData']:
                translated_value = signal_config_manager.translate_signal(key, value)
                translated_data[f"{key}_zh"] = translated_value
    
    return translated_data

def get_ai_prompt_template(command_type: str) -> str:
    """获取AI提示词模板"""
    return signal_config_manager.get_ai_template(command_type)

if __name__ == "__main__":
    # 测试信号翻译
    test_data = {
        "ticker": "AAPL",
        "CVDsignal": "cvdAboveMA",
        "pmaText": "PMA Strong Bullish",
        "signal": "BUY"
    }
    
    translated = translate_webhook_data(test_data)
    print("翻译测试:")
    print(json.dumps(translated, ensure_ascii=False, indent=2))
    
    # 测试模板获取
    ct_template = get_ai_prompt_template("CT")
    print(f"\nCT模板:\n{ct_template}")