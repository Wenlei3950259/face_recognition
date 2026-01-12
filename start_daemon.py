#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
后台启动脚本 - 使用 subprocess 实现
无需额外依赖，启动后自动转入后台
"""
import subprocess
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config

def start_daemon():
    """以守护进程模式启动服务"""
    host = config.get("server.host", "0.0.0.0")
    port = config.get("server.port", 5000)
    
    print("=" * 60)
    print("🚀 人脸识别异步服务 - 后台启动")
    print("=" * 60)
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    print(f"🔍 健康检查: http://{host}:{port}/health")
    print(f"📝 日志文件: log/face_recognition.log")
    print(f"📝 服务日志: server.log")
    print("=" * 60)
    
    # 检查端口是否被占用
    check_port = subprocess.run(
        f"lsof -ti:{port}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if check_port.stdout.strip():
        print(f"⚠️  警告: 端口 {port} 已被占用")
        print(f"进程ID: {check_port.stdout.strip()}")
        response = input("是否停止旧进程并重启？(y/n): ")
        if response.lower() == 'y':
            subprocess.run(f"kill -9 {check_port.stdout.strip()}", shell=True)
            print("✅ 已停止旧进程")
            time.sleep(2)
        else:
            print("❌ 启动取消")
            return
    
    # 启动服务（后台运行）
    log_file = "server.log"
    cmd = f"nohup python start_server.py > {log_file} 2>&1 &"
    
    print(f"\n🔄 正在启动服务...")
    subprocess.run(cmd, shell=True)
    
    # 等待服务启动
    print("⏳ 等待服务初始化...")
    max_wait = 30  # 最多等待30秒
    wait_interval = 2  # 每2秒检查一次
    
    for i in range(max_wait // wait_interval):
        time.sleep(wait_interval)
        
        # 检查服务是否启动成功
        check_process = subprocess.run(
            f"lsof -ti:{port}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if check_process.stdout.strip():
            pid = check_process.stdout.strip()
            print(f"\n✅ 服务启动成功！")
            print(f"📌 进程ID: {pid}")
            print(f"\n管理命令:")
            print(f"  查看日志: tail -f {log_file}")
            print(f"  查看状态: ps aux | grep start_server")
            print(f"  停止服务: kill -9 {pid}")
            print(f"  或使用: kill -9 $(lsof -ti:{port})")
            print(f"\n验证服务:")
            print(f"  curl http://localhost:{port}/health")
            print("\n" + "=" * 60)
            print("✨ 服务已在后台运行，可以安全关闭终端")
            print("=" * 60)
            return
    
    # 超时未启动成功
    print(f"\n❌ 服务启动失败或启动时间过长")
    print(f"请查看日志: tail -f {log_file}")
    print(f"\n可能的原因:")
    print(f"  1. 依赖未安装完整")
    print(f"  2. 模型文件下载中（首次启动需要下载约500MB模型）")
    print(f"  3. 配置文件错误")
    print(f"  4. 端口权限问题")
    print(f"\n建议:")
    print(f"  1. 查看详细日志: cat {log_file}")
    print(f"  2. 前台运行查看错误: python start_server.py")
    print(f"  3. 检查依赖: pip list | grep -E 'fastapi|insightface'")

if __name__ == "__main__":
    start_daemon()
