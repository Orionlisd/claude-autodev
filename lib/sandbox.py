"""
Docker安全沙箱模块
提供代码安全执行环境
"""

import paramiko
import json
from typing import Optional, Tuple

class ExecutionMode:
    """执行模式"""
    STRICT = "strict"      # 强制Docker，最安全
    BALANCED = "balanced"  # 关键操作Docker，普通操作直接执行
    DIRECT = "direct"      # 直接执行，最快但不安全

class DockerSandbox:
    """Docker沙箱管理器"""

    # 默认镜像配置
    DEFAULT_IMAGES = {
        "node": "node:18-alpine",
        "python": "python:3-alpine",
        "php": "php:8.2-cli-alpine",
        "static": "nginx:alpine",
        "default": "alpine:latest"
    }

    # 需要Docker的操作类型
    SANDBOX_REQUIRED = [
        "code_execute",    # 执行用户代码
        "test_run",        # 运行测试
        "npm_install",     # 安装npm依赖
        "pip_install",     # 安装pip依赖
        "code_compile"     # 编译代码
    ]

    # 可直接执行的操作类型
    DIRECT_ALLOWED = [
        "nginx_config",    # Nginx配置
        "pm2_manage",      # PM2管理
        "file_upload",     # 文件上传
        "dir_create",      # 创建目录
        "permission_set",  # 设置权限
        "service_restart"  # 重启服务
    ]

    def __init__(self, ssh: paramiko.SSHClient, mode: str = ExecutionMode.BALANCED):
        """
        初始化沙箱

        Args:
            ssh: SSH连接
            mode: 执行模式
        """
        self.ssh = ssh
        self.mode = mode
        self.docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """检查Docker是否可用"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command("docker --version")
            return "Docker version" in stdout.read().decode()
        except:
            return False

    def execute(self, command: str, operation_type: str = "code_execute",
                image: str = None, timeout: int = 300) -> Tuple[str, str, int]:
        """
        执行命令

        Args:
            command: 要执行的命令
            operation_type: 操作类型
            image: Docker镜像（可选）
            timeout: 超时时间（秒）

        Returns:
            (stdout, stderr, exit_code)
        """
        # 判断是否需要沙箱
        use_sandbox = self._should_use_sandbox(operation_type)

        if use_sandbox and self.docker_available:
            return self._execute_in_sandbox(command, image, timeout)
        else:
            return self._execute_direct(command, timeout)

    def _should_use_sandbox(self, operation_type: str) -> bool:
        """判断是否应该使用沙箱"""
        if self.mode == ExecutionMode.STRICT:
            return True
        elif self.mode == ExecutionMode.DIRECT:
            return False
        else:  # BALANCED
            return operation_type in self.SANDBOX_REQUIRED

    def _execute_in_sandbox(self, command: str, image: str = None,
                           timeout: int = 300) -> Tuple[str, str, int]:
        """在Docker沙箱中执行"""
        if not image:
            image = self.DEFAULT_IMAGES["default"]

        # 构建Docker命令
        docker_cmd = f"docker run --rm --network=none {image} sh -c '{command}'"

        stdin, stdout, stderr = self.ssh.exec_command(docker_cmd, timeout=timeout)

        exit_code = stdout.channel.recv_exit_status()
        return stdout.read().decode(), stderr.read().decode(), exit_code

    def _execute_direct(self, command: str, timeout: int = 300) -> Tuple[str, str, int]:
        """直接执行"""
        stdin, stdout, stderr = self.ssh.exec_command(command, timeout=timeout)

        exit_code = stdout.channel.recv_exit_status()
        return stdout.read().decode(), stderr.read().decode(), exit_code

    def execute_node(self, code: str, timeout: int = 60) -> Tuple[str, str, int]:
        """执行Node.js代码"""
        escaped_code = code.replace("'", "\\'")
        return self._execute_in_sandbox(
            f"node -e '{escaped_code}'",
            self.DEFAULT_IMAGES["node"],
            timeout
        )

    def execute_python(self, code: str, timeout: int = 60) -> Tuple[str, str, int]:
        """执行Python代码"""
        escaped_code = code.replace("'", "\\'")
        return self._execute_in_sandbox(
            f"python3 -c '{escaped_code}'",
            self.DEFAULT_IMAGES["python"],
            timeout
        )

    def execute_with_volume(self, command: str, host_path: str,
                           container_path: str = "/app", image: str = None,
                           timeout: int = 300) -> Tuple[str, str, int]:
        """带文件挂载的执行"""
        if not image:
            image = self.DEFAULT_IMAGES["default"]

        docker_cmd = f"docker run --rm -v {host_path}:{container_path} -w {container_path} {image} sh -c '{command}'"

        stdin, stdout, stderr = self.ssh.exec_command(docker_cmd, timeout=timeout)

        exit_code = stdout.channel.recv_exit_status()
        return stdout.read().decode(), stderr.read().decode(), exit_code


class SandboxConfig:
    """沙箱配置"""

    def __init__(self):
        self.mode = ExecutionMode.BALANCED
        self.default_timeout = 300
        self.network_enabled = False
        self.custom_images = {}

    @classmethod
    def from_file(cls, config_path: str) -> 'SandboxConfig':
        """从配置文件加载"""
        config = cls()
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                config.mode = data.get('mode', ExecutionMode.BALANCED)
                config.default_timeout = data.get('timeout', 300)
                config.network_enabled = data.get('network', False)
                config.custom_images = data.get('images', {})
        except:
            pass
        return config

    def save(self, config_path: str):
        """保存配置到文件"""
        data = {
            'mode': self.mode,
            'timeout': self.default_timeout,
            'network': self.network_enabled,
            'images': self.custom_images
        }
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
