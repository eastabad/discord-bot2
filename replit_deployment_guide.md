# Replit Discord Bot 部署指南

## 🚨 重要：部署类型选择

根据Replit官方文档，Discord Bot需要使用 **Reserved VM 部署**，不是 Autoscale。

### 为什么需要Reserved VM？

1. **持续连接**：Discord Bot需要保持与Discord网关的长连接
2. **后台运行**：Bot需要在没有HTTP请求时也保持运行  
3. **稳定性**：避免Autoscale的自动重启影响Bot连接

## 📋 部署步骤

### 1. 准备环境变量
确保在Replit Secrets中设置了：
- `DISCORD_TOKEN` - Discord机器人令牌
- `GEMINI_API_KEY` - Google Gemini API密钥
- `DATABASE_URL` - PostgreSQL数据库连接（已自动配置）

### 2. 选择正确的部署类型
1. 点击 **Deploy** 按钮
2. 选择 **Reserved VM** （不要选择Autoscale）
3. 配置资源：推荐4 vCPU / 8 GiB RAM
4. 点击部署

### 3. 验证部署
部署成功后：
- Bot会自动连接到Discord服务器
- API端点将在 `https://your-repl.replit.app` 可用
- TradingView webhook地址：`https://your-repl.replit.app/webhook/tradingview`

## 🔗 API端点

部署后可用的端点：
- `GET /api/health` - 健康检查
- `POST /webhook/tradingview` - TradingView webhook
- `POST /api/send-message` - 发送Discord消息
- `POST /api/send-dm` - 发送私信
- `POST /api/send-chart` - 发送图表

## 🛠️ 故障排除

### 如果部署失败：
1. 检查所有环境变量是否设置正确
2. 确保选择了Reserved VM而不是Autoscale
3. 查看部署日志中的错误信息
4. 确认Discord Token有效且有足够权限

### 常见问题：
- **"Address already in use"**：确保只有一个工作流在运行
- **"Invalid Discord Token"**：检查DISCORD_TOKEN是否正确设置
- **"Database connection failed"**：确保生产数据库已连接

## ✅ 当前状态

- ✅ Discord Bot代码准备完成
- ✅ API服务器集成完成  
- ✅ 工作流配置正确
- ✅ 环境变量验证通过
- 🔄 等待Reserved VM部署

## 📝 部署后验证清单

部署完成后验证：
- [ ] Discord Bot在线状态
- [ ] API健康检查响应正常
- [ ] TradingView webhook接收测试
- [ ] 数据库连接正常
- [ ] 日志输出无错误