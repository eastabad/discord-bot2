#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的频道状态检查
通过日志分析来诊断频道问题
"""

import subprocess
import re

def check_channel_status():
    """检查频道状态"""
    
    print("🔍 简单频道状态检查")
    print("=" * 50)
    
    # 要检查的频道ID
    test_channels = [
        "1404532905916760125",  # 第一个默认频道
        "1410289768109047879",  # 第二个默认频道
        "1411097396280299540"   # 配置中的第一个默认频道
    ]
    
    print("📊 检查的频道ID:")
    for channel_id in test_channels:
        print(f"   {channel_id}")
    print()
    
    # 检查最近的日志
    print("📋 检查最近的频道相关日志...")
    
    try:
        # 获取最近的日志
        result = subprocess.run([
            "docker", "logs", "discord-bot-main", "--tail", "200"
        ], capture_output=True, text=True, check=True)
        
        logs = result.stdout
        
        # 分析每个频道
        for channel_id in test_channels:
            print(f"📺 频道 {channel_id} 分析:")
            
            # 查找该频道的所有日志
            channel_logs = re.findall(f".*{channel_id}.*", logs)
            
            if channel_logs:
                print(f"   ✅ 找到 {len(channel_logs)} 条相关日志:")
                for log in channel_logs[-3:]:  # 显示最近3条
                    print(f"      {log.strip()}")
                    
                # 检查是否有错误
                error_logs = [log for log in channel_logs if "error" in log.lower() or "fail" in log.lower()]
                if error_logs:
                    print(f"   ⚠️  发现 {len(error_logs)} 条错误日志:")
                    for log in error_logs:
                        print(f"      ❌ {log.strip()}")
                else:
                    print(f"   ✅ 没有发现错误日志")
                    
            else:
                print(f"   ❌ 没有找到相关日志")
                
            print()
            
        # 检查整体统计
        print("📊 整体统计:")
        
        # 统计成功发送的消息
        success_sends = re.findall(r"Order Block信号.*已发送到频道.*", logs)
        print(f"   ✅ 成功发送: {len(success_sends)} 条")
        
        # 统计失败的发送
        failed_sends = re.findall(r"发送.*失败|failed|error", logs, re.IGNORECASE)
        print(f"   ❌ 发送失败: {len(failed_sends)} 条")
        
        # 统计权限相关错误
        permission_errors = re.findall(r"权限|permission|forbidden|unauthorized", logs, re.IGNORECASE)
        print(f"   🔐 权限错误: {len(permission_errors)} 条")
        
        # 统计频道不存在错误
        channel_not_found = re.findall(r"频道.*不存在|channel.*not.*found", logs, re.IGNORECASE)
        print(f"   📺 频道不存在: {len(channel_not_found)} 条")
        
        print()
        
        # 检查最近的错误
        print("🚨 最近的错误日志:")
        error_lines = re.findall(r".*ERROR.*|.*WARNING.*", logs)
        for line in error_lines[-5:]:  # 显示最近5条错误
            if any(channel_id in line for channel_id in test_channels):
                print(f"   {line.strip()}")
                
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行命令失败: {e}")
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")

def main():
    """主函数"""
    print("🚀 开始简单频道状态检查...")
    check_channel_status()
    print("✅ 检查完成!")

if __name__ == "__main__":
    main()
