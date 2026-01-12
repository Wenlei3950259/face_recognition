#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
停止服务脚本
"""
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config

def stop_server():
    """停止服务"""
    port = config.get("server.port", 5000)
    
    print("=" * 60)
    print("🛑 停止人脸识别服务")
    print("=" * 60)
    
    # 查找占用端口的进程
    check_port = subprocess.run(
        f"lsof -ti:{port}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if not check_port.stdout.strip():
        print(f"ℹ️  端口 {port} 没有运行的服务")
        return
    
    pids = check_port.stdout.strip().split('\n')
    print(f"📌 找到 {len(pids)} 个进程:")
    for pid in pids:
        # 获取进程信息
        ps_info = subprocess.run(
            f"ps -p {pid} -o pid,cmd",
            shell=True,
            capture_output=True,
            text=True
        )
        print(ps_info.stdout)
    
    response = input(f"\n确认停止这些进程？(y/n): ")
    if response.lower() != 'y':
        print("❌ 操作取消")
        return
    
    # 停止进程
    for pid in pids:
        subprocess.run(f"kill -9 {pid}", shell=True)
        print(f"✅ 已停止进程 {pid}")
    
    print("\n" + "=" * 60)
    print("✨ 服务已停止")
    print("=" * 60)

if __name__ == "__main__":
    stop_server()
