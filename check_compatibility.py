#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 Python 3.11 兼容性
"""
import sys

print(f"Python 版本: {sys.version}")
print(f"版本号: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

if sys.version_info >= (3, 11):
    print("\n⚠️  警告: Python 3.11+ 可能存在兼容性问题")
    print("推荐使用 Python 3.8 - 3.10")
    print()

print("测试导入关键模块...")

try:
    print("1. 测试 FastAPI...")
    from fastapi import FastAPI
    print("   ✅ FastAPI 导入成功")
except Exception as e:
    print(f"   ❌ FastAPI 导入失败: {e}")

try:
    print("2. 测试 Uvicorn...")
    import uvicorn
    print("   ✅ Uvicorn 导入成功")
except Exception as e:
    print(f"   ❌ Uvicorn 导入失败: {e}")

try:
    print("3. 测试 Pydantic...")
    from pydantic import BaseModel
    print("   ✅ Pydantic 导入成功")
except Exception as e:
    print(f"   ❌ Pydantic 导入失败: {e}")

try:
    print("4. 测试 API 模块...")
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 尝试导入 API 模块
    from api import face_recognition_api
    print("   ✅ API 模块导入成功")
except Exception as e:
    print(f"   ❌ API 模块导入失败: {e}")
    import traceback
    print("\n详细错误:")
    traceback.print_exc()

print("\n" + "="*60)
print("如果看到导入失败，建议:")
print("1. 创建 Python 3.8 环境:")
print("   conda create -n face_recognition_py38 python=3.8")
print("   conda activate face_recognition_py38")
print("   pip install -r requirements.txt")
print()
print("2. 或者尝试前台运行查看详细错误:")
print("   python start_server.py")
print("="*60)
