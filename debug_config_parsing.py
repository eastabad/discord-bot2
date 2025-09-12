#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OrderBlock配置文件解析
直接在VPS上测试配置文件解析逻辑
"""

def debug_config_parsing():
    """调试配置文件解析"""
    
    print("🔍 调试OrderBlock配置文件解析")
    print("=" * 50)
    
    # 配置文件路径
    config_file = "/opt/discord-bot/orderblock_routes.conf"
    
    print(f"📝 配置文件: {config_file}")
    print()
    
    try:
        # 读取配置文件
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📊 文件总行数: {len(lines)}")
        print()
        
        # 解析配置
        routes = {}
        default_channels = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue
            
            # 解析配置行
            if '=' in line:
                key, value_str = line.split('=', 1)
                key = key.strip()
                value_str = value_str.strip()
                
                if not key or not value_str:
                    print(f"⚠️  第{line_num}行格式错误: {line}")
                    continue
                
                # 处理默认频道配置
                if key == 'DEFAULT_CHANNEL':
                    default_channel_ids = []
                    for channel_str in value_str.split(','):
                        channel_str = channel_str.strip()
                        if channel_str:
                            try:
                                channel_id = int(channel_str)
                                default_channel_ids.append(channel_id)
                            except ValueError:
                                print(f"⚠️  无效的默认频道ID: {channel_str} (第{line_num}行)")
                    default_channels = default_channel_ids
                    print(f"✅ 默认频道: {default_channels}")
                    continue
                
                # 解析ticker路由频道ID列表
                channel_ids = []
                for channel_str in value_str.split(','):
                    channel_str = channel_str.strip()
                    if channel_str:
                        try:
                            channel_id = int(channel_str)
                            channel_ids.append(channel_id)
                        except ValueError:
                            print(f"⚠️  无效的频道ID: {channel_str} (第{line_num}行)")
                
                if channel_ids:
                    routes[key] = channel_ids
                    print(f"✅ 路由 {key}: {channel_ids}")
                else:
                    print(f"⚠️  第{line_num}行没有有效频道ID: {line}")
        
        print(f"\n📊 解析结果:")
        print(f"   总路由数: {len(routes)}")
        print(f"   默认频道: {default_channels}")
        
        # 检查特定ticker
        test_tickers = ['AAPL', 'NYSE:AAPL', 'NASDAQ:TSLA']
        print(f"\n🧪 检查特定ticker:")
        for ticker in test_tickers:
            if ticker in routes:
                channels = routes[ticker]
                print(f"   {ticker}: {len(channels)} 个频道 -> {channels}")
            else:
                print(f"   {ticker}: 未找到")
        
        # 检查是否有重复的ticker
        print(f"\n🔍 检查重复ticker:")
        ticker_count = {}
        for ticker in routes.keys():
            if ticker in ticker_count:
                ticker_count[ticker] += 1
            else:
                ticker_count[ticker] = 1
        
        for ticker, count in ticker_count.items():
            if count > 1:
                print(f"   ⚠️  {ticker}: 出现 {count} 次")
        
        # 显示所有路由
        print(f"\n📋 所有路由:")
        for ticker, channels in routes.items():
            print(f"   {ticker}: {channels}")
            
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    return True

def main():
    """主函数"""
    print("🚀 开始配置文件解析调试...")
    debug_config_parsing()
    print("✅ 调试完成!")

if __name__ == "__main__":
    main()
