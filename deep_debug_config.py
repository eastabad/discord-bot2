#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入调试OrderBlock配置管理器
直接在VPS上测试配置管理器的实例化和使用
"""

import sys
import os

# 添加项目路径
sys.path.append('/opt/discord-bot')

def deep_debug_config():
    """深入调试配置管理器"""
    
    print("🔍 深入调试OrderBlock配置管理器")
    print("=" * 50)
    
    try:
        # 导入OrderBlock配置管理器
        from orderblock_config_manager import OrderBlockConfigManager
        
        print("✅ 成功导入OrderBlockConfigManager")
        print()
        
        # 测试1: 使用相对路径
        print("🧪 测试1: 使用相对路径")
        try:
            config1 = OrderBlockConfigManager("orderblock_routes.conf")
            print(f"   配置文件路径: {config1.config_file}")
            print(f"   配置文件存在: {os.path.exists(config1.config_file)}")
            print(f"   路由数量: {len(config1.routes)}")
            print(f"   默认频道: {config1.default_channels}")
            
            # 检查特定ticker
            if 'NYSE:AAPL' in config1.routes:
                channels = config1.routes['NYSE:AAPL']
                print(f"   NYSE:AAPL: {len(channels)} 个频道 -> {channels}")
            else:
                print(f"   NYSE:AAPL: 未找到")
                
        except Exception as e:
            print(f"   ❌ 测试1失败: {e}")
        
        print()
        
        # 测试2: 使用绝对路径
        print("🧪 测试2: 使用绝对路径")
        try:
            config2 = OrderBlockConfigManager("/opt/discord-bot/orderblock_routes.conf")
            print(f"   配置文件路径: {config2.config_file}")
            print(f"   配置文件存在: {os.path.exists(config2.config_file)}")
            print(f"   路由数量: {len(config2.routes)}")
            print(f"   默认频道: {config2.default_channels}")
            
            # 检查特定ticker
            if 'NYSE:AAPL' in config2.routes:
                channels = config2.routes['NYSE:AAPL']
                print(f"   NYSE:AAPL: {len(channels)} 个频道 -> {channels}")
            else:
                print(f"   NYSE:AAPL: 未找到")
                
        except Exception as e:
            print(f"   ❌ 测试2失败: {e}")
        
        print()
        
        # 测试3: 检查配置文件内容
        print("🧪 测试3: 检查配置文件内容")
        config_file = "/opt/discord-bot/orderblock_routes.conf"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"   配置文件行数: {len(lines)}")
            
            # 查找AAPL相关行
            aapl_lines = [line.strip() for line in lines if 'AAPL' in line and '=' in line]
            print(f"   AAPL相关行数: {len(aapl_lines)}")
            
            for line in aapl_lines[:3]:  # 显示前3行
                print(f"     {line}")
                
        else:
            print(f"   ❌ 配置文件不存在: {config_file}")
        
        print()
        
        # 测试4: 手动解析配置文件
        print("🧪 测试4: 手动解析配置文件")
        try:
            config3 = OrderBlockConfigManager()
            config3.load_config()  # 重新加载配置
            
            print(f"   重新加载后路由数量: {len(config3.routes)}")
            
            # 检查所有AAPL相关路由
            aapl_routes = {k: v for k, v in config3.routes.items() if 'AAPL' in k}
            print(f"   AAPL相关路由数量: {len(aapl_routes)}")
            
            for ticker, channels in aapl_routes.items():
                print(f"     {ticker}: {len(channels)} 个频道 -> {channels}")
                
        except Exception as e:
            print(f"   ❌ 测试4失败: {e}")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    return True

def main():
    """主函数"""
    print("🚀 开始深入调试...")
    deep_debug_config()
    print("✅ 调试完成!")

if __name__ == "__main__":
    main()
