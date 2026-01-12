#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断脚本 - 检查环境和依赖
"""
import sys
import os
import subprocess

def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python():
    """检查 Python 版本"""
    print_section("Python 版本")
    print(f"Python: {sys.version}")
    print(f"可执行文件: {sys.executable}")

def check_dependencies():
    """检查依赖包"""
    print_section("依赖包检查")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'insightface',
        'numpy',
        'torch',
        'opencv-python',
        'onnx',
        'onnxruntime',
        'pymysql',
        'yaml'
    ]
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                __import__('cv2')
                print(f"✅ {package}: 已安装")
            elif package == 'yaml':
                __import__('yaml')
                print(f"✅ PyYAML: 已安装")
            else:
                __import__(package)
                print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")

def check_config():
    """检查配置文件"""
    print_section("配置文件检查")
    
    config_file = "config/config.yaml"
    if os.path.exists(config_file):
        print(f"✅ 配置文件存在: {config_file}")
        try:
            from config import config
            host = config.get("server.host", "未设置")
            port = config.get("server.port", "未设置")
            print(f"   服务地址: {host}:{port}")
        except Exception as e:
            print(f"❌ 配置文件读取失败: {e}")
    else:
        print(f"❌ 配置文件不存在: {config_file}")

def check_models():
    """检查模型文件"""
    print_section("模型文件检查")
    
    model_paths = [
        os.path.expanduser("~/.insightface/models/buffalo_l"),
        "/root/.insightface/models/buffalo_l"
    ]
    
    found = False
    for path in model_paths:
        if os.path.exists(path):
            print(f"✅ 模型目录存在: {path}")
            files = os.listdir(path)
            print(f"   文件数量: {len(files)}")
            if len(files) >= 5:
                print(f"   ✅ 模型文件完整")
            else:
                print(f"   ⚠️  模型文件可能不完整（需要5个文件）")
            found = True
            break
    
    if not found:
        print(f"⚠️  模型目录不存在，首次启动会自动下载")

def check_port():
    """检查端口占用"""
    print_section("端口检查")
    
    try:
        from config import config
        port = config.get("server.port", 5000)
    except:
        port = 5000
    
    result = subprocess.run(
        f"lsof -ti:{port}",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print(f"⚠️  端口 {port} 已被占用")
        print(f"   进程ID: {result.stdout.strip()}")
        
        # 获取进程信息
        ps_result = subprocess.run(
            f"ps -p {result.stdout.strip()} -o pid,cmd",
            shell=True,
            capture_output=True,
            text=True
        )
        print(f"   进程信息:\n{ps_result.stdout}")
    else:
        print(f"✅ 端口 {port} 可用")

def check_logs():
    """检查日志文件"""
    print_section("日志文件检查")
    
    log_files = [
        "log/face_recognition.log",
        "server.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✅ {log_file}: {size} 字节")
            
            # 显示最后几行
            if size > 0:
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"   最后 3 行:")
                            for line in lines[-3:]:
                                print(f"   {line.rstrip()}")
                except Exception as e:
                    print(f"   ⚠️  无法读取: {e}")
        else:
            print(f"⚠️  {log_file}: 不存在")

def check_permissions():
    """检查文件权限"""
    print_section("权限检查")
    
    files_to_check = [
        "start_server.py",
        "config/config.yaml",
        "log"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_readable = os.access(file_path, os.R_OK)
            is_writable = os.access(file_path, os.W_OK)
            is_executable = os.access(file_path, os.X_OK)
            
            status = []
            if is_readable:
                status.append("读")
            if is_writable:
                status.append("写")
            if is_executable:
                status.append("执行")
            
            print(f"✅ {file_path}: {'/'.join(status)}")
        else:
            print(f"❌ {file_path}: 不存在")

def test_import():
    """测试导入核心模块"""
    print_section("模块导入测试")
    
    try:
        print("测试导入 config...")
        from config import config
        print("✅ config 导入成功")
        
        print("测试导入 face_process...")
        from face_process.init_InsightFace import init_face_model
        print("✅ face_process 导入成功")
        
        print("测试导入 core...")
        from core.face_core import encode_embedding
        print("✅ core 导入成功")
        
        print("测试导入 api...")
        # 不实际导入 api，因为会启动服务
        print("⚠️  api 模块跳过（避免启动服务）")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  人脸识别系统 - 环境诊断")
    print("=" * 60)
    
    check_python()
    check_dependencies()
    check_config()
    check_models()
    check_port()
    check_logs()
    check_permissions()
    test_import()
    
    print("\n" + "=" * 60)
    print("  诊断完成")
    print("=" * 60)
    print("\n建议:")
    print("  1. 如果依赖未安装，运行: pip install -r requirements.txt")
    print("  2. 如果端口被占用，运行: kill -9 $(lsof -ti:5000)")
    print("  3. 如果模型未下载，首次启动需要等待几分钟")
    print("  4. 查看详细日志: tail -f server.log")
    print("  5. 前台运行测试: python start_server.py")
    print()

if __name__ == "__main__":
    main()
