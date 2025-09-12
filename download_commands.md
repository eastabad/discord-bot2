# Discord Bot 部署脚本下载命令

## 方案1: 完整VPS部署脚本 (推荐)
包含Docker + Nginx反向代理 + SSL + 防火墙配置

```bash
# 下载完整部署脚本
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/COMPLETE_VPS_DEPLOYMENT.sh

# 给予执行权限
chmod +x COMPLETE_VPS_DEPLOYMENT.sh

# 执行部署
sudo bash COMPLETE_VPS_DEPLOYMENT.sh
```

## 方案2: 简化VPS部署脚本
仅包含Docker配置，需手动配置Nginx

```bash
# 下载简化部署脚本
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/FRESH_VPS_DEPLOYMENT.sh

# 给予执行权限
chmod +x FRESH_VPS_DEPLOYMENT.sh

# 执行部署
sudo bash FRESH_VPS_DEPLOYMENT.sh
```

## 方案3: 快速VPS修复脚本
修复现有VPS部署问题

```bash
# 下载修复脚本
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/VPS_DEPLOY_WORKING_VERSION.sh

# 给予执行权限
chmod +x VPS_DEPLOY_WORKING_VERSION.sh

# 在现有项目目录中执行
cd /opt/discord-bot
sudo bash VPS_DEPLOY_WORKING_VERSION.sh
```

## 部署指南下载

```bash
# 下载部署指南
wget https://raw.githubusercontent.com/eastabad/DiscordBot/main/VPS_QUICK_SETUP_GUIDE.md
```

## 使用建议

1. **全新VPS**: 使用 `COMPLETE_VPS_DEPLOYMENT.sh` (推荐)
2. **现有环境**: 使用 `VPS_DEPLOY_WORKING_VERSION.sh`
3. **手动配置**: 使用 `FRESH_VPS_DEPLOYMENT.sh`

所有脚本都包含完整的错误处理和验证功能。