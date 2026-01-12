# Windows 部署启动指南

## 环境要求

- **操作系统**: Windows 10/11
- **Python**: 3.7+ (推荐 3.8)
- **Conda**: Miniconda 或 Anaconda
- **内存**: 建议 4GB 以上
- **磁盘**: 至少 2GB 可用空间

## 快速开始

### 方式一：使用批处理脚本（最简单）

```bash
# 双击运行或在命令行执行
start_server_win.bat
```

脚本会自动：
1. 检查 Python 环境
2. 检查并安装完整依赖（requirements.txt）
3. 启动服务

### 方式二：手动启动

#### 1. 激活 Conda 环境
```bash
# 如果环境在 E:\conda\envs\face_mobile_recognition
E:\conda\envs\face_mobile_recognition\Scripts\activate

# 或使用 conda activate
conda activate face_mobile_recognition
```

#### 2. 安装依赖（首次运行）
```bash
pip install -r requirements.txt
```

**包含的依赖**：
- FastAPI 及相关包（fastapi, uvicorn, python-multipart, slowapi, aiofiles）
- InsightFace 人脸识别（insightface, onnx, onnxruntime）
- 数据处理（numpy, torch, opencv-python）
- 其他工具（pymysql, PyYAML）

#### 3. 启动服务
```bash
python start_server.py
```

## 验证服务

### 1. 检查服务状态
```bash
# 使用 PowerShell
curl http://localhost:5000/health

# 或在浏览器访问
http://localhost:5000/health
```

期望输出：
```json
{"status":"healthy","service":"face-recognition-api"}
```

### 2. 查看 API 文档
在浏览器中打开：
```
http://localhost:5000/docs
```

### 3. 测试接口
使用 Postman 或 curl 测试接口（参考 README.md）

## 服务管理

### 启动服务
```bash
# 方式一：批处理脚本
start_server_win.bat

# 方式二：Python 脚本
python start_server.py
```

### 停止服务
- 在运行窗口按 `Ctrl+C`
- 或直接关闭命令行窗口

### 查看进程
```bash
# PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# CMD
tasklist | findstr python
```

### 停止进程
```bash
# 查找端口占用的进程
netstat -ano | findstr :5000

# 停止进程（替换 <PID> 为实际进程ID）
taskkill /PID <PID> /F
```

## 配置说明

### 配置文件位置
```
config/config.yaml
```

### 常用配置项
```yaml
server:
  host: "0.0.0.0"      # 监听地址
  port: 5000           # 服务端口

face_model:
  det_size: [640, 640] # 检测尺寸
  threshold: 0.5       # 相似度阈值

log:
  level: "INFO"        # 日志级别
  file: "log/face_recognition.log"
```

## 模型文件

### 模型位置
```
C:\Users\<用户名>\.insightface\models\buffalo_l\
```

### 首次启动
首次启动会自动下载模型文件（约 500MB），需要等待几分钟。

### 检查模型
```bash
# PowerShell
dir C:\Users\$env:USERNAME\.insightface\models\buffalo_l\
```

## 日志管理

### 日志位置
```
log/face_recognition.log
```

### 查看日志
```bash
# PowerShell - 查看最后 50 行
Get-Content log\face_recognition.log -Tail 50

# PowerShell - 实时查看
Get-Content log\face_recognition.log -Wait -Tail 50
```

### 日志级别
修改 `config/config.yaml` 中的 `log.level`:
- `DEBUG`: 调试信息
- `INFO`: 一般信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息

## 常见问题

### Q1: 端口被占用
```bash
# 查看端口占用
netstat -ano | findstr :5000

# 停止占用进程
taskkill /PID <进程ID> /F

# 或修改配置文件中的端口
```

### Q2: 模块导入错误
```bash
# 重新安装依赖
pip install -r requirements.txt

# 或单独安装缺失的包
pip install <包名>
```

### Q3: 模型下载失败
```bash
# 检查网络连接
# 或手动下载模型文件放到指定目录
# C:\Users\<用户名>\.insightface\models\buffalo_l\
```

### Q4: 权限问题
以管理员身份运行命令行或 PowerShell

### Q5: Conda 环境激活失败
```bash
# 使用完整路径激活
E:\conda\envs\face_mobile_recognition\python.exe start_server.py
```

## 性能优化

### 1. 使用 GPU 加速（如果有 NVIDIA 显卡）
修改 `config/config.yaml`:
```yaml
face_model:
  providers: ["CUDAExecutionProvider", "CPUExecutionProvider"]
```

需要安装：
```bash
pip install onnxruntime-gpu
```

### 2. 调整线程池大小
修改 `config/config.yaml`:
```yaml
face_model:
  thread_pool_workers: 8  # 根据 CPU 核心数调整
```

### 3. 调整检测尺寸
```yaml
face_model:
  det_size: [320, 320]  # 降低尺寸提升速度，但可能降低准确度
```

## 开发调试

### 启用调试模式
修改 `config/config.yaml`:
```yaml
server:
  debug: true

log:
  level: "DEBUG"
```

### 热重载（开发时）
```bash
# 使用 uvicorn 直接启动（支持热重载）
uvicorn api.face_recognition_api:app --reload --host 0.0.0.0 --port 5000
```

## 测试

### 运行测试脚本
```bash
python test_async_api.py
```

### 手动测试
```bash
# 健康检查
curl http://localhost:5000/health

# 使用 Postman 测试完整接口
```

## 防火墙配置

### Windows Defender 防火墙
1. 打开 Windows Defender 防火墙
2. 点击"高级设置"
3. 入站规则 → 新建规则
4. 选择"端口" → TCP → 特定本地端口 5000
5. 允许连接 → 完成

### 或使用命令行
```bash
# PowerShell（管理员）
New-NetFirewallRule -DisplayName "Face API" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

## 外网访问

### 1. 确认配置
```yaml
server:
  host: "0.0.0.0"  # 允许外网访问
```

### 2. 配置防火墙
允许 5000 端口入站连接

### 3. 配置路由器
如果在内网，需要配置端口转发

### 4. 使用内网穿透（可选）
- ngrok
- frp
- 花生壳

## 生产部署建议

### 1. 使用 Windows 服务
可以使用 NSSM 将 Python 脚本注册为 Windows 服务

### 2. 使用任务计划程序
设置开机自动启动

### 3. 使用 IIS 反向代理
配置 IIS 作为反向代理服务器

## 备份和恢复

### 备份
```bash
# 备份整个项目
xcopy /E /I face_recognition face_recognition_backup

# 备份配置和日志
xcopy /E /I config config_backup
xcopy /E /I log log_backup
```

### 恢复
```bash
xcopy /E /I face_recognition_backup face_recognition
```

## 卸载

### 1. 停止服务
按 Ctrl+C 或关闭窗口

### 2. 删除项目文件
删除项目目录

### 3. 删除 Conda 环境（可选）
```bash
conda env remove -n face_mobile_recognition
```

### 4. 删除模型文件（可选）
```bash
rmdir /S /Q C:\Users\<用户名>\.insightface
```

## 技术支持

- **主文档**: README.md
- **日志文件**: log/face_recognition.log
- **API 文档**: http://localhost:5000/docs

---

**祝使用愉快！** 🚀
