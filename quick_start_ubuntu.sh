#!/bin/bash
# 快速启动脚本 - Ubuntu
# 使用方法: bash quick_start_ubuntu.sh

echo "========================================"
echo "快速启动人脸识别服务"
echo "========================================"

# 激活 conda 环境
eval "$(conda shell.bash hook)"
conda activate face_mobile_recognition

# 检查并安装依赖
if ! python -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
fi

# 启动服务
echo ""
echo "启动服务..."
python start_server.py
