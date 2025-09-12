import json
import os
from datetime import datetime
from typing import Dict, Any, List


class SimpleAITemplate:
    """简化AI模板管理系统 - 直接文本编辑，支持变量替换"""
    
    def __init__(self):
        self.config_file = "config/simple_ai_templates.json"
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """加载模板配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ 简化AI模板已加载，共 {len(data.get('templates', {}))} 个模板")
                    return data


# 全局实例
_simple_ai_template_engine = None

def get_simple_ai_template_engine():
    """获取简化AI模板引擎实例"""
    global _simple_ai_template_engine
    if _simple_ai_template_engine is None:
        _simple_ai_template_engine = SimpleAITemplate()
    return _simple_ai_template_engine.get('templates', {})
            except Exception as e:
                print(f"❌ 加载AI模板失败: {e}")
        
        # 创建默认模板
        default_templates = self._create_default_templates()
        self._save_templates(default_templates)
        print(f"✅ 创建默认简化AI模板，共 {len(default_templates)} 个模板")
        return default_templates
    
    def _create_default_templates(self) -> Dict[str, Dict[str, Any]]:
        """创建默认简化模板"""
        return {
            "CT": {
                "name": "图表分析模板",
                "description": "用于图表分析的AI提示模板",
                "template": """请分析这张{ticker}的股票图表。

基于以下技术指标数据：
- 时间框架：{current_timeframe}
- MA趋势：{MAtrend_parsed}
- AI波段：{AIbandsignal_parsed}
- 评级状态：{ratingstatus_parsed}

请提供：
1. 技术分析概览
2. 关键支撑阻力位
3. 短期趋势预测
4. 交易建议

注意：请用中文回复，保持专业客观的分析风格。""",
                "variables": [
                    "ticker", "current_timeframe", "MAtrend_parsed", 
                    "AIbandsignal_parsed", "ratingstatus_parsed"
                ]
            },
            
            "RP": {
                "name": "报告生成模板",
                "description": "用于生成详细分析报告的AI提示模板",
                "template": """请为{ticker}生成一份详细的技术分析报告。

## 原始数据
{webhook_data}

## 解析结果
{parsed_summary}

请按以下结构生成报告：

### 📊 技术指标概览
- 当前时间框架：{current_timeframe}
- 主要趋势方向：{MAtrend_parsed}
- 市场强度：{ratingstatus_parsed}

### 📈 详细分析
1. 趋势分析：{pmaText_parsed}
2. 动量指标：{MOMOsignal_parsed}
3. 振荡指标：{RSIHAsignal_parsed}

### 💡 交易建议
基于当前技术面分析，提供具体的进入点位、止损和目标价位建议。

### ⚠️ 风险提示
指出当前市场环境下的主要风险因素。

请确保分析客观专业，避免过于绝对的预测。""",
                "variables": [
                    "ticker", "webhook_data", "parsed_summary", "current_timeframe",
                    "MAtrend_parsed", "ratingstatus_parsed", "pmaText_parsed", 
                    "MOMOsignal_parsed", "RSIHAsignal_parsed"
                ]
            },
            
            "IMAGE": {
                "name": "图片分析模板", 
                "description": "用于分析上传图片的AI提示模板",
                "template": """请分析这张图片中的股票图表。

如果提供了技术指标数据：
{parsed_summary}

请从图片中识别：
1. 图表类型和时间框架
2. 价格走势特征
3. 技术指标信号
4. 关键的支撑阻力位
5. 图表形态（如三角形、楔形、通道等）

结合技术指标数据（如果有），提供：
- 当前市场状态评估
- 可能的价格方向预测
- 关键关注点位
- 交易建议

请用中文详细分析，保持客观专业。""",
                "variables": ["parsed_summary"]
            },
            
            "PREDICT": {
                "name": "预测分析模板",
                "description": "用于价格预测的AI提示模板", 
                "template": """基于{ticker}的技术分析数据，请提供价格预测分析。

## 当前市场状态
- 时间框架：{current_timeframe}
- 趋势状态：{MAtrend_parsed}
- 市场评级：{ratingstatus_parsed}
- 波段信号：{AIbandsignal_parsed}

## 关键指标
- 动量信号：{MOMOsignal_parsed}
- 中枢趋势：{center_trend_parsed}
- 波浪状态：{wavemarket_state_parsed}

请提供：

### 🎯 短期预测（1-3天）
基于当前技术指标的短期价格方向和关键位。

### 📅 中期预测（1-2周）
结合趋势和动量指标的中期走势判断。

### 📊 关键价位
- 支撑位：
- 阻力位：
- 突破位：

### ⚡ 交易策略
- 进入策略：
- 止损位：
- 目标位：

### 📋 注意事项
提醒重要的风险因素和市场变化可能性。

请基于技术分析保持客观，避免过于绝对的预测。""",
                "variables": [
                    "ticker", "current_timeframe", "MAtrend_parsed", "ratingstatus_parsed",
                    "AIbandsignal_parsed", "MOMOsignal_parsed", "center_trend_parsed", 
                    "wavemarket_state_parsed"
                ]
            }
        }
    
    def _save_templates(self, templates: Dict[str, Any]):
        """保存模板配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        config = {
            "version": "1.0",
            "description": "简化AI模板配置 - 直接文本编辑，支持变量替换",
            "last_updated": datetime.now().isoformat(),
            "templates": templates
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ 简化AI模板已保存")
    
    def get_template(self, template_type: str) -> Dict[str, Any]:
        """获取指定类型的模板"""
        return self.templates.get(template_type, {})
    
    def update_template(self, template_type: str, new_template: str) -> bool:
        """更新模板内容"""
        if template_type not in self.templates:
            print(f"❌ 模板类型 {template_type} 不存在")
            return False
        
        self.templates[template_type]['template'] = new_template
        self.templates[template_type]['last_modified'] = datetime.now().isoformat()
        self._save_templates(self.templates)
        return True
    
    def get_template_list(self) -> List[Dict[str, Any]]:
        """获取所有模板列表"""
        template_list = []
        for template_type, template_data in self.templates.items():
            template_info = {
                'type': template_type,
                'name': template_data.get('name', ''),
                'description': template_data.get('description', ''),
                'template': template_data.get('template', ''),
                'variables': template_data.get('variables', []),
                'last_modified': template_data.get('last_modified', '')
            }
            template_list.append(template_info)
        return template_list
    
    def substitute_variables(self, template_type: str, data: Dict[str, Any]) -> str:
        """变量替换 - 支持webhook数据和解析结果"""
        template_info = self.get_template(template_type)
        template_text = template_info.get('template', '')
        
        if not template_text:
            return f"模板 {template_type} 未找到"
        
        # 使用简化配置引擎解析数据
        try:
            from simple_config_engine import process_with_simple_config
            parsing_results = process_with_simple_config(data)
            parsed_fields = parsing_results.get('parsed_fields', {})
            
            # 合并原始数据和解析结果
            all_variables = {}
            all_variables.update(data)  # 原始数据
            all_variables.update(parsed_fields)  # 解析后的字段
            
            # 添加特殊变量
            all_variables['webhook_data'] = json.dumps(data, ensure_ascii=False, indent=2)
            all_variables['parsed_summary'] = parsing_results.get('summary_text', '')
            
            print(f"✅ 解析成功，得到 {len(parsed_fields)} 个解析字段")
            print(f"📋 解析字段: {list(parsed_fields.keys())}")
            print(f"📋 总变量数: {len(all_variables)}")
            
        except Exception as e:
            print(f"⚠️ 解析数据失败: {e}")
            # 如果解析失败，只使用原始数据
            all_variables = data.copy()
        
        # 替换所有可用变量
        for key, value in all_variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in template_text:
                # 确保值为字符串
                str_value = str(value) if value is not None else ''
                template_text = template_text.replace(placeholder, str_value)
        
        return template_text
    
    def get_available_variables(self) -> Dict[str, List[str]]:
        """获取可用变量列表"""
        return {
            "webhook_variables": [
                "ticker", "current_timeframe", "adaptive_timeframe_1", "adaptive_timeframe_2",
                "MAtrend", "MAtrend_timeframe1", "MAtrend_timeframe2", "AIbandsignal",
                "CVDsignal", "choppingrange_signal", "SQZsignal", "RSIHAsignal",
                "rsi_state_trend", "center_trend", "MOMOsignal", "Middle_smooth_trend",
                "pmaText", "wavemarket_state", "HTFwave_signal", "ewotrend_state",
                "choppiness", "adxValue", "ratingstatus"
            ],
            "parsed_variables": [
                "MAtrend_parsed", "MAtrend_timeframe1_parsed", "MAtrend_timeframe2_parsed",
                "AIbandsignal_parsed", "CVDsignal_parsed", "choppingrange_signal_parsed",
                "SQZsignal_parsed", "RSIHAsignal_parsed", "rsi_state_trend_parsed",
                "center_trend_parsed", "MOMOsignal_parsed", "Middle_smooth_trend_parsed",
                "pmaText_parsed", "wavemarket_state_parsed", "HTFwave_signal_parsed",
                "ewotrend_state_parsed", "choppiness_parsed", "adxValue_parsed",
                "ratingstatus_parsed"
            ],
            "special_variables": [
                "webhook_data", "parsed_summary", "analysis_summary"
            ]
        }


# 全局实例
simple_ai_template = SimpleAITemplate()


def process_ai_template(template_type: str, data: Dict[str, Any]) -> str:
    """处理AI模板，进行变量替换"""
    return simple_ai_template.substitute_variables(template_type, data)


def get_all_templates() -> List[Dict[str, Any]]:
    """获取所有模板用于API"""
    return simple_ai_template.get_template_list()


def update_template_content(template_type: str, new_content: str) -> bool:
    """更新模板内容"""
    return simple_ai_template.update_template(template_type, new_content)