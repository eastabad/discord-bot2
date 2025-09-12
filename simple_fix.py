#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的图表API修复脚本
"""

def fix_chart_service():
    """修复chart_service.py中的交易所格式转换逻辑"""
    
    print("🔧 修复图表API交易所格式转换...")
    
    # 读取文件
    with open('/opt/discord-bot/chart_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 备份原文件
    import shutil
    import time
    backup_name = f'/opt/discord-bot/chart_service.py.backup.{int(time.time())}'
    shutil.copy('/opt/discord-bot/chart_service.py', backup_name)
    print(f"✅ 已备份原文件: {backup_name}")
    
    # 查找并修复
    new_lines = []
    in_get_ob_chart = False
    found_timeframe_check = False
    added_logic = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # 检查是否进入get_ob_chart方法
        if 'async def get_ob_chart' in line:
            in_get_ob_chart = True
            found_timeframe_check = False
            added_logic = False
            continue
        
        # 检查是否离开get_ob_chart方法
        if in_get_ob_chart and (line.startswith('    async def') or line.startswith('    def')):
            in_get_ob_chart = False
            continue
        
        # 在get_ob_chart方法中查找timeframe检查
        if in_get_ob_chart and 'normalized_timeframe is None:' in line:
            found_timeframe_check = True
            continue
        
        # 在timeframe检查后添加交易所格式转换逻辑
        if in_get_ob_chart and found_timeframe_check and 'return None' in line and not added_logic:
            # 添加新的逻辑
            new_logic = [
                '            
',
                '            # 处理交易所格式转换
',
                '            original_symbol = symbol
',
                '            if ':' in symbol:
',
                '                # 如果已经是 EXCHANGE:TICKER 格式，提取 TICKER 部分
',
                '                ticker_part = symbol.split(':', 1)[1]
',
                '                symbol = ticker_part
',
                '                self.logger.info(f"转换交易所格式: {original_symbol} -> {symbol}")
',
                '            elif symbol in self.stock_exchange_map:
',
                '                # 检查股票交易所映射
',
                '                symbol = self.stock_exchange_map[symbol]
',
                '                self.logger.info(f"使用交易所映射: {symbol}")
',
                '            else:
',
                '                # 使用智能检测功能自动匹配交易所
',
                '                symbol = await self.detect_stock_exchange(symbol)
',
                '                self.logger.info(f"智能检测交易所: {symbol}")
',
                '            
'
            ]
            
            # 在return None后插入新逻辑
            for logic_line in new_logic:
                new_lines.append(logic_line)
            
            added_logic = True
            print("✅ 已添加交易所格式转换逻辑")
    
    # 写回文件
    with open('/opt/discord-bot/chart_service.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ 修复完成！")
    
    # 验证修复结果
    print("\n📋 验证修复结果...")
    with open('/opt/discord-bot/chart_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '转换交易所格式' in content:
        print("✅ 交易所格式转换逻辑已添加")
    else:
        print("❌ 交易所格式转换逻辑未找到")
    
    # 语法检查
    try:
        import ast
        ast.parse(content)
        print("✅ 语法检查通过")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")

if __name__ == "__main__":
    fix_chart_service()
