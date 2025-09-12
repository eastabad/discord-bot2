#!/usr/bin/env python3
"""
批量清理频道的Python脚本
"""

import requests
import time
import json

def clean_channels():
    """批量清理频道"""
    
    # 频道ID列表
    channels = [
        ("1405694936191602730", "AAPL-1"),
        ("1384983850043576383", "AAPL-2"),
        ("1405694951232110644", "AMD-1"),
        ("1384987734342369331", "AMD-2"),
        ("1405694944303382558", "AMZN-1"),
        ("1384977574165348433", "AMZN-2"),
        ("1405694949533548684", "COIN-1"),
        ("1384989426584916019", "COIN-2"),
        ("1405694938561122325", "GOOG-1"),
        ("1384982848796102686", "GOOG-2"),
        ("1405694947738259496", "META-1"),
        ("1384982180865904810", "META-2"),
        ("1405694940423655617", "MSFT-1"),
        ("1384984501251211354", "MSFT-2"),
        ("1405694952918351932", "MSTR-1"),
        ("1384989015458975856", "MSTR-2"),
        ("1405694945809141781", "NVDA-1"),
        ("1384974332362620938", "NVDA-2"),
        ("1405694942608621751", "TSLA-1"),
        ("1384969246978736269", "TSLA-2")
    ]
    
    print(f"🧹 开始批量清理 {len(channels)} 个频道...")
    print("=" * 60)
    
    success_count = 0
    total_deleted = 0
    
    for i, (channel_id, channel_name) in enumerate(channels, 1):
        try:
            print(f"📋 [{i:2d}/{len(channels)}] 清理 {channel_name} ({channel_id})...")
            
            # 调用cleanup API
            response = requests.post(
                'http://localhost:5000/api/cleanup',
                headers={'Content-Type': 'application/json'},
                json={'channel_id': channel_id},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                deleted_count = result.get('deleted_count', 0)
                total_deleted += deleted_count
                success_count += 1
                
                print(f"   ✅ 成功: 删除了 {deleted_count} 条消息")
            else:
                print(f"   ❌ 失败: HTTP {response.status_code}")
                print(f"       响应: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        # 频道间稍作休息
        if i < len(channels):
            time.sleep(1)
    
    print("=" * 60)
    print(f"🎉 批量清理完成！")
    print(f"📊 统计结果:")
    print(f"   • 成功清理: {success_count}/{len(channels)} 个频道")
    print(f"   • 总删除消息: {total_deleted} 条")
    
    return success_count, total_deleted

if __name__ == "__main__":
    clean_channels()
