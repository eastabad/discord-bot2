#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断OrderBlock频道状态
检查频道是否存在、Bot是否有权限、消息是否成功发送
"""

import asyncio
import discord
import os
import sys

# 添加项目路径
sys.path.append('/opt/discord-bot')

async def diagnose_channels():
    """诊断频道状态"""
    
    print("🔍 诊断OrderBlock频道状态")
    print("=" * 50)
    
    try:
        # 导入bot实例
        from bot import bot
        
        # 等待bot准备就绪
        await asyncio.sleep(2)
        
        # 测试的频道ID
        test_channels = [
            "1404532905916760125",  # 第一个默认频道
            "1410289768109047879",  # 第二个默认频道
            "1411097396280299540"   # 配置中的第一个默认频道
        ]
        
        print(f"🤖 Bot状态: {bot.user.name}#{bot.user.discriminator}")
        print(f"🏠 服务器数量: {len(bot.guilds)}")
        print()
        
        for channel_id in test_channels:
            print(f"📺 检查频道: {channel_id}")
            
            try:
                # 获取频道对象
                channel = bot.get_channel(int(channel_id))
                
                if channel:
                    print(f"   ✅ 频道存在: {channel.name}")
                    print(f"   🏠 服务器: {channel.guild.name}")
                    print(f"   📝 类型: {channel.type}")
                    
                    # 检查Bot权限
                    bot_member = channel.guild.get_member(bot.user.id)
                    if bot_member:
                        permissions = channel.permissions_for(bot_member)
                        print(f"   🔐 发送消息权限: {permissions.send_messages}")
                        print(f"   🔐 嵌入链接权限: {permissions.embed_links}")
                        print(f"   🔐 附加文件权限: {permissions.attach_files}")
                        
                        if permissions.send_messages:
                            print(f"   🚀 尝试发送测试消息...")
                            try:
                                test_msg = await channel.send("🧪 OrderBlock频道诊断测试消息")
                                print(f"   ✅ 测试消息发送成功: {test_msg.id}")
                                
                                # 删除测试消息
                                await test_msg.delete()
                                print(f"   🗑️  测试消息已删除")
                                
                            except Exception as e:
                                print(f"   ❌ 发送测试消息失败: {e}")
                        else:
                            print(f"   ❌ Bot没有发送消息权限")
                    else:
                        print(f"   ❌ Bot不是该服务器的成员")
                        
                else:
                    print(f"   ❌ 频道不存在或Bot无法访问")
                    
            except Exception as e:
                print(f"   ❌ 检查频道时出错: {e}")
                
            print()
            
        # 检查所有服务器中的频道
        print("🏠 检查Bot所在的所有服务器:")
        for guild in bot.guilds:
            print(f"   📋 {guild.name} (ID: {guild.id})")
            print(f"      👥 成员数: {guild.member_count}")
            print(f"      📺 频道数: {len(guild.channels)}")
            
            # 检查是否有我们关心的频道
            for channel_id in test_channels:
                if guild.get_channel(int(channel_id)):
                    print(f"      🎯 找到目标频道: {channel_id}")
                    
            print()
            
    except Exception as e:
        print(f"❌ 诊断过程中出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 开始频道诊断...")
    
    # 运行异步诊断
    asyncio.run(diagnose_channels())
    
    print("✅ 诊断完成!")

if __name__ == "__main__":
    main()
