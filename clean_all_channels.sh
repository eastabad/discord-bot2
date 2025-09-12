#!/bin/bash

# 清理所有orderblock_routes.conf中指定的频道

echo "🧹 开始清理所有指定频道..."

# 频道ID列表
channels=(
    "1405694936191602730"  # AAPL
    "1384983850043576383"  # AAPL
    "1405694951232110644"  # AMD
    "1384987734342369331"  # AMD
    "1405694944303382558"  # AMZN
    "1384977574165348433"  # AMZN
    "1405694949533548684"  # COIN
    "1384989426584916019"  # COIN
    "1405694938561122325"  # GOOG
    "1384982848796102686"  # GOOG
    "1405694947738259496"  # META
    "1384982180865904810"  # META
    "1405694940423655617"  # MSFT
    "1384984501251211354"  # MSFT
    "1405694952918351932"  # MSTR
    "1384989015458975856"  # MSTR
    "1405694945809141781"  # NVDA
    "1384974332362620938"  # NVDA
    "1405694942608621751"  # TSLA
    "1384969246978736269"  # TSLA
)

total_channels=${#channels[@]}
cleaned_count=0

echo "📋 总共需要清理 $total_channels 个频道"

for i in "${!channels[@]}"; do
    channel_id="${channels[$i]}"
    echo "📋 [$((i+1))/$total_channels] 清理频道 $channel_id..."
    
    # 调用cleanup API
    response=$(curl -s -X POST 'http://localhost:5000/api/cleanup' \
        -H 'Content-Type: application/json' \
        -d "{\"channel_id\": \"$channel_id\"}")
    
    if echo "$response" | grep -q '"status": "success"'; then
        echo "   ✅ 成功清理"
        ((cleaned_count++))
    else
        echo "   ❌ 清理失败: $response"
    fi
    
    # 频道间稍作休息
    sleep 2
done

echo "🎉 清理完成！成功清理了 $cleaned_count/$total_channels 个频道"
