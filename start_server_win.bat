@echo off
chcp 65001 >nul
echo ========================================
echo 人脸识别异步服务启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo [1/3] 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到缺少依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/3] 启动服务...
echo.
python start_server.py

pause
