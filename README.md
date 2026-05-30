# Claude AutoDev - 全自动化开发部署技能

## 简介

Claude AutoDev 是一个让Claude能够自主完成项目开发、测试、修复、部署全流程的技能。

用户只需要提供需求和权限，其他所有操作由AI自动完成。

## 核心特性

- 🤖 **自主开发** - 接收需求后自动开始开发
- 🧪 **自动测试** - 自己测试每个功能
- 🔧 **自动修复** - 发现问题自动解决
- 🚀 **自动部署** - 测试通过后自动部署
- ✅ **交付完整** - 确认可运营后才交付
- 🌐 **WebFetch** - 自动搜索解决方案、获取文档
- 🐳 **Docker沙箱** - 安全执行代码、隔离测试环境

## 使用方式

### 方式1：直接调用
```
/claude-autodev
```

### 方式2：自然语言
```
帮我自动开发一个音乐网站
用自动化模式部署这个项目
```

## 工作流程

1. **需求沟通** - 了解用户想要什么
2. **方案规划** - 制定技术方案
3. **权限申请** - 获取执行权限
4. **环境安装** - 自动安装环境
5. **项目开发** - 自动完成开发
6. **自动测试** - 测试每个功能
7. **问题修复** - 自动修复问题
8. **部署交付** - 部署并交付

## 核心原则

### 用户只需要
1. 提供需求和信息
2. 批准方案和权限

### AI完成
- 需求分析
- 功能规划
- 环境安装
- 项目开发
- 测试验证
- 问题修复
- 部署交付

### 绝对不能
- ❌ 让用户手动执行命令
- ❌ 让用户复制粘贴代码
- ❌ 交付半成品

## 支持的项目类型

- ✅ Web网站（PHP/Node.js/Python）
- ✅ API服务
- ✅ 静态网站
- ✅ 移动应用（需要额外配置）

## 示例

### 示例1：音乐网站
```
用户：帮我做一个音乐网站

AI：
1. 了解需求（搜索、播放、下载）
2. 列出功能清单
3. 询问直接搭建还是提供灵感
4. 用户选择后开始开发
5. 自动测试所有功能
6. 自动修复问题
7. 部署到服务器
8. 交付访问地址
```

### 示例2：API服务
```
用户：帮我做一个天气API

AI：
1. 了解需求（查询天气、支持城市）
2. 制定技术方案
3. 申请服务器权限
4. 自动安装Node.js
5. 开发API服务
6. 测试所有接口
7. 部署并交付
```

## 技术实现

### 服务器连接
使用 Python paramiko 库连接服务器执行命令

### 环境安装
自动检测并安装所需的运行环境

### 测试验证
使用 curl 和 Python 自动测试所有功能

### 问题修复
基于知识库和网上资源自动排查问题

### WebFetch - 网页获取能力
```python
import urllib.request

def web_fetch(url):
    """获取网页内容，用于搜索解决方案"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read().decode('utf-8')
```

**使用场景：**
- 搜索GitHub开源项目
- 获取API文档
- 查找问题解决方案
- 研究成熟项目的实现

### Docker 沙箱模式
```python
def docker_sandbox(ssh, command, image="node:18-alpine"):
    """在Docker容器中安全执行代码"""
    docker_cmd = f"docker run --rm {image} sh -c '{command}'"
    stdin, stdout, stderr = ssh.exec_command(docker_cmd)
    return stdout.read().decode()
```

**使用场景：**
- 安全测试代码
- 隔离环境执行
- 测试不同版本运行环境
- 避免污染服务器

**支持的Docker镜像：**
| 项目类型 | 镜像 |
|----------|------|
| Node.js | node:18-alpine |
| Python | python:3-alpine |
| PHP | php:8.2-cli-alpine |
| 静态网站 | nginx:alpine |

## 注意事项

1. **权限申请** - 没有权限时向用户申请
2. **测试全面** - 每个功能都要测试
3. **修复彻底** - 修bug要考虑全面
4. **交付完整** - 确认可运营后才交付

## 核心模块

### lib/ 目录结构

```
lib/
├── __init__.py    # 模块导出
├── sandbox.py     # 安全沙箱
├── resume.py      # 断点续传
├── retry.py       # 重试机制
├── audit.py       # 审计日志
└── executor.py    # 核心执行器
```

### 快速使用

```python
from lib.executor import TaskExecutor

# 创建执行器
executor = TaskExecutor(max_retries=3)

# 连接服务器
executor.connect("186.241.74.16", username="root", password="xxx")

# 开始任务
executor.start_task("my-task", "任务描述")

# 执行命令（自动重试、记录日志）
result = executor.execute("npm install")

# 完成任务
executor.complete_task()
```

## 更新日志

- v1.2.0 (2026-05-30) - 安全与可靠性
  - 添加Docker安全沙箱，代码执行隔离
  - 添加断点续传，支持任务暂停/恢复/回滚
  - 添加重试机制，避免无限循环
  - 添加审计日志，完整记录所有操作
  - 添加诊断报告，失败时提供解决方案

- v1.1.0 (2026-05-30) - 功能增强
  - 添加WebFetch能力，可搜索GitHub、获取文档
  - 添加Docker沙箱模式，安全执行代码
  - 优化工作流程

- v1.0.0 (2026-05-30) - 初始版本
  - 完整的自动化工作流程
  - 支持Web项目开发
  - 支持自动测试修复
  - 支持自动部署
