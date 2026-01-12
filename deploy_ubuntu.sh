#!/bin/bash
# Ubuntu 服务器自动部署脚本
# 使用方法: bash deploy_ubuntu.sh

set -e  # 遇到错误立即退出

echo "========================================"
echo "人脸识别异步服务 - Ubuntu 部署脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/home/face/face_recognition"
CONDA_ENV="face_mobile_recognition"

# 检查是否在项目目录
if [ ! -f "start_server.py" ]; then
    echo -e "${RED}[错误] 请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${GREEN}[1/5] 检查 Conda 环境...${NC}"
if ! command -v conda &> /dev/null; then
    echo -e "${RED}[错误] 未检测到 Conda，请先安装 Miniconda 或 Anaconda${NC}"
    exit 1
fi

# 检查环境是否存在
if ! conda env list | grep -q "$CONDA_ENV"; then
    echo -e "${RED}[错误] Conda 环境 '$CONDA_ENV' 不存在${NC}"
    echo "请先创建环境: conda create -n $CONDA_ENV python=3.8"
    exit 1
fi

echo -e "${GREEN}✓ Conda 环境检查通过${NC}"
echo ""

echo -e "${GREEN}[2/5] 激活 Conda 环境...${NC}"
# 初始化 conda
eval "$(conda shell.bash hook)"
conda activate $CONDA_ENV

if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 无法激活 Conda 环境${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境已激活: $CONDA_ENV${NC}"
python --version
echo ""

echo -e "${GREEN}[3/5] 检查已安装的依赖...${NC}"
# 检查是否已安装 FastAPI
if python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}依赖已安装，跳过安装步骤${NC}"
else
    echo -e "${YELLOW}正在安装项目依赖...${NC}"
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 依赖安装失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
fi
echo ""

echo -e "${GREEN}[4/5] 检查模型文件...${NC}"
MODEL_DIR="$HOME/.insightface/models/buffalo_l"
if [ -d "$MODEL_DIR" ]; then
    echo -e "${GREEN}✓ 模型文件已存在: $MODEL_DIR${NC}"
    ls -lh "$MODEL_DIR"
else
    echo -e "${YELLOW}⚠ 模型文件不存在，首次启动时会自动下载${NC}"
fi
echo ""

echo -e "${GREEN}[5/5] 检查配置文件...${NC}"
if [ -f "config/config.yaml" ]; then
    echo -e "${GREEN}✓ 配置文件存在${NC}"
    echo "服务配置:"
    grep -A 3 "^server:" config/config.yaml
else
    echo -e "${RED}[错误] 配置文件不存在${NC}"
    exit 1
fi
echo ""

echo "========================================"
echo -e "${GREEN}部署检查完成！${NC}"
echo "========================================"
echo ""
echo "启动选项:"
echo ""
echo "1. 前台启动（测试用）:"
echo "   python start_server.py"
echo ""
echo "2. 后台启动（推荐）:"
echo "   nohup python start_server.py > server.log 2>&1 &"
echo ""
echo "3. 使用 screen（推荐）:"
echo "   screen -S face_api"
echo "   python start_server.py"
echo "   # 按 Ctrl+A 然后 D 退出"
echo ""
echo "4. 使用 systemd（生产环境推荐）:"
echo "   参考 ubuntu_部署启动指南.md"
echo ""

# 询问是否立即启动
read -p "是否立即启动服务？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${GREEN}正在启动服务...${NC}"
    echo "按 Ctrl+C 可停止服务"
    echo ""
    python start_server.py
else
    echo ""
    echo -e "${YELLOW}部署完成，请手动启动服务${NC}"
fi
