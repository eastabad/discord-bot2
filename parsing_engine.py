#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立解析引擎
每个字段的判断条件可通过可视化界面配置，解析结果用于AI模板生成
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import re


class FieldParser:
    """单个字段解析器"""
    
    def __init__(self, field_name: str, config: Dict[str, Any]):
        self.field_name = field_name
        self.config = config
        self.conditions = config.get('conditions', [])
        self.default_output = config.get('default_output', '')
    
    def parse(self, data: Dict[str, Any]) -> str:
        """
        根据配置的条件解析字段
        返回解析后的文本内容
        """
        field_value = data.get(self.field_name)
        
        if field_value is None:
            return self.default_output
        
        # 遍历所有条件，找到匹配的
        for condition in self.conditions:
            if self._match_condition(field_value, condition):
                return self._format_output(condition['output'], data, field_value)
        
        # 没有匹配条件时返回默认输出
        return self.default_output or str(field_value)
    
    def _match_condition(self, value: Any, condition: Dict[str, Any]) -> bool:
        """检查值是否匹配条件"""
        condition_type = condition.get('type', 'equals')
        condition_value = condition.get('value')
        
        if condition_type == 'equals':
            return str(value) == str(condition_value)
        elif condition_type == 'contains':
            return str(condition_value).lower() in str(value).lower()
        elif condition_type == 'starts_with':
            return str(value).lower().startswith(str(condition_value).lower())
        elif condition_type == 'ends_with':
            return str(value).lower().endswith(str(condition_value).lower())
        elif condition_type == 'regex':
            try:
                return bool(re.match(condition_value, str(value)))
            except re.error:
                return False
        elif condition_type == 'greater_than':
            try:
                return float(value) > float(condition_value)
            except (ValueError, TypeError):
                return False
        elif condition_type == 'less_than':
            try:
                return float(value) < float(condition_value)
            except (ValueError, TypeError):
                return False
        elif condition_type == 'range':
            try:
                min_val = float(condition_value.get('min', float('-inf')))
                max_val = float(condition_value.get('max', float('inf')))
                return min_val <= float(value) <= max_val
            except (ValueError, TypeError):
                return False
        
        return False
    
    def _format_output(self, output_template: str, data: Dict[str, Any], field_value: Any) -> str:
        """格式化输出文本，支持变量替换"""
        # 基本变量替换
        formatted = output_template.replace('{value}', str(field_value))
        formatted = formatted.replace('{field}', self.field_name)
        
        # 支持其他字段的变量替换
        for key, value in data.items():
            formatted = formatted.replace(f'{{{key}}}', str(value))
        
        return formatted


class ParsingEngine:
    """解析引擎主类"""
    
    def __init__(self, config_dir: str = 'config'):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, 'parsing_rules.json')
        self.parsers = {}
        self._load_config()
    
    def _load_config(self):
        """加载解析配置"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 为每个字段创建解析器
            for field_name, field_config in config.get('fields', {}).items():
                self.parsers[field_name] = FieldParser(field_name, field_config)
            
            print(f"✅ 解析引擎配置已加载，共 {len(self.parsers)} 个字段解析器")
            
        except Exception as e:
            print(f"❌ 加载解析配置失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认配置"""
        default_config = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "fields": {
                "CVDsignal": {
                    "description": "CVD信号解析",
                    "conditions": [
                        {
                            "type": "equals",
                            "value": "cvdAboveMA",
                            "output": "CVD显示强烈买压，资金大量流入，机构积极建仓"
                        },
                        {
                            "type": "equals", 
                            "value": "cvdBelowMA",
                            "output": "CVD显示卖压增加，资金流出明显，需要谨慎观察"
                        }
                    ],
                    "default_output": "CVD信号: {value}"
                },
                "pmaText": {
                    "description": "PMA趋势强度解析",
                    "conditions": [
                        {
                            "type": "contains",
                            "value": "Strong Bullish",
                            "output": "PMA显示强劲上涨动能，多头趋势非常明确，建议积极关注"
                        },
                        {
                            "type": "contains",
                            "value": "Bullish", 
                            "output": "PMA显示看涨信号，上涨趋势初步确立"
                        },
                        {
                            "type": "contains",
                            "value": "Bearish",
                            "output": "PMA显示下跌信号，空头力量占据主导"
                        },
                        {
                            "type": "contains",
                            "value": "Strong Bearish",
                            "output": "PMA显示强烈下跌动能，建议规避风险"
                        }
                    ],
                    "default_output": "PMA趋势: {value}"
                },
                "signal": {
                    "description": "交易信号解析",
                    "conditions": [
                        {
                            "type": "equals",
                            "value": "BUY",
                            "output": "系统发出买入信号，多个技术指标汇聚支持上涨"
                        },
                        {
                            "type": "equals",
                            "value": "SELL", 
                            "output": "系统发出卖出信号，技术面转向看空"
                        },
                        {
                            "type": "equals",
                            "value": "HOLD",
                            "output": "建议持有观望，等待更明确的方向信号"
                        }
                    ],
                    "default_output": "交易信号: {value}"
                },
                "close": {
                    "description": "价格解析",
                    "conditions": [
                        {
                            "type": "greater_than",
                            "value": 1000,
                            "output": "当前价格 ${value}，处于高价位区间"
                        },
                        {
                            "type": "range",
                            "value": {"min": 100, "max": 1000},
                            "output": "当前价格 ${value}，处于中等价位区间"
                        }
                    ],
                    "default_output": "当前价格: ${value}"
                },
                "timeframe": {
                    "description": "时间框架解析",
                    "conditions": [
                        {
                            "type": "equals",
                            "value": "1H",
                            "output": "基于1小时级别分析，适合短线交易"
                        },
                        {
                            "type": "equals",
                            "value": "4H", 
                            "output": "基于4小时级别分析，适合中短线操作"
                        },
                        {
                            "type": "equals",
                            "value": "1D",
                            "output": "基于日线级别分析，适合中长线布局"
                        }
                    ],
                    "default_output": "分析周期: {value}"
                },
                "poc_summary": {
                    "description": "POC价格汇总解析",
                    "conditions": [
                        {
                            "type": "contains",
                            "value": "Daily POC:",
                            "output": "POC分析显示关键价格水平：{value}，这些是机构重点关注的成交密集区域，价格在这些水平附近容易形成支撑或阻力"
                        }
                    ],
                    "default_output": "POC价格信息: {value}"
                },
                "POCtrend": {
                    "description": "POC趋势信号解析",
                    "conditions": [
                        {
                            "type": "equals",
                            "value": "3",
                            "output": "POC显示超强多头趋势：价格大幅突破所有周期POC，多头动能极其强劲，适合追涨策略"
                        },
                        {
                            "type": "equals",
                            "value": "2",
                            "output": "POC显示强势多头趋势：价格站上所有周期的POC，短中长期共振，多头主导市场"
                        },
                        {
                            "type": "equals",
                            "value": "1",
                            "output": "POC显示温和多头趋势：价格突破部分POC水平，上涨动能开始显现"
                        },
                        {
                            "type": "equals",
                            "value": "0",
                            "output": "POC显示震荡状态：价格围绕POC水平震荡，多空力量相对平衡"
                        },
                        {
                            "type": "equals",
                            "value": "-1",
                            "output": "POC显示温和空头趋势：价格跌破部分POC水平，下跌动能开始显现"
                        },
                        {
                            "type": "equals",
                            "value": "-2",
                            "output": "POC显示强势空头趋势：价格跌破所有周期的POC，短中长期共振，空头主导市场"
                        },
                        {
                            "type": "equals",
                            "value": "-3",
                            "output": "POC显示超强空头趋势：价格大幅跌破所有周期POC，空头动能极其强劲，适合做空策略"
                        }
                    ],
                    "default_output": "POC趋势信号: {value}"
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 默认解析配置已创建: {self.config_file}")
    
    def parse_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        解析完整数据，返回每个字段的解析结果
        """
        results = {}
        
        for field_name, parser in self.parsers.items():
            if field_name in data:
                results[f"{field_name}_parsed"] = parser.parse(data)
                results[f"{field_name}_raw"] = str(data[field_name])
        
        return results
    
    def get_parsed_summary(self, data: Dict[str, Any]) -> str:
        """
        获取解析结果的汇总文本，用于AI模板
        """
        parsed_results = self.parse_data(data)
        
        summary_parts = []
        for key, value in parsed_results.items():
            if key.endswith('_parsed'):
                summary_parts.append(value)
        
        return '\n'.join(summary_parts)
    
    def reload_config(self):
        """重新加载配置"""
        self.parsers.clear()
        self._load_config()
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 读取配置失败: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            config['updated_at'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 重新加载解析器
            self.reload_config()
            return True
            
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False


# 全局解析引擎实例
_parsing_engine = None

def get_parsing_engine() -> ParsingEngine:
    """获取全局解析引擎实例"""
    global _parsing_engine
    if _parsing_engine is None:
        _parsing_engine = ParsingEngine()
    return _parsing_engine


# 测试函数
if __name__ == "__main__":
    # 创建测试数据
    test_data = {
        "ticker": "TSLA",
        "CVDsignal": "cvdAboveMA",
        "pmaText": "PMA Strong Bullish", 
        "signal": "BUY",
        "close": "250.45",
        "timeframe": "1H"
    }
    
    # 测试解析引擎
    engine = get_parsing_engine()
    
    print("原始数据:")
    print(json.dumps(test_data, indent=2))
    
    print("\n解析结果:")
    parsed_results = engine.parse_data(test_data)
    for key, value in parsed_results.items():
        print(f"{key}: {value}")
    
    print("\n汇总文本:")
    summary = engine.get_parsed_summary(test_data)
    print(summary)