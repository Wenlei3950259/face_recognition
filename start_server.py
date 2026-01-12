#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI 异步服务启动脚本
支持前台运行模式
"""
import uvicorn
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config

if __name__ == "__main__":
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 5000)
    
    print(f"🚀 启动人脸识别异步服务...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"� API文档: http://{host}:{port}/docs")
    print(f"🔍 健康检查: http://{host}:{port}/health")
    
    uvicorn.run(
        "api.face_recognition_api:app",
        host=host,
        port=port,
        reload=False,
        workers=1,  # 单worker模式（模型全局单例）
        log_level="info",
        access_log=True
    )
