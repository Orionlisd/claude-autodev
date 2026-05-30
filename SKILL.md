---
name: claude-autodev
description: >
  全自动化开发部署技能。让Claude能够自主完成项目开发、测试、修复、部署全流程。
  用户只需要提供需求和权限，其他所有操作由AI自动完成。
  支持Web应用、API服务、移动端等各类项目。
priority: high
auto_trigger: true
trigger_keywords:
  - 开发
  - 部署
  - 搭建
  - 做一个
  - 创建
  - 编写
  - 代码
  - 项目
  - 网站
  - 应用
  - APP
  - API
  - 服务
  - 程序
---

# Claude AutoDev - 全自动化开发部署

## 核心原则

**用户只需要做两件事：**
1. 提供需求和信息
2. 批准方案和权限

**其他所有事情都由AI完成：**
- 需求分析
- 功能规划
- 环境安装
- 项目开发
- 测试验证
- 问题修复
- 部署交付

**绝对不能出现：**
- ❌ "请在服务器执行这个命令"
- ❌ "请手动安装这个"
- ❌ "请复制这个到终端"
- ✅ 向用户申请权限，用户批准后自动执行

---

## 完整工作流程

### 阶段1：需求沟通

**目标：** 理解用户想要什么

**执行步骤：**
1. 了解用户的核心需求
2. 列出3-5个主要功能（不要太多）
3. 给用户选择：
   > "我们现在直接开始搭建，还是我来为你提供更多灵感？"

**如果用户选择"直接搭建"：** 进入阶段2
**如果用户选择"提供更多灵感"：**
- 搜索GitHub成熟项目
- 参考市面成熟产品
- 整理功能清单
- 让用户选择
- 然后进入阶段2

### 阶段2：方案规划

**目标：** 制定完整的技术方案

**执行步骤：**
1. 确定技术栈（PHP/Node.js/Python等）
2. 确定需要的环境和工具
3. 确定部署方式
4. 输出完整方案给用户

**方案格式：**
```
## 实现方案

### 需求理解
[用户的核心需求]

### 技术方案
- 技术栈：xxx
- 主要功能：xxx

### 环境需求
- 服务器环境：xxx
- 需要安装：xxx
- 需要配置：xxx

### 预期效果
- 访问地址：xxx
- 功能：xxx

---
这个方案可以吗？确认后我将自动完成所有步骤。
```

### 阶段3：权限申请

**目标：** 获取执行所需的权限

**执行步骤：**
1. 列出需要的权限（SSH、服务器密码等）
2. 说明每个权限的用途
3. 向用户申请

**权限申请格式：**
```
为了完成自动化部署，我需要以下权限：

1. 服务器SSH连接
   - 用途：上传文件、执行命令、配置环境
   - 需要：IP地址、用户名、密码

2. 域名配置
   - 用途：配置网站访问
   - 需要：域名已解析到服务器

请提供以上信息，我将自动完成所有操作。
```

### 阶段4：环境安装

**目标：** 自动安装所需的运行环境

**执行步骤：**
1. 检查服务器现有环境
2. 缺少的环境自动安装
3. 配置服务器（Nginx、PM2等）

**自动化执行：**
```python
# 使用paramiko连接服务器
import paramiko
ssh = paramiko.SSHClient()
ssh.connect(server, username=user, password=password)

# 检查环境
stdin, stdout, stderr = ssh.exec_command("node -v")
if "not found" in stdout.read():
    # 自动安装Node.js
    ssh.exec_command("curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -")
    ssh.exec_command("yum install -y nodejs")
```

### 阶段5：项目开发

**目标：** 自动完成项目开发

**执行步骤：**
1. 创建项目结构
2. 编写代码
3. 安装依赖

**关键点：**
- 代码要完整，不要半成品
- 每个功能都要实现
- 配置要正确

### 阶段6：自动测试

**目标：** 自己测试每个功能

**执行步骤：**
1. 启动项目
2. 测试每个功能
3. 记录测试结果

**测试清单：**
- [ ] 页面能否正常访问
- [ ] 每个按钮能否点击
- [ ] 每个接口能否调用
- [ ] 边界情况是否处理

**测试代码示例：**
```python
# 测试首页
stdin, stdout, stderr = ssh.exec_command("curl -s -o /dev/null -w '%{http_code}' http://example.com")
status = stdout.read().decode()
if status != "200":
    # 自动修复

# 测试API
stdin, stdout, stderr = ssh.exec_command("curl -s 'http://example.com/api/test'")
result = stdout.read().decode()
if "error" in result:
    # 自动修复
```

### 阶段7：问题修复

**目标：** 自动修复发现的问题

**执行步骤：**
1. 分析错误原因
2. 修改代码
3. 重新测试
4. 确认修复成功

**修复原则：**
- 不要只修表面，要考虑全面
- 修复后要重新测试所有功能
- 利用知识库排查问题

**修复流程：**
```
发现问题 → 分析原因 → 修改代码 → 重新测试 → 确认修复
     ↑                                        ↓
     └────────── 如果还有问题 ←──────────────┘
```

### 阶段8：部署交付

**目标：** 部署项目并交付给用户

**执行步骤：**
1. 最终测试确认
2. 部署到服务器
3. 配置域名
4. 验证访问
5. 交付给用户

**交付格式：**
```
## ✅ 项目已完成

### 访问地址
- 前台：http://xxx.com
- 后台：http://xxx.com/admin（如有）

### 功能说明
- 功能1：xxx
- 功能2：xxx

### 使用说明
- xxx

---
项目已部署完成，所有功能已测试通过！
```

---

## 关键技能

### 1. WebFetch - 网页获取能力

**用途：** 搜索解决方案、获取文档、研究开源项目

**实现方式：** 使用Python urllib库

```python
import urllib.request
import json

def web_fetch(url, timeout=10):
    """获取网页内容"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode('utf-8')

def web_fetch_json(url, timeout=10):
    """获取JSON API数据"""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))

def search_github(query, limit=5):
    """搜索GitHub项目"""
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page={limit}"
    result = web_fetch_json(url)
    return result.get('items', [])
```

**使用场景：**
- 遇到问题时搜索GitHub解决方案
- 获取开源项目的文档
- 研究成熟项目的实现方式
- 查找可用的API接口

---

### 2. Docker 沙箱模式

**用途：** 安全执行代码、测试项目、隔离环境

**实现方式：** 使用paramiko在服务器上执行Docker命令

```python
import paramiko

def docker_sandbox(ssh, command, image="node:18-alpine"):
    """在Docker沙箱中执行命令"""
    docker_cmd = f"docker run --rm {image} sh -c '{command}'"
    stdin, stdout, stderr = ssh.exec_command(docker_cmd)
    return stdout.read().decode(), stderr.read().decode()

def docker_sandbox_with_volume(ssh, command, host_path, container_path="/app", image="node:18-alpine"):
    """带文件挂载的Docker沙箱"""
    docker_cmd = f"docker run --rm -v {host_path}:{container_path} -w {container_path} {image} sh -c '{command}'"
    stdin, stdout, stderr = ssh.exec_command(docker_cmd)
    return stdout.read().decode(), stderr.read().decode()

def docker_test_nodejs(ssh, code):
    """在Docker中测试Node.js代码"""
    return docker_sandbox(ssh, f"node -e '{code}'", "node:18-alpine")

def docker_test_python(ssh, code):
    """在Docker中测试Python代码"""
    return docker_sandbox(ssh, f"python3 -c '{code}'", "python:3-alpine")
```

**使用场景：**
- 测试代码是否能正常运行
- 隔离环境避免污染服务器
- 安全执行用户提供的代码
- 测试不同版本的运行环境

**Docker镜像选择：**
| 项目类型 | 推荐镜像 |
|----------|----------|
| Node.js | node:18-alpine |
| Python | python:3-alpine |
| PHP | php:8.2-cli-alpine |
| 静态网站 | nginx:alpine |

---

### 4. 服务器连接
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(server_ip, username="root", password=password)

# 执行命令
stdin, stdout, stderr = ssh.exec_command("command")
result = stdout.read().decode()

# 上传文件
sftp = ssh.open_sftp()
sftp.put(local_path, remote_path)
sftp.close()
```

### 5. 环境检测
```python
def check_environment(ssh):
    """检查服务器环境"""
    env = {}
    
    # 检查Node.js
    stdin, stdout, stderr = ssh.exec_command("node -v")
    env['node'] = stdout.read().decode().strip()
    
    # 检查PHP
    stdin, stdout, stderr = ssh.exec_command("php -v")
    env['php'] = stdout.read().decode().strip()
    
    # 检查Nginx
    stdin, stdout, stderr = ssh.exec_command("nginx -v")
    env['nginx'] = stderr.read().decode().strip()
    
    return env
```

### 6. 自动安装
```python
def install_environment(ssh, env_type):
    """自动安装环境"""
    if env_type == "node":
        ssh.exec_command("curl -fsSL https://rpm.nodesource.com/setup_18.x | bash -")
        ssh.exec_command("yum install -y nodejs")
    elif env_type == "php":
        ssh.exec_command("yum install -y php php-fpm")
    elif env_type == "nginx":
        ssh.exec_command("yum install -y nginx")
```

### 7. 测试验证
```python
def test_website(url, expected_status=200):
    """测试网站是否正常"""
    import urllib.request
    try:
        response = urllib.request.urlopen(url)
        return response.status == expected_status
    except:
        return False
```

---

## 常见问题处理

### 1. 端口被占用
```python
# 查找占用端口的进程
stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep :3000")
# 杀死进程
ssh.exec_command("kill -9 <pid>")
```

### 2. 权限问题
```python
# 修改文件权限
ssh.exec_command("chown -R www:www /www/wwwroot/site.com")
ssh.exec_command("chmod -R 755 /www/wwwroot/site.com")
```

### 3. Nginx配置
```python
# 创建Nginx配置
config = """
server {
    listen 80;
    server_name domain.com;
    root /www/wwwroot/domain.com;
    index index.php index.html;
    
    location ~ \\.php$ {
        fastcgi_pass unix:/tmp/php-cgi.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
"""
sftp = ssh.open_sftp()
with sftp.open(f'/www/server/panel/vhost/nginx/{domain}.conf', 'w') as f:
    f.write(config)
sftp.close()
ssh.exec_command("nginx -s reload")
```

---

## 使用方式

### 方式1：用户调用
用户可以说：
- "帮我自动开发一个xxx"
- "用claude-autodev模式开发"
- "/claude-autodev"

### 方式2：自动触发
当用户需要：
- 完整的项目开发
- 自动化部署
- 全流程自动化

---

## 注意事项

1. **权限申请** - 没有权限时向用户申请，不要让用户手动执行
2. **测试全面** - 每个功能都要测试，不能遗漏
3. **修复彻底** - 修bug要考虑全面，不能修了又冒出来
4. **交付完整** - 确认可运营后才交付，不要给半成品

---

## v1.2.0 新增功能

### 1. 安全沙箱（Docker）

所有用户代码执行都在Docker容器中进行，确保安全隔离。

```python
from lib.sandbox import DockerSandbox, ExecutionMode

# 创建沙箱
sandbox = DockerSandbox(ssh, ExecutionMode.BALANCED)

# 在沙箱中执行代码
stdout, stderr, exit_code = sandbox.execute_node("console.log('Hello')")

# 带文件挂载执行
stdout, stderr, exit_code = sandbox.execute_with_volume(
    "npm test", "/path/to/project", "/app"
)
```

**执行模式：**
- `STRICT` - 强制Docker，最安全
- `BALANCED` - 关键操作Docker，普通操作直接执行（默认）
- `DIRECT` - 直接执行，最快但不安全

### 2. 断点续传（Resume）

支持任务暂停、恢复、回滚到任意检查点。

```python
from lib.resume import ResumeManager

# 创建任务
manager = ResumeManager()
task = manager.create_task("music-website", "开发音乐网站")

# 保存检查点
manager.save_checkpoint("development", "创建项目结构")
manager.save_checkpoint("development", "编写API代码")

# 暂停任务
manager.pause_task()

# 恢复任务
task = manager.resume_task("music-website")

# 回滚到上一个检查点
manager.rollback_last_checkpoint()
```

### 3. 重试机制（Retry）

固定重试次数，超出后生成诊断报告，避免无限循环。

```python
from lib.retry import RetryManager, RetryConfig, MaxRetriesExceeded

# 配置重试
config = RetryConfig(max_retries=3, timeout=300)
manager = RetryManager(config)

try:
    # 执行可能失败的操作
    result = manager.execute_with_retry(
        lambda: ssh.exec_command("npm install"),
        "安装依赖"
    )
except MaxRetriesExceeded as e:
    # 生成诊断报告
    print(e.report.format_markdown())
```

**诊断报告示例：**
```
## ❌ 执行失败 - 诊断报告

### 错误信息
- 重试次数：3/3
- 最后错误：npm ERR! code E404

### 建议解决方案
1. 检查包名是否正确
2. 检查npm registry配置
3. 检查网络连接

### 请选择操作
- 继续执行: 提供更多指导后继续
- 回滚: 回滚到上一个检查点
- 终止: 终止当前任务
```

### 4. 审计日志（Audit）

详细记录所有执行操作，支持回滚。

```python
from lib.audit import AuditLogger

# 创建日志
logger = AuditLogger()
logger.start_execution("deploy-001", {"server": "186.241.74.16"})

# 记录命令
logger.log_command("mkdir -p /www/site", exit_code=0, duration=0.1)
logger.log_command("scp site.tar.gz root@server:/tmp/", exit_code=0, duration=2.5)

# 结束执行
logger.end_execution("completed")

# 生成回滚脚本
logger.save_rollback_script("rollback.sh")

# 生成报告
print(logger.generate_report())
```

**日志格式（JSON）：**
```json
{
    "execution_id": "exec-20260530-001",
    "start_time": "2026-05-30T10:00:00",
    "commands": [
        {
            "seq": 1,
            "command": "mkdir -p /www/site",
            "exit_code": 0,
            "duration": 0.1,
            "reversible": true,
            "rollback_cmd": "rmdir /www/site"
        }
    ],
    "rollback_script": ["rmdir /www/site"]
}
```

### 5. 核心执行器（Executor）

整合所有功能的统一接口。

```python
from lib.executor import TaskExecutor

# 创建执行器
executor = TaskExecutor(
    sandbox_mode="balanced",
    max_retries=3,
    timeout=300
)

# 连接服务器
executor.connect("186.241.74.16", username="root", password="xxx")

# 开始任务
executor.start_task("music-website", "开发音乐网站")

# 执行命令（自动重试、记录日志、支持回滚）
result = executor.execute("npm install", "dependency_install")

# 执行并自动回滚
result = executor.execute_with_rollback(
    "npm run build",
    "rm -rf dist",
    "build"
)

# 完成任务
executor.complete_task()

# 生成报告
print(executor.generate_report())

# 保存回滚脚本
executor.save_rollback_script()
```

---

## 文件结构

```
claude-autodev/
├── SKILL.md           # 技能文档
├── README.md          # 使用说明
└── lib/               # 核心库
    ├── __init__.py    # 模块导出
    ├── sandbox.py     # 安全沙箱
    ├── resume.py      # 断点续传
    ├── retry.py       # 重试机制
    ├── audit.py       # 审计日志
    └── executor.py    # 核心执行器
```
