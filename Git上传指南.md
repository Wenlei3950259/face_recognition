# Git 上传指南

## 步骤 1: 初始化 Git 仓库

```bash
git init
```

## 步骤 2: 配置 Git 用户信息（如果还没配置）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

## 步骤 3: 添加所有文件到暂存区

```bash
git add .
```

## 步骤 4: 提交到本地仓库

```bash
git commit -m "重构: 将项目从医疗系统改为人脸识别系统

- 修改所有 Author 为 wen_l
- 将所有 medical 相关词汇改为 recognition
- 重命名 API 文件和日志文件
- 更新所有文档和配置文件
- 添加 .gitignore 文件"
```

## 步骤 5: 关联远程仓库

### 如果是新建的远程仓库：
```bash
git remote add origin https://github.com/你的用户名/你的仓库名.git
```

### 如果已有远程仓库，需要更换：
```bash
git remote set-url origin https://github.com/你的用户名/你的仓库名.git
```

### 查看远程仓库：
```bash
git remote -v
```

## 步骤 6: 推送到远程仓库

### 首次推送（设置上游分支）：
```bash
git branch -M main
git push -u origin main
```

### 后续推送：
```bash
git push
```

---

## 常用 Git 命令

### 查看状态
```bash
git status
```

### 查看提交历史
```bash
git log
git log --oneline
```

### 查看修改内容
```bash
git diff
```

### 添加特定文件
```bash
git add 文件名
```

### 撤销修改（未提交）
```bash
git checkout -- 文件名
```

### 撤销已添加到暂存区的文件
```bash
git reset HEAD 文件名
```

### 修改最后一次提交
```bash
git commit --amend
```

---

## 注意事项

### 1. 敏感信息
确保 `config/config.yaml` 中没有敏感信息（如数据库密码）。如果有，建议：
- 创建 `config/config.example.yaml` 作为模板
- 将 `config/config.yaml` 添加到 `.gitignore`

### 2. 大文件
模型文件（.insightface 目录）已在 `.gitignore` 中排除，不会上传。

### 3. 日志文件
日志文件已在 `.gitignore` 中排除。

### 4. IDE 配置
`.idea` 目录已排除，不会上传 IDE 配置。

---

## 如果遇到问题

### 问题 1: 推送被拒绝（远程有更新）
```bash
# 先拉取远程更新
git pull origin main --rebase

# 再推送
git push
```

### 问题 2: 需要强制推送（谨慎使用）
```bash
git push -f origin main
```

### 问题 3: 忘记添加 .gitignore 导致上传了不该上传的文件
```bash
# 从 Git 中删除但保留本地文件
git rm --cached 文件名

# 或删除整个目录
git rm -r --cached 目录名

# 提交删除
git commit -m "删除不需要的文件"
git push
```

---

## 推荐的提交信息格式

```
类型: 简短描述

详细描述（可选）
```

**类型示例：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**
```bash
git commit -m "feat: 添加人脸相似度批量计算接口"
git commit -m "fix: 修复图片解码失败的问题"
git commit -m "docs: 更新部署文档"
```

---

## 快速命令（复制使用）

```bash
# 完整流程
git init
git add .
git commit -m "重构: 将项目从医疗系统改为人脸识别系统"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

---

## 后续开发流程

```bash
# 1. 修改代码
# 2. 查看修改
git status
git diff

# 3. 添加修改
git add .

# 4. 提交
git commit -m "描述你的修改"

# 5. 推送
git push
```
