# Ubuntu 服务器部署启动指南

## 环境信息
- **服务器**: Ubuntu
- **项目路径**: /home/face/face_recognition
- **Conda 环境**: face_mobile_recognition
- **Conda 路径**: /root/miniconda3/envs/face_mobile_recognition

## 快速启动步骤

### 1. 激活 Conda 环境
```bash
conda activate face_mobile_recognition
```

### 2. 安装项目依赖
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

**包含的依赖**：
- FastAPI 及相关包（fastapi, uvicorn, python-multipart, slowapi, aiofiles）
- InsightFace 人脸识别（insightface, onnx, onnxruntime）
- 数据处理（numpy, torch, opencv-python）
- 其他工具（pymysql, PyYAML）

**注意**：首次部署需要安装完整依赖，后续升级只需安装新增的 FastAPI 相关包。

### 3. 进入项目目录
```bash
cd /home/face/face_recognition
```

### 4. 启动服务
```bash
python start_server.py
```

## 完整命令（一键执行）

```bash
# 切换到项目目录
cd /home/face/face_recognition

# 激活环境
conda activate face_mobile_recognition

# 安装依赖（使用清华镜像）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 启动服务
python start_server.py
```

## 后台运行（推荐生产环境）

### 方式一：使用 nohup
```bash
cd /home/face/face_recognition
conda activate face_mobile_recognition
nohup python start_server.py > server.log 2>&1 &

# 查看日志
tail -f server.log

# 查看进程
ps aux | grep start_server

# 停止服务
kill -9 <进程ID>
```

### 方式二：使用 screen（推荐）
```bash
# 创建新的 screen 会话
screen -S face_api

# 在 screen 中启动服务
cd /home/face/face_recognition
conda activate face_mobile_recognition
python start_server.py

# 按 Ctrl+A 然后按 D 退出 screen（服务继续运行）

# 重新连接到 screen
screen -r face_api

# 查看所有 screen 会话
screen -ls

# 停止服务：重新连接后按 Ctrl+C
```

### 方式三：使用 systemd（最推荐）
创建服务文件 `/etc/systemd/system/face-api.service`:

```bash
sudo nano /etc/systemd/system/face-api.service
```

内容如下：
```ini
[Unit]
Description=Face recognition API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/face/face_recognition
Environment="PATH=/root/miniconda3/envs/face_mobile_recognition/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/root/miniconda3/envs/face_mobile_recognition/bin/python start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start face-api

# 设置开机自启
sudo systemctl enable face-api

# 查看状态
sudo systemctl status face-api

# 查看日志
sudo journalctl -u face-api -f

# 停止服务
sudo systemctl stop face-api

# 重启服务
sudo systemctl restart face-api
```

## 验证服务

### 1. 检查服务是否启动
```bash
# 检查端口
netstat -tlnp | grep 5000
# 或
ss -tlnp | grep 5000

# 检查进程
ps aux | grep start_server
```

### 2. 测试健康检查接口
```bash
curl http://localhost:5000/health
```

期望输出：
```json
{"status":"healthy","service":"face-recognition-api"}
```

### 3. 测试 API 文档
```bash
# 在浏览器访问（需要替换为服务器IP）
http://服务器IP:5000/docs
```

## 防火墙配置

### Ubuntu UFW
```bash
# 允许 5000 端口
sudo ufw allow 5000

# 查看状态
sudo ufw status
```

### CentOS/RHEL Firewalld
```bash
# 允许 5000 端口
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-ports
```

## 配置外网访问

### 1. 确认配置文件
检查 `config/config.yaml`:
```yaml
server:
  host: "0.0.0.0"  # 允许外网访问
  port: 5000
```

### 2. 使用 Nginx 反向代理（推荐）

安装 Nginx:
```bash
sudo apt update
sudo apt install nginx
```

创建配置文件 `/etc/nginx/sites-available/face-api`:
```nginx
server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/face-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 性能优化

### 1. 多实例部署（负载均衡）
```bash
# 启动多个实例（不同端口）
# 实例1
python start_server.py &  # 端口 5000

# 修改配置文件端口为 5001
# 实例2
python start_server.py &  # 端口 5001

# 修改配置文件端口为 5002
# 实例3
python start_server.py &  # 端口 5002
```

Nginx 负载均衡配置：
```nginx
upstream face_api {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name 你的域名或IP;

    location / {
        proxy_pass http://face_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 系统资源限制
```bash
# 查看系统资源
free -h  # 内存
df -h    # 磁盘
top      # CPU 和进程
```

## 日志管理

### 查看应用日志
```bash
# 实时查看
tail -f log/face_recognition.log

# 查看最后 100 行
tail -n 100 log/face_recognition.log

# 搜索错误
grep ERROR log/face_recognition.log
```

### 日志轮转（防止日志文件过大）
应用已内置日志轮转（10MB 自动切割，保留 5 个备份）

## 常见问题

### Q1: 端口被占用
```bash
# 查看占用端口的进程
sudo lsof -i :5000

# 杀死进程
sudo kill -9 <PID>
```

### Q2: 权限问题
```bash
# 给予执行权限
chmod +x start_server.py
chmod +x start_server.sh
```

### Q3: 模型文件路径
Linux 模型路径：`/root/.insightface/models/`

检查模型是否存在：
```bash
ls -la /root/.insightface/models/buffalo_l/
```

### Q4: 依赖安装失败
```bash
# 更新 pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple <包名>
```

## 监控和维护

### 1. 服务监控脚本
创建 `monitor.sh`:
```bash
#!/bin/bash
while true; do
    if ! curl -s http://localhost:5000/health > /dev/null; then
        echo "$(date): Service is down, restarting..."
        systemctl restart face-api
    fi
    sleep 60
done
```

### 2. 性能监控
```bash
# 安装 htop
sudo apt install htop

# 实时监控
htop

# 查看网络连接
netstat -an | grep 5000
```

## 测试脚本

### 快速测试
```bash
# 健康检查
curl http://localhost:5000/health

# 查看 API 文档（返回 HTML）
curl http://localhost:5000/docs

# 测试特征提取（需要准备测试图片）
curl -X POST http://localhost:5000/api/face/extract \
  -F "image_type=file" \
  -F "image=@test_face.jpg"
```

## 安全建议

### 1. 添加 API 认证（后续优化）
### 2. 使用 HTTPS（Nginx + Let's Encrypt）
```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d 你的域名
```

### 3. 限制访问 IP（可选）
在 Nginx 配置中：
```nginx
location / {
    allow 192.168.1.0/24;  # 允许内网
    deny all;               # 拒绝其他
    proxy_pass http://127.0.0.1:5000;
}
```

## 备份和恢复

### 备份
```bash
# 备份整个项目
tar -czf face_recognition_backup_$(date +%Y%m%d).tar.gz /home/face/face_recognition

# 备份配置和日志
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/ log/
```

### 恢复
```bash
tar -xzf face_recognition_backup_20260112.tar.gz -C /home/face/
```

---

## 快速启动命令总结

```bash
# 1. 进入项目目录
cd /home/face/face_recognition

# 2. 激活环境
conda activate face_mobile_recognition

# 3. 安装依赖（首次部署）
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 4. 前台启动（测试）
python start_server.py

# 5. 后台启动（生产）
nohup python start_server.py > server.log 2>&1 &

# 6. 验证
curl http://localhost:5000/health
```

**祝部署顺利！** 🚀
