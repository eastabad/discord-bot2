#!/usr/bin/env python3
"""
POC (Point of Control) 分析器
解析POC相关字段并提供趋势分析文本
"""

import logging

logger = logging.getLogger(__name__)

class POCAnalyzer:
    """POC数据分析器"""
    
    def __init__(self):
        self.poc_trend_descriptions = {
            2: "强势多头趋势：价格站上所有周期的 POC，短中长期共振，多头主导",
            1: "短期强势但中期承压：短线资金推高，但上周/月度 POC 压力仍在，谨慎追多",
            0: "震荡区间：价格在不同周期 POC 之间波动，多空分歧，观望为主",
            -1: "短期偏弱但中期强势：短线回调，但中期资金依然看多，可等待低吸机会",
            -2: "强势空头趋势：价格跌破所有周期的 POC，短中长期共振，空头主导"
        }
    
    def parse_poc_data(self, data: dict) -> dict:
        """
        解析POC相关数据
        
        Args:
            data: TradingView webhook数据
            
        Returns:
            dict: 包含解析后POC信息的字典
        """
        result = {
            'poc_summary': None,
            'poc_trend': None,
            'poc_trend_description': None
        }
        
        try:
            # 多层级提取poc_summary (直接输出数值)
            poc_summary = (data.get('poc_summary') or 
                         data.get('data', {}).get('poc_summary') if isinstance(data.get('data'), dict) else None)
            if poc_summary is not None:
                result['poc_summary'] = poc_summary
                logger.info(f"解析poc_summary: {result['poc_summary']}")
            
            # 多层级提取POCtrend并转换为描述文本
            poc_trend_value = (data.get('POCtrend') or 
                             data.get('data', {}).get('POCtrend') if isinstance(data.get('data'), dict) else None)
            if poc_trend_value is not None:
                # 尝试转换为整数
                try:
                    trend_int = int(float(poc_trend_value))
                    result['poc_trend'] = trend_int
                    
                    # 获取对应的描述文本
                    if trend_int in self.poc_trend_descriptions:
                        result['poc_trend_description'] = self.poc_trend_descriptions[trend_int]
                        logger.info(f"解析POCtrend: {trend_int} -> {result['poc_trend_description']}")
                    else:
                        # 如果值不在预定义范围内，使用默认描述
                        result['poc_trend_description'] = f"POC趋势值: {trend_int}"
                        logger.warning(f"未知POC趋势值: {trend_int}")
                        
                except (ValueError, TypeError):
                    logger.warning(f"无效的POCtrend值: {poc_trend_value}")
                    result['poc_trend_description'] = f"POC趋势: {poc_trend_value}"
            
            return result
            
        except Exception as e:
            logger.error(f"解析POC数据失败: {e}")
            return result
    
    def format_poc_info_for_embed(self, poc_data: dict) -> str:
        """
        为Discord embed格式化POC信息
        POC Summary显示为6个价格信息，排成两行
        POC Trend显示为第三行
        """
        try:
            lines = []
            
            # POC Summary处理 - 假设poc_summary包含6个价格信息
            if poc_data.get('poc_summary') is not None:
                poc_summary = poc_data['poc_summary']
                
                # 如果poc_summary是字符串，尝试解析价格信息
                if isinstance(poc_summary, str):
                    # 支持TradingView POC格式: "Daily POC: 123.45; Prev DailyPOC: 124.50; Weekly POC: 125.00; ..."
                    # 以及简单逗号分隔格式: "172.50,170.25,168.75,175.80,173.20,169.90"
                    import re
                    
                    # 检查是否是TradingView的标签格式
                    if 'POC:' in poc_summary:
                        # 提取带标签的POC信息
                        poc_pattern = r'(Daily POC|Prev DailyPOC|Weekly POC|Prev Weekly POC|Monthly POC|Prev Monthly POC):\s*(\d+\.?\d*)'
                        matches = re.findall(poc_pattern, poc_summary)
                        
                        if len(matches) >= 6:
                            # 保留标签，排成两行显示
                            line1_parts = []
                            line2_parts = []
                            for i, (label, price) in enumerate(matches[:6]):
                                # 简化标签名称
                                short_label = label.replace('Prev ', 'P').replace('POC', '').replace('Daily', 'D').replace('Weekly', 'W').replace('Monthly', 'M').strip()
                                formatted_item = f"{short_label}: ${price}"
                                
                                if i < 3:
                                    line1_parts.append(formatted_item)
                                else:
                                    line2_parts.append(formatted_item)
                            
                            line1 = f"📊 **POC Prices:** {' | '.join(line1_parts)}"
                            line2 = f"**Levels:** {' | '.join(line2_parts)}"
                            lines.extend([line1, line2])
                        else:
                            # 如果匹配不够6个，显示原始内容
                            lines.append(f"📊 **POC Summary:** {poc_summary}")
                    else:
                        # 简单数字格式
                        price_matches = re.findall(r'\d+\.\d+', str(poc_summary))
                        if len(price_matches) >= 6:
                            # 排成两行，每行3个价格
                            line1 = f"📊 **POC Prices:** ${price_matches[0]} | ${price_matches[1]} | ${price_matches[2]}"
                            line2 = f"**Levels:** ${price_matches[3]} | ${price_matches[4]} | ${price_matches[5]}"
                            lines.extend([line1, line2])
                        else:
                            # 如果不是6个价格，按原来方式显示
                            lines.append(f"📊 **POC Summary:** {poc_summary}")
                elif isinstance(poc_summary, (list, tuple)) and len(poc_summary) >= 6:
                    # 如果是列表格式
                    line1 = f"📊 **POC Prices:** ${poc_summary[0]} | ${poc_summary[1]} | ${poc_summary[2]}"
                    line2 = f"**Levels:** ${poc_summary[3]} | ${poc_summary[4]} | ${poc_summary[5]}"
                    lines.extend([line1, line2])
                else:
                    # 默认单行显示
                    lines.append(f"📊 **POC Summary:** {poc_summary}")
            
            # POC Trend描述
            if poc_data.get('poc_trend_description'):
                lines.append(f"📈 **POC Trend:** {poc_data['poc_trend_description']}")
            
            if lines:
                return '\n'.join(lines)
            else:
                return ""
                
        except Exception as e:
            logger.error(f"格式化POC信息失败: {e}")
            return ""

# 全局实例
_poc_analyzer = None

def get_poc_analyzer() -> POCAnalyzer:
    """获取POC分析器实例"""
    global _poc_analyzer
    if _poc_analyzer is None:
        _poc_analyzer = POCAnalyzer()
    return _poc_analyzer