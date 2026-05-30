"""
Claude AutoDev 核心库
提供安全沙箱、断点续传、重试机制、审计日志功能
"""

from .sandbox import DockerSandbox, ExecutionMode, SandboxConfig
from .resume import ResumeManager, TaskState, TaskStatus
from .retry import RetryManager, RetryConfig, MaxRetriesExceeded, DiagnosticReport
from .audit import AuditLogger, ExecutionLog, CommandRecord

__version__ = "1.2.0"
__all__ = [
    "DockerSandbox",
    "ExecutionMode",
    "SandboxConfig",
    "ResumeManager",
    "TaskState",
    "TaskStatus",
    "RetryManager",
    "RetryConfig",
    "MaxRetriesExceeded",
    "DiagnosticReport",
    "AuditLogger",
    "ExecutionLog",
    "CommandRecord",
]
