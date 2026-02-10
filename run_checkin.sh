#!/bin/bash

# JavBus论坛多用户签到脚本执行器
# 设置执行时间和日志记录

echo "---------- JavBus论坛批量签到开始 ----------"
echo "当前时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "当前北京时间: $(date -u -d '+8 hour' '+%Y-%m-%d %H:%M:%S')"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3命令"
    exit 1
fi

# 检查依赖
if ! python3 -c "import requests, lxml" &> /dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 执行签到脚本
python3 checkin.py

echo "---------- JavBus论坛批量签到结束 ----------"