# VPS更新检查清单

## 更新前准备
- [ ] 确认VPS连接正常
- [ ] 备份现有`.env`文件
- [ ] 确认数据库连接正常
- [ ] 记录当前容器状态

## 核心文件更新
需要更新的关键文件:
- [ ] `bot.py` - TradersPost命令修复 + DMChannel错误修复
- [ ] `multi_ai_service.py` - Gemini 2.5 Pro优化 + 配额管理
- [ ] `config/simple_ai_templates.json` - AI模板配置
- [ ] `models.py` - 数据库模型定义
- [ ] `webhook_service.py` - Webhook处理逻辑

## Docker更新步骤
1. [ ] 停止现有容器: `docker-compose down`
2. [ ] 更新文件到VPS (手动上传或rsync)
3. [ ] 重建镜像: `docker-compose build --no-cache discord-bot`
4. [ ] 启动服务: `docker-compose up -d`
5. [ ] 等待15秒让服务完全启动

## 部署后验证
### 基础服务检查
- [ ] `docker-compose ps` 显示所有容器运行中
- [ ] `curl http://localhost:5000/api/health` 返回正常
- [ ] `curl http://localhost:5000/api/ai-status` 显示4个AI模型可用

### Discord Bot功能验证
- [ ] 私信测试 `!traderpost info` 有正确响应
- [ ] 私信测试 `!traderspost` 显示帮助信息
- [ ] 图表命令 `CT TSLA` 能生成图表
- [ ] 报告命令 `RP TSLA` 能生成AI分析

### AI模型测试
- [ ] Gemini 2.5 Pro 响应正常
- [ ] 配额耗尽时能自动切换到备用模型
- [ ] AI报告质量符合预期

### Webhook功能测试  
- [ ] TradingView webhook接收正常
- [ ] 个人webhook URL生成正常
- [ ] TradersPost集成按钮功能正常

## 故障排除检查
如果遇到问题，检查以下项目:
- [ ] `docker-compose logs discord-bot` 查看错误日志
- [ ] 环境变量是否正确配置
- [ ] 数据库连接是否正常
- [ ] 端口5000和8081是否被占用
- [ ] API密钥是否有效

## 性能监控
部署后持续监控:
- [ ] 内存使用情况
- [ ] AI API调用频率
- [ ] 错误日志数量
- [ ] 用户请求响应时间

## 回滚计划
如果更新失败:
1. [ ] 恢复备份的文件
2. [ ] `docker-compose down && docker-compose up -d`
3. [ ] 验证基础功能正常
4. [ ] 调查失败原因

---
**更新完成时间:** ________________  
**验证人员:** ________________  
**备注:** ________________