#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI模板引擎
整合解析引擎的结果到AI提示词模板中，生成最终的AI提示
"""

import json
import os
from typing import Dict, Any, Optional
from parsing_engine import get_parsing_engine


class AITemplateEngine:
    """AI模板引擎"""
    
    def __init__(self, config_dir: str = 'config'):
        self.config_dir = config_dir
        self.templates_file = os.path.join(config_dir, 'ai_templates.json')
        self.parsing_engine = get_parsing_engine()
    
    def get_template(self, command_type: str, template_name: Optional[str] = None) -> Optional[str]:
        """
        获取AI模板
        Args:
            command_type: 命令类型 (CT, RP, IMAGE, PREDICT)
            template_name: 可选的特定模板名称
        Returns:
            模板内容字符串
        """
        try:
            if not os.path.exists(self.templates_file):
                return None
                
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # 按命令类型筛选模板
            matching_templates = [
                t for t in templates 
                if t.get('command_type') == command_type
            ]
            
            if not matching_templates:
                return None
            
            # 如果指定了模板名称，查找具体模板
            if template_name:
                for template in matching_templates:
                    if template.get('template_name') == template_name:
                        return template.get('template_content')
            
            # 返回第一个匹配的模板
            return matching_templates[0].get('template_content')
            
        except Exception as e:
            print(f"❌ 获取AI模板失败: {e}")
            return None
    
    def generate_ai_prompt(self, command_type: str, data: Dict[str, Any], 
                          template_name: Optional[str] = None, 
                          additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        生成AI提示词
        Args:
            command_type: 命令类型 (CT, RP, IMAGE, PREDICT)
            data: 原始数据
            template_name: 可选的特定模板名称
            additional_context: 额外的上下文数据
        Returns:
            完整的AI提示词
        """
        # 获取模板
        template = self.get_template(command_type, template_name)
        if not template:
            return f"未找到 {command_type} 类型的AI模板"
        
        # 解析数据
        parsed_results = self.parsing_engine.parse_data(data)
        summary_text = self.parsing_engine.get_parsed_summary(data)
        
        # 准备变量替换字典
        template_vars = {
            # 原始数据
            **data,
            # 解析结果
            **parsed_results,
            # 汇总文本
            'parsed_summary': summary_text,
            'analysis_summary': summary_text,
            'technical_analysis': summary_text,
            # 额外上下文
            **(additional_context or {})
        }
        
        # 执行变量替换
        final_prompt = template
        for key, value in template_vars.items():
            placeholder = f"{{{key}}}"
            if placeholder in final_prompt:
                final_prompt = final_prompt.replace(placeholder, str(value))
        
        return final_prompt
    
    def generate_chart_prompt(self, data: Dict[str, Any]) -> str:
        """生成图表分析提示词"""
        return self.generate_ai_prompt('CT', data)
    
    def generate_report_prompt(self, data: Dict[str, Any]) -> str:
        """生成报告提示词"""
        return self.generate_ai_prompt('RP', data)
    
    def generate_image_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """生成图像分析提示词"""
        return self.generate_ai_prompt('IMAGE', data)
    
    def generate_prediction_prompt(self, data: Dict[str, Any]) -> str:
        """生成预测分析提示词"""
        return self.generate_ai_prompt('PREDICT', data)


# 全局模板引擎实例
_template_engine = None

def get_template_engine() -> AITemplateEngine:
    """获取全局模板引擎实例"""
    global _template_engine
    if _template_engine is None:
        _template_engine = AITemplateEngine()
    return _template_engine


# 测试函数
if __name__ == "__main__":
    # 测试数据
    test_data = {
        "ticker": "TSLA",
        "CVDsignal": "cvdAboveMA",
        "pmaText": "PMA Strong Bullish",
        "signal": "BUY",
        "close": "250.45",
        "timeframe": "1H",
        "volume": "1250000",
        "rsi": "65.4"
    }
    
    # 测试模板引擎
    engine = get_template_engine()
    
    print("=== 图表分析提示词 ===")
    chart_prompt = engine.generate_chart_prompt(test_data)
    print(chart_prompt)
    print()
    
    print("=== 报告生成提示词 ===")
    report_prompt = engine.generate_report_prompt(test_data)
    print(report_prompt)
    print()
    
    print("=== 预测分析提示词 ===")
    predict_prompt = engine.generate_prediction_prompt(test_data)
    print(predict_prompt)