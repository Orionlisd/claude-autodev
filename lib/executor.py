"""
核心执行器
整合沙箱、重试、审计、断点续传功能
"""

import paramiko
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .sandbox import DockerSandbox, ExecutionMode
from .resume import ResumeManager, TaskStatus
from .retry import RetryManager, RetryConfig, MaxRetriesExceeded
from .audit import AuditLogger


class TaskExecutor:
    """任务执行器"""

    def __init__(self, ssh: paramiko.SSHClient = None,
                 sandbox_mode: str = ExecutionMode.BALANCED,
                 max_retries: int = 3,
                 timeout: int = 300,
                 log_dir: str = ".claude-autodev/logs"):
        """
        初始化执行器

        Args:
            ssh: SSH连接
            sandbox_mode: 沙箱模式
            max_retries: 最大重试次数
            timeout: 超时时间
            log_dir: 日志目录
        """
        self.ssh = ssh

        # 初始化各模块
        self.sandbox = DockerSandbox(ssh, sandbox_mode) if ssh else None
        self.retry_manager = RetryManager(RetryConfig(
            max_retries=max_retries,
            timeout=timeout
        ))
        self.resume_manager = ResumeManager()
        self.audit_logger = AuditLogger(log_dir)

        # 当前任务状态
        self.current_task_id = None

    def connect(self, server: str, username: str = "root",
                password: str = None, key_filename: str = None):
        """建立SSH连接"""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {"hostname": server, "username": username}
        if password:
            connect_kwargs["password"] = password
        if key_filename:
            connect_kwargs["key_filename"] = key_filename

        self.ssh.connect(**connect_kwargs)
        self.sandbox = DockerSandbox(self.ssh)
        return self

    def start_task(self, task_id: str, description: str = "",
                   metadata: Dict = None) -> str:
        """
        开始新任务

        Args:
            task_id: 任务ID
            description: 任务描述
            metadata: 元数据

        Returns:
            任务ID
        """
        self.current_task_id = task_id

        # 创建任务状态
        self.resume_manager.create_task(task_id, description)

        # 开始审计日志
        self.audit_logger.start_execution(task_id, metadata)

        return task_id

    def execute(self, command: str, operation_type: str = "code_execute",
                image: str = None, checkpoint: bool = True) -> Dict[str, Any]:
        """
        执行命令

        Args:
            command: 要执行的命令
            operation_type: 操作类型
            image: Docker镜像
            checkpoint: 是否保存检查点

        Returns:
            执行结果
        """
        if not self.ssh:
            raise RuntimeError("未建立SSH连接")

        # 记录开始时间
        start_time = datetime.now()

        try:
            # 使用重试机制执行
            result = self.retry_manager.execute_with_retry(
                lambda: self.sandbox.execute(command, operation_type, image),
                command
            )

            # 计算耗时
            duration = (datetime.now() - start_time).total_seconds()

            # 记录审计日志
            stdout, stderr, exit_code = result
            self.audit_logger.log_command(
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration=duration
            )

            # 保存检查点
            if checkpoint and self.current_task_id:
                self.resume_manager.save_checkpoint(
                    phase=operation_type,
                    step=command[:50],
                    data={"command": command, "exit_code": exit_code}
                )

            return {
                "success": exit_code == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code,
                "duration": duration
            }

        except MaxRetriesExceeded as e:
            # 超过重试次数
            self.audit_logger.log_command(
                command=command,
                exit_code=-1,
                stderr=str(e),
                duration=(datetime.now() - start_time).total_seconds()
            )

            # 标记任务失败
            if self.current_task_id:
                self.resume_manager.fail_task(str(e))

            return {
                "success": False,
                "error": str(e),
                "report": e.report.format_markdown(),
                "exit_code": -1
            }

    def execute_with_rollback(self, command: str, rollback_command: str,
                             operation_type: str = "code_execute") -> Dict[str, Any]:
        """
        执行命令，失败时自动回滚

        Args:
            command: 要执行的命令
            rollback_command: 回滚命令
            operation_type: 操作类型

        Returns:
            执行结果
        """
        result = self.execute(command, operation_type, checkpoint=False)

        if not result["success"]:
            # 执行回滚
            rollback_result = self.execute(rollback_command, "rollback", checkpoint=False)
            result["rolled_back"] = rollback_result["success"]
            result["rollback_result"] = rollback_result

        return result

    def save_checkpoint(self, phase: str, step: str, data: Dict = None):
        """手动保存检查点"""
        if self.current_task_id:
            self.resume_manager.save_checkpoint(phase, step, data)

    def pause_task(self):
        """暂停任务"""
        if self.current_task_id:
            self.resume_manager.pause_task()
            self.audit_logger.end_execution("paused")

    def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        task = self.resume_manager.resume_task(task_id)
        if task:
            self.current_task_id = task_id
            self.audit_logger.start_execution(task_id)
            return True
        return False

    def complete_task(self):
        """完成任务"""
        if self.current_task_id:
            self.resume_manager.complete_task()
            self.audit_logger.end_execution("completed")

    def fail_task(self, error: str):
        """标记任务失败"""
        if self.current_task_id:
            self.resume_manager.fail_task(error)
            self.audit_logger.end_execution("failed")

    def get_task_status(self) -> Dict:
        """获取任务状态"""
        if not self.current_task_id:
            return {"status": "no_task"}

        task = self.resume_manager.get_task(self.current_task_id)
        if not task:
            return {"status": "not_found"}

        return {
            "task_id": task.task_id,
            "status": task.status,
            "checkpoints": len(task.checkpoints),
            "last_checkpoint": task.get_current_phase(),
            "error": task.error
        }

    def generate_rollback_script(self) -> str:
        """生成回滚脚本"""
        return self.audit_logger.generate_rollback_script()

    def save_rollback_script(self, path: str = None) -> str:
        """保存回滚脚本"""
        return self.audit_logger.save_rollback_script(path)

    def generate_report(self) -> str:
        """生成执行报告"""
        return self.audit_logger.generate_report()

    def list_tasks(self) -> list:
        """列出所有任务"""
        return self.resume_manager.list_tasks()

    def list_logs(self) -> list:
        """列出所有日志"""
        return self.audit_logger.list_logs()

    def close(self):
        """关闭连接"""
        if self.ssh:
            self.ssh.close()
            self.ssh = None


class QuickExecutor:
    """快速执行器（简化接口）"""

    @staticmethod
    def run(server: str, command: str, username: str = "root",
            password: str = None, key_filename: str = None) -> Dict:
        """
        快速执行单个命令

        Args:
            server: 服务器地址
            command: 要执行的命令
            username: 用户名
            password: 密码
            key_filename: 密钥文件路径

        Returns:
            执行结果
        """
        executor = TaskExecutor()
        try:
            executor.connect(server, username, password, key_filename)
            executor.start_task("quick-task", f"Quick execute: {command[:50]}")
            result = executor.execute(command)
            executor.complete_task()
            return result
        finally:
            executor.close()

    @staticmethod
    def deploy(server: str, local_path: str, remote_path: str,
               username: str = "root", password: str = None,
               key_filename: str = None) -> Dict:
        """
        快速部署文件

        Args:
            server: 服务器地址
            local_path: 本地路径
            remote_path: 远程路径
            username: 用户名
            password: 密码
            key_filename: 密钥文件路径

        Returns:
            部署结果
        """
        executor = TaskExecutor()
        try:
            executor.connect(server, username, password, key_filename)
            executor.start_task("quick-deploy", f"Deploy {local_path} to {remote_path}")

            # 上传文件
            sftp = executor.ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()

            executor.audit_logger.log_command(
                command=f"scp {local_path} {remote_path}",
                exit_code=0,
                stdout="File uploaded successfully"
            )

            executor.complete_task()
            return {"success": True, "message": "部署成功"}
        except Exception as e:
            executor.fail_task(str(e))
            return {"success": False, "error": str(e)}
        finally:
            executor.close()
