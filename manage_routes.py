#!/usr/bin/env python3
"""
Order Block路由管理命令行工具
用于管理orderblock_routes.conf配置文件
"""

import sys
import os
from orderblock_config_manager import OrderBlockConfigManager

def print_help():
    print("Order Block路由管理工具")
    print("用法:")
    print("  python manage_routes.py list                           # 列出所有路由")
    print("  python manage_routes.py add TICKER CHANNEL_ID          # 添加路由")
    print("  python manage_routes.py set TICKER CHANNEL_ID1,ID2...  # 设置ticker的所有频道")
    print("  python manage_routes.py remove TICKER                  # 删除ticker")
    print("  python manage_routes.py validate                       # 验证配置")
    print("  python manage_routes.py status                         # 显示配置状态")
    print("")
    print("示例:")
    print("  python manage_routes.py add NASDAQ:TSLA 1404532905916760125")
    print("  python manage_routes.py set NVDA 1405694945809141781,1404532905916760125")
    print("  python manage_routes.py list")

def format_channel_list(channel_ids):
    """格式化频道ID列表显示"""
    return ', '.join(str(c) for c in channel_ids)

def main():
    if len(sys.argv) < 2:
        print_help()
        return

    try:
        manager = OrderBlockConfigManager()
        command = sys.argv[1].lower()

        if command == "list":
            routes = manager.get_routes()
            default_channel = manager.get_default_channel()
            
            print("📋 Order Block路由配置:")
            print("=" * 60)
            
            # 显示默认频道
            if default_channel:
                print(f"🏠 默认频道: {default_channel}")
            else:
                print("⚠️  未配置默认频道")
            print()
            
            # 显示ticker路由
            if routes:
                print(f"📊 Ticker路由 ({len(routes)} 个):")
                for ticker in sorted(routes.keys()):
                    channels = routes[ticker]
                    print(f"  {ticker:<20} -> {format_channel_list(channels)}")
                print()
            else:
                print("❌ 暂无ticker路由配置")
                print("使用以下命令添加配置:")
                print("  python manage_routes.py add NASDAQ:TSLA 1404532905916760125")

        elif command == "add" and len(sys.argv) >= 4:
            ticker = sys.argv[2]
            try:
                channel_id = int(sys.argv[3])
                manager.add_channel_to_ticker(ticker, channel_id)
                manager.save_config()
                print(f"✅ 已添加路由: {ticker} -> {channel_id}")
                
                # 显示当前该ticker的所有频道
                channels = manager.get_channels_for_ticker(ticker)
                print(f"📊 {ticker} 当前映射到: {format_channel_list(channels)}")
            except ValueError:
                print("❌ 错误: 频道ID必须是数字")

        elif command == "set" and len(sys.argv) >= 4:
            ticker = sys.argv[2]
            channels_str = sys.argv[3]
            
            try:
                # 解析频道ID列表
                channel_ids = []
                for channel_str in channels_str.split(','):
                    channel_str = channel_str.strip()
                    if channel_str:
                        channel_ids.append(int(channel_str))
                
                if channel_ids:
                    manager.set_ticker_channels(ticker, channel_ids)
                    manager.save_config()
                    print(f"✅ 已设置 {ticker} 的路由: {format_channel_list(channel_ids)}")
                else:
                    print("❌ 错误: 未提供有效的频道ID")
            except ValueError:
                print("❌ 错误: 频道ID必须是数字，多个ID用逗号分隔")

        elif command == "remove" and len(sys.argv) >= 3:
            ticker = sys.argv[2]
            if manager.remove_ticker(ticker):
                manager.save_config()
                print(f"✅ 已删除ticker: {ticker}")
            else:
                print(f"❌ ticker不存在: {ticker}")

        elif command == "validate":
            errors = manager.validate_config()
            if errors:
                print("❌ 配置验证失败:")
                for error in errors:
                    print(f"   • {error}")
                sys.exit(1)
            else:
                print("✅ 配置验证通过")

        elif command == "status":
            routes = manager.get_routes()
            usage = manager.get_channel_usage()
            
            print("📊 配置状态报告")
            print("=" * 50)
            print(f"总ticker数量: {len(routes)}")
            print(f"总频道数量: {len(usage)}")
            print()
            
            if usage:
                print("频道使用情况:")
                for channel_id, tickers in usage.items():
                    print(f"  频道 {channel_id}: {len(tickers)} 个ticker")
                    for ticker in tickers:
                        print(f"    • {ticker}")
                print()
            
            # 验证配置
            errors = manager.validate_config()
            if errors:
                print("⚠️  配置问题:")
                for error in errors:
                    print(f"   • {error}")
            else:
                print("✅ 配置正常")

        elif command == "help":
            print_help()

        else:
            print("❌ 无效的命令")
            print_help()
            sys.exit(1)

    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()