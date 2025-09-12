#!/bin/bash
# 修复Nginx SSL配置错误
set -e

echo "🔧 修复Nginx SSL配置..."

# 检查是否提供了域名参数
DOMAIN_NAME="$1"

if [ "$DOMAIN_NAME" != "" ]; then
    echo "🌐 配置域名: $DOMAIN_NAME"
    
    # 创建带域名但先不启用SSL的配置
    cat > /etc/nginx/sites-available/discord-bot << EOF
# HTTP配置 - 用于Let's Encrypt验证
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    # Let's Encrypt验证目录
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # API路由
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Webhook路由
    location /webhook/ {
        proxy_pass http://127.0.0.1:5000/webhook/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 配置管理
    location /config/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:5000/api/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 默认路由
    location / {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    echo "✅ 创建了HTTP-only配置，等待SSL证书申请"
    
else
    echo "🌐 配置IP访问模式"
    
    # 创建仅IP访问的配置
    cat > /etc/nginx/sites-available/discord-bot << 'EOF'
server {
    listen 80;
    server_name _;
    
    # API路由
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Webhook路由
    location /webhook/ {
        proxy_pass http://127.0.0.1:5000/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 配置管理
    location /config/ {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:5000/api/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 默认路由
    location / {
        proxy_pass http://127.0.0.1:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

    echo "✅ 创建了IP访问配置"
fi

# 启用配置
ln -sf /etc/nginx/sites-available/discord-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 确保webroot目录存在
mkdir -p /var/www/html

# 测试配置
echo "🔧 测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx配置测试通过"
    
    # 重启Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    echo "✅ Nginx已重启"
    
    # 如果有域名，申请SSL证书
    if [ "$DOMAIN_NAME" != "" ]; then
        echo "🔒 准备申请SSL证书..."
        echo "请确保域名 $DOMAIN_NAME 已正确解析到此服务器"
        
        read -p "域名解析是否已完成？(y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🔒 申请SSL证书..."
            
            # 申请SSL证书
            certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME --redirect
            
            if [ $? -eq 0 ]; then
                echo "✅ SSL证书申请成功"
                
                # 设置自动续期
                echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
                echo "✅ SSL证书自动续期已设置"
                
                # 测试配置
                nginx -t && systemctl reload nginx
                
                echo "🌐 HTTPS访问地址:"
                echo "  - https://$DOMAIN_NAME"
                echo "  - https://$DOMAIN_NAME/config/"
                echo "  - https://$DOMAIN_NAME/health"
                
            else
                echo "⚠️ SSL证书申请失败，继续使用HTTP"
            fi
        else
            echo "⚠️ 请先配置域名解析，稍后可手动申请SSL:"
            echo "certbot --nginx -d $DOMAIN_NAME"
        fi
    fi
    
    # 显示访问信息
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo
    echo "✅ Nginx配置修复完成"
    echo "🌐 访问地址:"
    echo "  - 主页: http://$SERVER_IP"
    echo "  - 配置: http://$SERVER_IP/config/"
    echo "  - 健康: http://$SERVER_IP/health"
    echo "  - Webhook: http://$SERVER_IP/webhook/tradingview"
    
    if [ "$DOMAIN_NAME" != "" ]; then
        echo "  - 域名: http://$DOMAIN_NAME (或 https 如果SSL成功)"
    fi
    
else
    echo "❌ Nginx配置测试失败"
    nginx -t
    exit 1
fi