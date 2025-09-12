import json
import os
from datetime import datetime
from typing import Dict, Any, List


class SimpleFieldConfig:
    """简化的字段配置 - 硬编码逻辑，只允许编辑输出文本"""
    
    def __init__(self):
        self.config_dir = 'config'
        self.config_file = os.path.join(self.config_dir, 'simple_field_texts.json')
        self.field_configs = {}
        self._load_config()
    
    def _load_config(self):
        """加载简化配置"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if not os.path.exists(self.config_file):
            self._create_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.field_configs = config.get('fields', {})
            print(f"✅ 简化配置已加载，共 {len(self.field_configs)} 个字段")
            
        except Exception as e:
            print(f"❌ 加载简化配置失败: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """创建默认的简化配置"""
        default_config = {
            "version": "1.0",
            "description": "简化字段配置 - 硬编码逻辑，只允许编辑输出文本",
            "created_at": datetime.now().isoformat(),
            "fields": {
                "MAtrend": {
                    "logic": "hardcoded: 1=上涨, 0=中性, -1=下跌",
                    "timeframe_reference": "current_timeframe",
                    "outputs": {
                        "1": "{current_timeframe}级别的MA趋势显示上涨趋势，多头排列",
                        "0": "{current_timeframe}级别的MA趋势中性，方向不明", 
                        "-1": "{current_timeframe}级别的MA趋势显示下跌趋势，空头排列"
                    }
                },
                "MAtrend_timeframe1": {
                    "logic": "hardcoded: 1=上涨, 0=中性, -1=下跌 (第一层时间框架趋势状态)",
                    "timeframe_reference": "adaptive_timeframe_1",
                    "outputs": {
                        "1": "第一层时间框架({adaptive_timeframe_1})MA趋势显示上涨趋势，多头排列",
                        "0": "第一层时间框架({adaptive_timeframe_1})MA趋势显示中性，震荡整理", 
                        "-1": "第一层时间框架({adaptive_timeframe_1})MA趋势显示下跌趋势，空头排列",
                        "default": "第一层时间框架MA趋势状态: {value}"
                    }
                },
                "MAtrend_timeframe2": {
                    "logic": "hardcoded: 1=上涨, 0=中性, -1=下跌 (第二层时间框架趋势状态)",
                    "timeframe_reference": "adaptive_timeframe_2",
                    "outputs": {
                        "1": "第二层时间框架({adaptive_timeframe_2})MA趋势显示上涨趋势，多头排列",
                        "0": "第二层时间框架({adaptive_timeframe_2})MA趋势显示中性，震荡整理", 
                        "-1": "第二层时间框架({adaptive_timeframe_2})MA趋势显示下跌趋势，空头排列",
                        "default": "第二层时间框架MA趋势状态: {value}"
                    }
                },
                "AIbandsignal": {
                    "logic": "hardcoded: green uptrend / red downtrend",
                    "outputs": {
                        "green_uptrend": "AI波段显示绿色上涨趋势，多头力量强劲",
                        "red_downtrend": "AI波段显示红色下跌趋势，空头力量占据主导地位"
                    }
                },
                "CVDsignal": {
                    "logic": "hardcoded: cvdAboveMA / cvdBelowMA",
                    "outputs": {
                        "cvdAboveMA": "CVD信号显示价量背离指标在移动平均线上方，买盘力量较强",
                        "cvdBelowMA": "CVD信号显示价量背离指标在移动平均线下方，卖盘力量较强"
                    }
                },
                "choppingrange_signal": {
                    "logic": "hardcoded: chopping / no chopping",
                    "outputs": {
                        "chopping": "市场处于震荡整理状态，价格在区间内波动",
                        "no chopping": "市场趋势明确，价格突破震荡区间"
                    }
                },
                "SQZsignal": {
                    "logic": "hardcoded: squeeze / no squeeze",
                    "outputs": {
                        "squeeze": "波动性收缩信号，市场即将突破",
                        "no squeeze": "波动性正常，市场处于趋势运行中"
                    }
                },
                "RSIHAsignal": {
                    "logic": "hardcoded: BullishHA / BearishHA",
                    "outputs": {
                        "BullishHA": "RSI-HA信号显示多头海肯阿什形态，上涨动能增强",
                        "BearishHA": "RSI-HA信号显示空头海肯阿什形态，下跌动能增强"
                    }
                },
                "rsi_state_trend": {
                    "logic": "hardcoded: Bullish / Bearish / Neutral",
                    "outputs": {
                        "Bullish": "RSI状态趋势显示多头强势，超买区域运行",
                        "Bearish": "RSI状态趋势显示空头强势，超卖区域运行",
                        "Neutral": "RSI状态趋势显示中性，在中轴附近震荡"
                    }
                },
                "center_trend": {
                    "logic": "hardcoded: Strong Bullish / Weak Bullish / Weak Bearish / Strong Bearish",
                    "outputs": {
                        "Strong Bullish": "中枢趋势显示强势多头，价格持续上涨突破",
                        "Weak Bullish": "中枢趋势显示弱势多头，价格温和上涨",
                        "Weak Bearish": "中枢趋势显示弱势空头，价格温和下跌",
                        "Strong Bearish": "中枢趋势显示强势空头，价格持续下跌突破"
                    }
                },
                "MOMOsignal": {
                    "logic": "hardcoded: bullishmomo / bearishmomo",
                    "outputs": {
                        "bullishmomo": "动量信号显示多头动量增强，买入动能加速",
                        "bearishmomo": "动量信号显示空头动量增强，卖出动能加速"
                    }
                },
                "Middle_smooth_trend": {
                    "logic": "hardcoded: Neutral / Bullish + / Bullish / Bearish + / Bearish",
                    "outputs": {
                        "Neutral": "中线平滑趋势显示中性状态，方向待定",
                        "Bullish +": "中线平滑趋势显示强势多头，上涨动能充足",
                        "Bullish": "中线平滑趋势显示多头趋势，价格稳步上涨",
                        "Bearish +": "中线平滑趋势显示强势空头，下跌动能充足",
                        "Bearish": "中线平滑趋势显示空头趋势，价格稳步下跌"
                    }
                },
                "pmaText": {
                    "logic": "hardcoded: PMA Strong Bullish / PMA Bullish / PMA Strong Bearish / PMA Bearish / PMA Trendless",
                    "outputs": {
                        "PMA Strong Bullish": "PMA显示强势多头信号，价格动能强劲向上",
                        "PMA Bullish": "PMA显示多头信号，价格温和上涨",
                        "PMA Strong Bearish": "PMA显示强势空头信号，价格动能强劲向下",
                        "PMA Bearish": "PMA显示空头信号，价格温和下跌",
                        "PMA Trendless": "PMA显示无趋势状态，价格方向不明"
                    }
                },
                "wavemarket_state": {
                    "logic": "hardcoded: {current_timeframe} Long Strong / Long Weak / Short Strong / Short Weak / Neutral",
                    "timeframe_reference": "current_timeframe",
                    "outputs": {
                        "Long Strong": "{current_timeframe}级别波浪市场状态显示强势做多，多头力量占主导",
                        "Long Weak": "{current_timeframe}级别波浪市场状态显示弱势做多，多头力量有限",
                        "Short Strong": "{current_timeframe}级别波浪市场状态显示强势做空，空头力量占主导",
                        "Short Weak": "{current_timeframe}级别波浪市场状态显示弱势做空，空头力量有限",
                        "Neutral": "{current_timeframe}级别波浪市场状态显示中性，多空力量均衡"
                    }
                },
                "HTFwave_signal": {
                    "logic": "hardcoded: {adaptive_timeframe_1} Bullish / Bearish / Neutral",
                    "timeframe_reference": "adaptive_timeframe_1",
                    "outputs": {
                        "Bullish": "{adaptive_timeframe_1}级别高时间框架波浪信号显示多头趋势",
                        "Bearish": "{adaptive_timeframe_1}级别高时间框架波浪信号显示空头趋势",
                        "Neutral": "{adaptive_timeframe_1}级别高时间框架波浪信号显示中性状态"
                    }
                },
                "ewotrend_state": {
                    "logic": "hardcoded: Strong Bullish / Weak Bullish / Weak Bearish / Strong Bearish",
                    "outputs": {
                        "Strong Bullish": "EWO趋势状态显示强势多头，波浪振荡器强烈看涨",
                        "Weak Bullish": "EWO趋势状态显示弱势多头，波浪振荡器温和看涨",
                        "Weak Bearish": "EWO趋势状态显示弱势空头，波浪振荡器温和看跌",
                        "Strong Bearish": "EWO趋势状态显示强势空头，波浪振荡器强烈看跌"
                    }
                },
                "choppiness": {
                    "logic": "hardcoded: 数值输出",
                    "outputs": {
                        "default": "震荡指数为{value}，数值越高表示市场越震荡"
                    }
                },
                "adxValue": {
                    "logic": "hardcoded: 数值输出",
                    "outputs": {
                        "default": "ADX数值为{value}，反映趋势强度指标"
                    }
                },
                "ratingstatus": {
                    "logic": "hardcoded: 13种评级状态组合",
                    "outputs": {
                        "Neutral": "评级状态显示中性，市场方向不明确",
                        "Bullish-Weak-TrendDriven": "评级状态显示弱势多头，由趋势驱动",
                        "Bullish-Weak-OscDriven": "评级状态显示弱势多头，由振荡指标驱动",
                        "Bullish-Medium-TrendDriven": "评级状态显示中等多头，由趋势驱动",
                        "Bullish-Medium-OscDriven": "评级状态显示中等多头，由振荡指标驱动",
                        "Bullish-Strong-TrendDriven": "评级状态显示强势多头，由趋势驱动",
                        "Bullish-Strong-OscDriven": "评级状态显示强势多头，由振荡指标驱动",
                        "Bearish-Weak-TrendDriven": "评级状态显示弱势空头，由趋势驱动",
                        "Bearish-Weak-OscDriven": "评级状态显示弱势空头，由振荡指标驱动",
                        "Bearish-Medium-TrendDriven": "评级状态显示中等空头，由趋势驱动",
                        "Bearish-Medium-OscDriven": "评级状态显示中等空头，由振荡指标驱动",
                        "Bearish-Strong-TrendDriven": "评级状态显示强势空头，由趋势驱动",
                        "Bearish-Strong-OscDriven": "评级状态显示强势空头，由振荡指标驱动"
                    }
                },
                "action": {
                    "logic": "hardcoded: buy / sell / hold",
                    "outputs": {
                        "buy": "交易操作：买入",
                        "sell": "交易操作：卖出", 
                        "hold": "交易操作：持有"
                    }
                },
                "stoploss": {
                    "logic": "hardcoded: 直接数值输出",
                    "outputs": {
                        "default": "止损价位：{value}"
                    }
                },
                "takeprofit": {
                    "logic": "hardcoded: 直接数值输出", 
                    "outputs": {
                        "default": "止盈价位：{value}"
                    }
                },
                "entry_price": {
                    "logic": "hardcoded: 直接数值输出",
                    "outputs": {
                        "default": "入场价位：{value}"
                    }
                },
                "position_size": {
                    "logic": "hardcoded: 直接数值输出",
                    "outputs": {
                        "default": "仓位规模：{value}"
                    }
                },
                "risk_reward": {
                    "logic": "hardcoded: 直接数值输出",
                    "outputs": {
                        "default": "风险收益比：{value}"
                    }
                },
                "indicator": {
                    "logic": "hardcoded: 指标名称直接输出",
                    "outputs": {
                        "default": "技术指标：{value}"
                    }
                },
                "oscrating": {
                    "logic": "hardcoded: 振荡指标评级数值",
                    "outputs": {
                        "default": "振荡指标评级：{value}"
                    }
                },
                "trendrating": {
                    "logic": "hardcoded: 趋势指标评级数值",
                    "outputs": {
                        "default": "趋势指标评级：{value}"
                    }
                },
                "risk": {
                    "logic": "hardcoded: 风险等级",
                    "outputs": {
                        "Low": "风险等级：低风险",
                        "Medium": "风险等级：中等风险",
                        "High": "风险等级：高风险",
                        "default": "风险等级：{value}"
                    }
                },
                "poc_summary": {
                    "logic": "hardcoded: POC价格汇总解析",
                    "outputs": {
                        "default": "POC分析显示关键价格水平：{value}，这些是机构重点关注的成交密集区域，价格在这些水平附近容易形成支撑或阻力"
                    }
                },
                "POCtrend": {
                    "logic": "hardcoded: POC趋势信号解析 (-2到2的数值)",
                    "outputs": {
                        "2": "强势多头趋势：价格站上所有周期的 POC，短中长期共振，多头主导",
                        "1": "短期强势但中期承压：短线资金推高，但上周/月度 POC 压力仍在，谨慎追多",
                        "0": "震荡区间：价格在不同周期 POC 之间波动，多空分歧，观望为主",
                        "-1": "短期偏弱但中期强势：短线回调，但中期资金依然看多，可等待低吸机会",
                        "-2": "强势空头趋势：价格跌破所有周期的 POC，短中长期共振，空头主导",
                        "default": "POC趋势信号: {value}"
                    }
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        self.field_configs = default_config['fields']
        print(f"✅ 创建默认简化配置，共 {len(self.field_configs)} 个字段")
    
    def get_field_output(self, field_name: str, field_value: Any, data: Dict[str, Any]) -> str:
        """获取字段输出文本"""
        if field_name not in self.field_configs:
            return f"{field_name}: {field_value}"
        
        field_config = self.field_configs[field_name]
        outputs = field_config.get('outputs', {})
        field_str = str(field_value)
        
        # 硬编码逻辑处理
        if field_name in ["MAtrend", "MAtrend_timeframe1", "MAtrend_timeframe2"]:
            # 1, 0, -1 逻辑
            if field_str in outputs:
                return self._substitute_variables(outputs[field_str], data)
        
        elif field_name == "AIbandsignal":
            # green uptrend / red downtrend
            if "green uptrend" in field_str.lower():
                return self._substitute_variables(outputs.get('green_uptrend', f"AI波段: {field_value}"), data)
            elif "red downtrend" in field_str.lower():
                return self._substitute_variables(outputs.get('red_downtrend', f"AI波段: {field_value}"), data)
        
        elif field_name == "CVDsignal":
            # cvdAboveMA / cvdBelowMA
            if "cvdAboveMA" in field_str:
                return self._substitute_variables(outputs.get('cvdAboveMA', f"CVD: {field_value}"), data)
            elif "cvdBelowMA" in field_str:
                return self._substitute_variables(outputs.get('cvdBelowMA', f"CVD: {field_value}"), data)
        
        elif field_name == "choppingrange_signal":
            # chopping / no chopping
            if "chopping" in field_str.lower() and "no chopping" not in field_str.lower():
                return self._substitute_variables(outputs.get('chopping', f"震荡: {field_value}"), data)
            elif "no chopping" in field_str.lower():
                return self._substitute_variables(outputs.get('no chopping', f"非震荡: {field_value}"), data)
        
        elif field_name == "SQZsignal":
            # squeeze / no squeeze
            if "squeeze" in field_str.lower() and "no squeeze" not in field_str.lower():
                return self._substitute_variables(outputs.get('squeeze', f"挤压: {field_value}"), data)
            elif "no squeeze" in field_str.lower():
                return self._substitute_variables(outputs.get('no squeeze', f"非挤压: {field_value}"), data)
        
        elif field_name == "RSIHAsignal":
            # BullishHA / BearishHA
            if "BullishHA" in field_str:
                return self._substitute_variables(outputs.get('BullishHA', f"多头HA: {field_value}"), data)
            elif "BearishHA" in field_str:
                return self._substitute_variables(outputs.get('BearishHA', f"空头HA: {field_value}"), data)
        
        elif field_name == "rsi_state_trend":
            # Bullish / Bearish / Neutral
            if "Bullish" in field_str:
                return self._substitute_variables(outputs.get('Bullish', f"RSI多头: {field_value}"), data)
            elif "Bearish" in field_str:
                return self._substitute_variables(outputs.get('Bearish', f"RSI空头: {field_value}"), data)
            elif "Neutral" in field_str:
                return self._substitute_variables(outputs.get('Neutral', f"RSI中性: {field_value}"), data)
        
        elif field_name == "center_trend":
            # Strong Bullish / Weak Bullish / Weak Bearish / Strong Bearish
            if "Strong Bullish" in field_str:
                return self._substitute_variables(outputs.get('Strong Bullish', f"强势多头: {field_value}"), data)
            elif "Weak Bullish" in field_str:
                return self._substitute_variables(outputs.get('Weak Bullish', f"弱势多头: {field_value}"), data)
            elif "Weak Bearish" in field_str:
                return self._substitute_variables(outputs.get('Weak Bearish', f"弱势空头: {field_value}"), data)
            elif "Strong Bearish" in field_str:
                return self._substitute_variables(outputs.get('Strong Bearish', f"强势空头: {field_value}"), data)
        
        elif field_name == "MOMOsignal":
            # bullishmomo / bearishmomo
            if "bullishmomo" in field_str.lower():
                return self._substitute_variables(outputs.get('bullishmomo', f"多头动量: {field_value}"), data)
            elif "bearishmomo" in field_str.lower():
                return self._substitute_variables(outputs.get('bearishmomo', f"空头动量: {field_value}"), data)
        
        elif field_name == "Middle_smooth_trend":
            # Neutral / Bullish + / Bullish / Bearish + / Bearish
            if "Bullish +" in field_str:
                return self._substitute_variables(outputs.get('Bullish +', f"强势多头: {field_value}"), data)
            elif "Bearish +" in field_str:
                return self._substitute_variables(outputs.get('Bearish +', f"强势空头: {field_value}"), data)
            elif "Bullish" in field_str:
                return self._substitute_variables(outputs.get('Bullish', f"多头: {field_value}"), data)
            elif "Bearish" in field_str:
                return self._substitute_variables(outputs.get('Bearish', f"空头: {field_value}"), data)
            elif "Neutral" in field_str:
                return self._substitute_variables(outputs.get('Neutral', f"中性: {field_value}"), data)
        
        elif field_name == "pmaText":
            # PMA Strong Bullish / PMA Bullish / PMA Strong Bearish / PMA Bearish / PMA Trendless
            if "PMA Strong Bullish" in field_str:
                return self._substitute_variables(outputs.get('PMA Strong Bullish', f"PMA强势多头: {field_value}"), data)
            elif "PMA Strong Bearish" in field_str:
                return self._substitute_variables(outputs.get('PMA Strong Bearish', f"PMA强势空头: {field_value}"), data)
            elif "PMA Bullish" in field_str:
                return self._substitute_variables(outputs.get('PMA Bullish', f"PMA多头: {field_value}"), data)
            elif "PMA Bearish" in field_str:
                return self._substitute_variables(outputs.get('PMA Bearish', f"PMA空头: {field_value}"), data)
            elif "PMA Trendless" in field_str:
                return self._substitute_variables(outputs.get('PMA Trendless', f"PMA无趋势: {field_value}"), data)
        
        elif field_name == "wavemarket_state":
            # Long Strong / Long Weak / Short Strong / Short Weak / Neutral
            if "Long Strong" in field_str:
                return self._substitute_variables(outputs.get('Long Strong', f"强势做多: {field_value}"), data)
            elif "Long Weak" in field_str:
                return self._substitute_variables(outputs.get('Long Weak', f"弱势做多: {field_value}"), data)
            elif "Short Strong" in field_str:
                return self._substitute_variables(outputs.get('Short Strong', f"强势做空: {field_value}"), data)
            elif "Short Weak" in field_str:
                return self._substitute_variables(outputs.get('Short Weak', f"弱势做空: {field_value}"), data)
            elif "Neutral" in field_str:
                return self._substitute_variables(outputs.get('Neutral', f"中性: {field_value}"), data)
        
        elif field_name == "HTFwave_signal":
            # Bullish / Bearish / Neutral
            if "Bullish" in field_str:
                return self._substitute_variables(outputs.get('Bullish', f"HTF多头: {field_value}"), data)
            elif "Bearish" in field_str:
                return self._substitute_variables(outputs.get('Bearish', f"HTF空头: {field_value}"), data)
            elif "Neutral" in field_str:
                return self._substitute_variables(outputs.get('Neutral', f"HTF中性: {field_value}"), data)
        
        elif field_name == "ewotrend_state":
            # Strong Bullish / Weak Bullish / Weak Bearish / Strong Bearish
            if "Strong Bullish" in field_str:
                return self._substitute_variables(outputs.get('Strong Bullish', f"EWO强势多头: {field_value}"), data)
            elif "Weak Bullish" in field_str:
                return self._substitute_variables(outputs.get('Weak Bullish', f"EWO弱势多头: {field_value}"), data)
            elif "Weak Bearish" in field_str:
                return self._substitute_variables(outputs.get('Weak Bearish', f"EWO弱势空头: {field_value}"), data)
            elif "Strong Bearish" in field_str:
                return self._substitute_variables(outputs.get('Strong Bearish', f"EWO强势空头: {field_value}"), data)
        
        elif field_name == "ratingstatus":
            # 13种评级状态组合 - 精确匹配
            if field_str in outputs:
                return outputs[field_str]
            return f"评级状态: {field_value}"
        
        elif field_name == "action":
            # 交易操作 - 直接匹配
            if field_str in outputs:
                return outputs[field_str]
            return f"交易操作: {field_value}"
        
        elif field_name in ["choppiness", "adxValue", "stoploss", "takeprofit", "entry_price", "position_size", "risk_reward", "indicator", "oscrating", "trendrating"]:
            # 数值输出
            try:
                output_text = outputs.get('default', f"{field_name}: {{value}}")
                output_text = output_text.replace('{value}', str(field_value))
                return self._substitute_variables(output_text, data)
            except Exception:
                pass
        
        elif field_name == "risk":
            # 风险等级 - 匹配预设值或默认
            if field_str in outputs:
                return outputs[field_str]
            else:
                output_text = outputs.get('default', f"风险等级: {{value}}")
                return output_text.replace('{value}', str(field_value))
        
        elif field_name in ["lastSupplyText", "lastDemandText", "referencePrice"]:
            # 供需区字段 - 使用default模板
            output_text = outputs.get('default', f"{field_name}: {{value}}")
            return output_text.replace('{value}', str(field_value))
        
        elif field_name == "poc_summary":
            # POC价格汇总 - 直接使用default模板
            output_text = outputs.get('default', f"POC价格信息: {{value}}")
            return output_text.replace('{value}', str(field_value))
        
        elif field_name == "POCtrend":
            # POC趋势信号 - 数值匹配 (-2到2)
            if field_str in outputs:
                return outputs[field_str]
            else:
                output_text = outputs.get('default', f"POC趋势信号: {{value}}")
                return output_text.replace('{value}', str(field_value))
        
        return f"{field_name}: {field_value}"
    
    def _convert_timeframe(self, timeframe_value: Any) -> str:
        """转换时间框架数值为可读格式 - 支持多种格式"""
        try:
            # 尝试转换为整数
            multiplier = int(timeframe_value)
            
            # 按照用户提供的逻辑转换
            if multiplier == 15:
                return "15MIN"
            elif multiplier == 30:
                return "30MIN"
            elif multiplier == 60:
                return "1H"
            elif multiplier == 120:
                return "2H"
            elif multiplier == 240:
                return "4H"
            elif multiplier == 1440:
                return "1D"
            elif multiplier == 10080:
                return "1W"
            else:
                return f"{multiplier}MIN"
                
        except (ValueError, TypeError):
            # 如果不是数字，检查字符串
            timeframe_str = str(timeframe_value).lower()
            
            # 处理字符串格式
            if timeframe_str in ['15m', '15min']:
                return "15MIN"
            elif timeframe_str in ['30m', '30min']:
                return "30MIN"
            elif timeframe_str in ['1h', '60m', '60min']:
                return "1H"
            elif timeframe_str in ['2h', '120m', '120min']:
                return "2H"
            elif timeframe_str in ['4h', '240m', '240min']:
                return "4H"
            elif timeframe_str in ['1d', 'daily', 'd', '1day']:
                return "1D"
            elif timeframe_str in ['1w', 'weekly', 'w', '1week']:
                return "1W"
            else:
                # 返回原值
                return str(timeframe_value)

    def _substitute_variables(self, text: str, data: Dict[str, Any]) -> str:
        """替换变量"""
        # 先处理时间框架变量的转换
        if '{current_timeframe}' in text:
            timeframe = data.get('current_timeframe', 'Unknown')
            converted_timeframe = self._convert_timeframe(timeframe)
            text = text.replace('{current_timeframe}', converted_timeframe)
            
        if '{adaptive_timeframe_1}' in text:
            timeframe = data.get('adaptive_timeframe_1', 'Unknown')
            converted_timeframe = self._convert_timeframe(timeframe)
            text = text.replace('{adaptive_timeframe_1}', converted_timeframe)
            
        if '{adaptive_timeframe_2}' in text:
            timeframe = data.get('adaptive_timeframe_2', 'Unknown')
            converted_timeframe = self._convert_timeframe(timeframe)
            text = text.replace('{adaptive_timeframe_2}', converted_timeframe)
        
        # 处理其他变量
        for key, value in data.items():
            if key not in ['current_timeframe', 'adaptive_timeframe_1', 'adaptive_timeframe_2']:
                text = text.replace(f'{{{key}}}', str(value))
        
        return text
    
    def update_field_output(self, field_name: str, output_key: str, new_text: str):
        """更新字段输出文本"""
        if field_name not in self.field_configs:
            print(f"❌ 字段 {field_name} 不存在")
            return False
        
        self.field_configs[field_name]['outputs'][output_key] = new_text
        self._save_config()
        return True
    
    def _save_config(self):
        """保存配置"""
        config = {
            "version": "1.0",
            "description": "简化字段配置 - 硬编码逻辑，只允许编辑输出文本",
            "last_updated": datetime.now().isoformat(),
            "fields": self.field_configs
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("✅ 简化配置已保存")
    
    def get_field_list(self) -> List[Dict[str, Any]]:
        """获取字段列表用于界面显示"""
        field_list = []
        for field_name, field_config in self.field_configs.items():
            field_info = {
                'name': field_name,
                'logic': field_config.get('logic', ''),
                'timeframe_ref': field_config.get('timeframe_reference', ''),
                'outputs': field_config.get('outputs', {})
            }
            field_list.append(field_info)
        return field_list


# 全局实例
simple_config = SimpleFieldConfig()


def process_with_simple_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """使用简化配置处理数据 - 支持不同的JSON结构"""
    results = {
        'parsed_fields': {},
        'summary_text': '',
        'original_data': data
    }
    
    # 检测JSON结构并准备数据源
    combined_data = {}
    
    # 如果有'data'字段，说明是交易动作webhook
    if 'data' in data and isinstance(data['data'], dict):
        # 技术指标在data字段里
        combined_data.update(data['data'])
        # 交易字段在根级别
        for key in ['action', 'stoploss', 'takeprofit', 'entry_price', 'position_size', 'risk_reward', 'ticker', 'symbol']:
            if key in data:
                combined_data[key] = data[key]
        # 供需区字段多层级提取
        for key in ['lastSupplyText', 'lastDemandText', 'referencePrice']:
            if key in data:
                combined_data[key] = data[key]
            elif 'data' in data and key in data['data']:
                combined_data[key] = data['data'][key]
        # extras字段里的内容
        if 'extras' in data and isinstance(data['extras'], dict):
            combined_data.update(data['extras'])
        # 时间框架字段处理 - 支持新旧格式
        # 新格式：current_timeframe, adaptive_timeframe_1/2
        for tf_key in ['current_timeframe', 'adaptive_timeframe_1', 'adaptive_timeframe_2']:
            if tf_key in data:
                combined_data[tf_key] = data[tf_key]
            elif 'data' in data and tf_key in data['data']:
                combined_data[tf_key] = data['data'][tf_key]
            elif 'extras' in data and tf_key in data['extras']:
                combined_data[tf_key] = data['extras'][tf_key]
        
        # 处理extras中的timeframe字段(特殊情况)
        if 'extras' in data and 'timeframe' in data['extras']:
            timeframe_value = data['extras']['timeframe']
            # 如果没有current_timeframe，用timeframe作为current_timeframe
            if 'current_timeframe' not in combined_data:
                combined_data['current_timeframe'] = timeframe_value
        
        # 老格式时间框架字段
        for old_tf_key in ['MAtrend_timeframe1', 'MAtrend_timeframe2']:
            if old_tf_key in data:
                combined_data[old_tf_key] = data[old_tf_key]
            elif 'data' in data and old_tf_key in data['data']:
                combined_data[old_tf_key] = data['data'][old_tf_key]
    else:
        # 普通K线webhook，所有数据在根级别
        combined_data = data.copy()
    
    summary_lines = []
    
    # 解析所有配置字段
    for field_name in simple_config.field_configs.keys():
        field_value = combined_data.get(field_name)
        if field_value is not None:
            parsed_output = simple_config.get_field_output(field_name, field_value, combined_data)
            results['parsed_fields'][f'{field_name}_parsed'] = parsed_output
            results['parsed_fields'][f'{field_name}_raw'] = field_value
            summary_lines.append(parsed_output)
    
    # 处理时间框架字段 - 仅供其他字段引用，不加入summary_lines
    # 新格式时间框架
    for field_name in ['current_timeframe', 'adaptive_timeframe_1', 'adaptive_timeframe_2']:
        field_value = combined_data.get(field_name)
        if field_value is not None:
            converted_timeframe = simple_config._convert_timeframe(field_value)
            if field_name == 'current_timeframe':
                desc = f"基于{converted_timeframe}时间框架分析，适合中短线交易策略" if converted_timeframe in ["1H", "2H", "4H"] else f"基于{converted_timeframe}时间框架分析，适合短线交易操作"
            elif field_name == 'adaptive_timeframe_1':
                desc = f"第一层时间框架为{converted_timeframe}，观察中期趋势变化" if converted_timeframe in ["4H", "1D"] else f"第一层时间框架为{converted_timeframe}，捕捉短期价格波动"
            else:
                desc = f"第二层时间框架为{converted_timeframe}，确认长期趋势支撑" if converted_timeframe in ["1D", "1W"] else f"第二层时间框架为{converted_timeframe}"
            
            results['parsed_fields'][f'{field_name}_parsed'] = desc
            results['parsed_fields'][f'{field_name}_raw'] = field_value
            # 不添加到summary_lines - 时间框架仅供引用
    
    # MAtrend_timeframe1/2 是趋势状态，不是时间框架数值
    # 这些字段现在由配置字段解析处理，不需要特殊的时间框架处理
    
    results['summary_text'] = '\n'.join(summary_lines)
    return results