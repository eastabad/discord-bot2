#!/usr/bin/env python3
"""
生产环境Discord机器人入口文件
兼容Docker部署和VPS直接部署
"""

# 导入主程序
from main_with_api import main
import asyncio

if __name__ == "__main__":
    """程序入口点 - 兼容Docker CMD"""
    asyncio.run(main())