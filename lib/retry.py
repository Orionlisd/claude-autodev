"""
重试机制模块
支持固定重试次数、超时控制、诊断报告
"""

import time
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3          # 最大重试次数
    timeout: int = 300            # 单步超时（秒）
    backoff_factor: float = 1.5   # 退避因子
    max_backoff: int = 60         # 最大退避时间（秒）

@dataclass
class ErrorRecord:
    """错误记录"""
    attempt: int
    timestamp: str
    error_type: str
    error_message: str
    command: str
    context: Dict

class DiagnosticReport:
    """诊断报告"""

    def __init__(self, task_name: str):
        self.task_name = task_name
        self.start_time = datetime.now()
        self.end_time = None
        self.status = "in_progress"
        self.error_history: List[ErrorRecord] = []
        self.suggestions: List[str] = []
        self.options: List[Dict] = []

    def add_error(self, attempt: int, error_type: str, error_message: str,
                  command: str = "", context: Dict = None):
        """添加错误记录"""
        record = ErrorRecord(
            attempt=attempt,
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            error_message=error_message,
            command=command,
            context=context or {}
        )
        self.error_history.append(record)

    def add_suggestion(self, suggestion: str):
        """添加建议"""
        self.suggestions.append(suggestion)

    def add_option(self, label: str, description: str, action: str):
        """添加选项"""
        self.options.append({
            "label": label,
            "description": description,
            "action": action
        })

    def generate(self) -> Dict:
        """生成报告"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        report = {
            "task": self.task_name,
            "status": "failed",
            "duration": f"{duration:.1f}秒",
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "retry_count": len(self.error_history),
            "error_history": [
                {
                    "attempt": e.attempt,
                    "timestamp": e.timestamp,
                    "error_type": e.error_type,
                    "error_message": e.error_message,
                    "command": e.command
                }
                for e in self.error_history
            ],
            "suggestions": self.suggestions,
            "options": self.options
        }

        return report

    def format_markdown(self) -> str:
        """格式化为Markdown"""
        report = self.generate()

        lines = [
            f"## ❌ 执行失败 - 诊断报告",
            f"",
            f"### 基本信息",
            f"- **任务**: {report['task']}",
            f"- **状态**: {report['status']}",
            f"- **耗时**: {report['duration']}",
            f"- **重试次数**: {report['retry_count']}",
            f"",
            f"### 错误历史",
        ]

        for i, error in enumerate(report['error_history'], 1):
            lines.extend([
                f"",
                f"**第{i}次尝试** ({error['timestamp']})",
                f"- 类型: `{error['error_type']}`",
                f"- 错误: {error['error_message']}",
            ])
            if error['command']:
                lines.append(f"- 命令: `{error['command']}`")

        if report['suggestions']:
            lines.extend([
                f"",
                f"### 建议解决方案",
            ])
            for i, suggestion in enumerate(report['suggestions'], 1):
                lines.append(f"{i}. {suggestion}")

        if report['options']:
            lines.extend([
                f"",
                f"### 请选择操作",
            ])
            for option in report['options']:
                lines.append(f"- **{option['label']}**: {option['description']}")

        return "\n".join(lines)


class RetryManager:
    """重试管理器"""

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.current_retry = 0
        self.report: Optional[DiagnosticReport] = None

    def execute_with_retry(self, func: Callable, task_name: str,
                          *args, **kwargs) -> Any:
        """
        执行函数，失败时重试

        Args:
            func: 要执行的函数
            task_name: 任务名称
            *args, **kwargs: 函数参数

        Returns:
            函数返回值

        Raises:
            MaxRetriesExceeded: 超过最大重试次数
        """
        self.report = DiagnosticReport(task_name)
        self.current_retry = 0

        while self.current_retry < self.config.max_retries:
            try:
                result = func(*args, **kwargs)

                # 检查结果是否成功
                if self._is_success(result):
                    return result
                else:
                    # 记录错误
                    error_msg = self._extract_error(result)
                    self.report.add_error(
                        attempt=self.current_retry + 1,
                        error_type="execution_failed",
                        error_message=error_msg,
                        context={"result": result}
                    )

            except TimeoutError as e:
                self.report.add_error(
                    attempt=self.current_retry + 1,
                    error_type="timeout",
                    error_message=str(e)
                )

            except Exception as e:
                self.report.add_error(
                    attempt=self.current_retry + 1,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )

            self.current_retry += 1

            # 退避等待
            if self.current_retry < self.config.max_retries:
                wait_time = min(
                    self.config.backoff_factor ** self.current_retry,
                    self.config.max_backoff
                )
                time.sleep(wait_time)

        # 超过最大重试次数
        self._generate_suggestions()
        raise MaxRetriesExceeded(self.report)

    def _is_success(self, result: Any) -> bool:
        """判断结果是否成功"""
        if isinstance(result, dict):
            return result.get("success", False) or result.get("exit_code", -1) == 0
        if isinstance(result, tuple) and len(result) == 3:
            _, _, exit_code = result
            return exit_code == 0
        return bool(result)

    def _extract_error(self, result: Any) -> str:
        """提取错误信息"""
        if isinstance(result, dict):
            return result.get("error", result.get("stderr", "Unknown error"))
        if isinstance(result, tuple) and len(result) == 3:
            _, stderr, _ = result
            return stderr or "Unknown error"
        return str(result)

    def _generate_suggestions(self):
        """生成建议"""
        if not self.report:
            return

        errors = self.report.error_history
        if not errors:
            return

        last_error = errors[-1]

        # 根据错误类型生成建议
        if last_error.error_type == "timeout":
            self.report.add_suggestion("增加超时时间")
            self.report.add_suggestion("检查网络连接")
            self.report.add_suggestion("检查服务器负载")

        elif "permission" in last_error.error_message.lower():
            self.report.add_suggestion("检查文件权限")
            self.report.add_suggestion("使用sudo执行")
            self.report.add_suggestion("检查用户权限")

        elif "not found" in last_error.error_message.lower():
            self.report.add_suggestion("检查命令/文件是否存在")
            self.report.add_suggestion("安装缺失的依赖")
            self.report.add_suggestion("检查PATH环境变量")

        elif "connection" in last_error.error_message.lower():
            self.report.add_suggestion("检查网络连接")
            self.report.add_suggestion("检查服务器是否可达")
            self.report.add_suggestion("检查防火墙设置")

        else:
            self.report.add_suggestion("查看详细错误日志")
            self.report.add_suggestion("检查服务器状态")
            self.report.add_suggestion("手动执行命令测试")

        # 添加操作选项
        self.report.add_option(
            "继续执行",
            "提供更多指导后继续",
            "continue"
        )
        self.report.add_option(
            "回滚",
            "回滚到上一个检查点",
            "rollback"
        )
        self.report.add_option(
            "终止",
            "终止当前任务",
            "abort"
        )


class MaxRetriesExceeded(Exception):
    """超过最大重试次数异常"""

    def __init__(self, report: DiagnosticReport):
        self.report = report
        super().__init__(f"超过最大重试次数: {report.task_name}")


class TimeoutError(Exception):
    """超时异常"""
    pass


def retry_on_failure(max_retries: int = 3, timeout: int = 300):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = RetryManager(RetryConfig(
                max_retries=max_retries,
                timeout=timeout
            ))
            return manager.execute_with_retry(func, func.__name__, *args, **kwargs)
        return wrapper
    return decorator
