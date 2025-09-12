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
                    return data.get('templates', {})
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
            "RP": {
                "name": "报告生成模板", 
                "description": "用于生成详细分析报告的AI提示模板",
                "template": """请为{ticker}生成一份详细的技术分析报告。

基于以下原始数据：
{webhook_data}

请按以下结构生成报告：
### 📊 技术指标概览
### 📈 趋势分析
### 💰 交易建议
### ⚠️ 风险提醒

请用中文回复，保持专业客观的分析风格。""",
                "variables": ["ticker", "webhook_data"]
            }
        }
    
    def _save_templates(self, templates: Dict[str, Any]):
        """保存模板到文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        config = {
            "templates": templates,
            "last_updated": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def substitute_variables(self, template_type: str, data: Dict[str, Any]) -> str:
        """变量替换 - 支持webhook数据和解析结果"""
        template_info = self.templates.get(template_type, {})
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
            
            # 处理嵌套的stopLoss和takeProfit数据
            if 'stopLoss' in data and isinstance(data['stopLoss'], dict):
                stop_price = data['stopLoss'].get('stopPrice')
                if stop_price is not None:
                    all_variables['stop_loss_level'] = str(stop_price)
            
            if 'takeProfit' in data and isinstance(data['takeProfit'], dict):
                limit_price = data['takeProfit'].get('limitPrice')
                if limit_price is not None:
                    all_variables['take_profit_level'] = str(limit_price)
            
            # 添加风险等级处理
            if 'extras' in data and isinstance(data['extras'], dict):
                risk = data['extras'].get('risk')
                if risk is not None:
                    all_variables['risk_level'] = str(risk)
            
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
    
    def get_template(self, template_type: str) -> Dict[str, Any]:
        """获取指定类型的模板"""
        return self.templates.get(template_type, {})
    
    def get_all_templates(self) -> Dict[str, Any]:
        """获取所有模板"""
        return self.templates
    
    def update_template(self, template_type: str, template_content: str) -> bool:
        """更新模板内容"""
        try:
            # 确保模板类型存在
            if template_type not in self.templates:
                self.templates[template_type] = {
                    'name': f'{template_type}模板',
                    'description': f'{template_type}的AI分析模板',
                    'template': '',
                    'variables': []
                }
            
            # 更新模板内容
            self.templates[template_type]['template'] = template_content
            
            # 保存到文件
            self._save_templates(self.templates)
            
            print(f"✅ 模板 {template_type} 更新成功")
            return True
            
        except Exception as e:
            print(f"❌ 模板 {template_type} 更新失败: {e}")
            return False


# 全局实例
_simple_ai_template_engine = None

def get_simple_ai_template_engine():
    """获取简化AI模板引擎实例"""
    global _simple_ai_template_engine
    if _simple_ai_template_engine is None:
        _simple_ai_template_engine = SimpleAITemplate()
    return _simple_ai_template_engine

def get_all_templates():
    """获取所有模板 - API兼容函数"""
    engine = get_simple_ai_template_engine()
    return engine.get_all_templates()

def update_template_content(template_type: str, template_content: str) -> bool:
    """更新模板内容 - API兼容函数"""
    engine = get_simple_ai_template_engine()
    return engine.update_template(template_type, template_content)