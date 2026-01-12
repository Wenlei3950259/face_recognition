#!/bin/bash
# Linux/Mac 启动脚本

echo "========================================"
echo "人脸识别异步服务启动脚本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装"
    exit 1
fi

echo "[1/3] 检查依赖包..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "[提示] 检测到缺少依赖，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi
fi

echo "[2/3] 启动服务..."
echo ""
python3 start_server.py
