"""
审计日志模块
记录所有执行操作，支持回滚
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class CommandRecord:
    """命令记录"""

    def __init__(self, seq: int, command: str, exit_code: int = None,
                 stdout: str = "", stderr: str = "", duration: float = 0):
        self.seq = seq
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout[:1000]  # 限制长度
        self.stderr = stderr[:1000]
        self.duration = duration
        self.timestamp = datetime.now().isoformat()
        self.reversible = self._check_reversible()
        self.rollback_cmd = self._get_rollback_command()

    def _check_reversible(self) -> bool:
        """检查命令是否可回滚"""
        reversible_patterns = [
            ("mkdir", "rmdir"),
            ("cp ", "rm "),
            ("mv ", "mv back"),
            ("echo >", "rm "),
            ("echo >>", ""),
            ("yum install", "yum remove"),
            ("apt install", "apt remove"),
            ("npm install", "npm uninstall"),
            ("pip install", "pip uninstall"),
            ("touch", "rm"),
            ("tar xzf", "rm -rf"),
            ("unzip", "rm -rf"),
            ("chown", ""),
            ("chmod", ""),
            ("sed -i", ""),
            ("pm2 start", "pm2 delete"),
            ("pm2 restart", ""),
        ]

        cmd_lower = self.command.lower()
        for pattern, _ in reversible_patterns:
            if pattern in cmd_lower:
                return True
        return False

    def _get_rollback_command(self) -> Optional[str]:
        """获取回滚命令"""
        cmd = self.command.strip()
        cmd_lower = cmd.lower()

        # mkdir -> rmdir
        if cmd_lower.startswith("mkdir"):
            dir_path = cmd.split()[-1].strip('"')
            return f"rmdir {dir_path}"

        # cp -> rm
        if cmd_lower.startswith("cp"):
            parts = cmd.split()
            if len(parts) >= 3:
                dest = parts[-1].strip('"')
                return f"rm -rf {dest}"

        # touch -> rm
        if cmd_lower.startswith("touch"):
            file_path = cmd.split()[-1].strip('"')
            return f"rm -f {file_path}"

        # echo > -> rm
        if " > " in cmd:
            file_path = cmd.split(">")[-1].strip()
            return f"rm -f {file_path}"

        # tar xzf -> rm extracted dir
        if "tar xzf" in cmd_lower or "tar xvf" in cmd_lower:
            parts = cmd.split()
            for i, part in enumerate(parts):
                if part == "-C" and i + 1 < len(parts):
                    return f"rm -rf {parts[i+1]}/*"

        # pm2 start -> pm2 delete
        if "pm2 start" in cmd_lower:
            name_match = cmd.split("--name")
            if len(name_match) > 1:
                name = name_match[1].strip().split()[0]
                return f"pm2 delete {name}"

        # yum/apt install -> remove
        if "yum install" in cmd_lower:
            packages = cmd.replace("yum install -y", "").replace("yum install", "").strip()
            return f"yum remove -y {packages}"

        if "apt install" in cmd_lower:
            packages = cmd.replace("apt install -y", "").replace("apt install", "").strip()
            return f"apt remove -y {packages}"

        # npm install -> npm uninstall
        if "npm install" in cmd_lower:
            packages = cmd.replace("npm install", "").replace("--save", "").strip()
            return f"npm uninstall {packages}"

        return None

    def to_dict(self) -> Dict:
        return {
            "seq": self.seq,
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration": self.duration,
            "timestamp": self.timestamp,
            "reversible": self.reversible,
            "rollback_cmd": self.rollback_cmd
        }


class ExecutionLog:
    """执行日志"""

    def __init__(self, execution_id: str = None):
        self.execution_id = execution_id or f"exec-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.start_time = datetime.now()
        self.end_time = None
        self.commands: List[CommandRecord] = []
        self.status = "running"
        self.metadata: Dict = {}

    def add_command(self, command: str, exit_code: int = None,
                   stdout: str = "", stderr: str = "", duration: float = 0) -> CommandRecord:
        """添加命令记录"""
        seq = len(self.commands) + 1
        record = CommandRecord(seq, command, exit_code, stdout, stderr, duration)
        self.commands.append(record)
        return record

    def set_metadata(self, key: str, value):
        """设置元数据"""
        self.metadata[key] = value

    def complete(self, status: str = "completed"):
        """标记完成"""
        self.end_time = datetime.now()
        self.status = status

    def get_duration(self) -> float:
        """获取总耗时"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.get_duration(),
            "status": self.status,
            "metadata": self.metadata,
            "commands": [cmd.to_dict() for cmd in self.commands],
            "total_commands": len(self.commands),
            "reversible_commands": sum(1 for cmd in self.commands if cmd.reversible)
        }


class AuditLogger:
    """审计日志管理器"""

    def __init__(self, log_dir: str = ".claude-autodev/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log: Optional[ExecutionLog] = None

    def start_execution(self, execution_id: str = None,
                       metadata: Dict = None) -> ExecutionLog:
        """开始新的执行"""
        self.current_log = ExecutionLog(execution_id)
        if metadata:
            self.current_log.metadata = metadata
        return self.current_log

    def log_command(self, command: str, exit_code: int = None,
                   stdout: str = "", stderr: str = "", duration: float = 0):
        """记录命令执行"""
        if not self.current_log:
            self.start_execution()

        record = self.current_log.add_command(
            command, exit_code, stdout, stderr, duration
        )

        # 实时写入日志
        self._write_log_entry(record)
        return record

    def end_execution(self, status: str = "completed"):
        """结束执行"""
        if self.current_log:
            self.current_log.complete(status)
            self._save_log()

    def get_log_file(self) -> Path:
        """获取日志文件路径"""
        return self.log_dir / f"{self.current_log.execution_id}.json"

    def _write_log_entry(self, record: CommandRecord):
        """实时写入日志条目"""
        log_file = self.get_log_entry_file()

        entry = {
            "timestamp": record.timestamp,
            "seq": record.seq,
            "command": record.command,
            "exit_code": record.exit_code,
            "duration": record.duration
        }

        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def _get_log_entry_file(self) -> Path:
        """获取实时日志文件"""
        if self.current_log:
            return self.log_dir / f"{self.current_log.execution_id}.jsonl"
        return self.log_dir / "current.jsonl"

    def _save_log(self):
        """保存完整日志"""
        if not self.current_log:
            return

        log_file = self.log_dir / f"{self.current_log.execution_id}.json"
        with open(log_file, 'w') as f:
            json.dump(self.current_log.to_dict(), f, indent=2)

    def generate_rollback_script(self) -> str:
        """生成回滚脚本"""
        if not self.current_log:
            return ""

        lines = [
            "#!/bin/bash",
            f"# 回滚脚本 - {self.current_log.execution_id}",
            f"# 生成时间: {datetime.now().isoformat()}",
            f"# 命令数量: {len(self.current_log.commands)}",
            "",
            "set -e",
            "",
            "# 按逆序执行回滚命令",
        ]

        # 逆序遍历命令
        for cmd in reversed(self.current_log.commands):
            if cmd.reversible and cmd.rollback_cmd:
                lines.extend([
                    f"",
                    f"# 回滚命令 {cmd.seq}: {cmd.command}",
                    f"# 原始时间: {cmd.timestamp}",
                    f"echo '回滚命令 {cmd.seq}...'",
                    f"{cmd.rollback_cmd} || echo '回滚失败，跳过'",
                ])

        lines.extend([
            "",
            "echo '回滚完成！'"
        ])

        return "\n".join(lines)

    def save_rollback_script(self, script_path: str = None):
        """保存回滚脚本"""
        if not script_path:
            script_path = self.log_dir / f"rollback_{self.current_log.execution_id}.sh"

        script = self.generate_rollback_script()
        with open(script_path, 'w') as f:
            f.write(script)

        # 设置可执行权限
        os.chmod(script_path, 0o755)
        return script_path

    def load_log(self, execution_id: str) -> Optional[ExecutionLog]:
        """加载历史日志"""
        log_file = self.log_dir / f"{execution_id}.json"
        if not log_file.exists():
            return None

        with open(log_file, 'r') as f:
            data = json.load(f)

        log = ExecutionLog(data["execution_id"])
        log.start_time = datetime.fromisoformat(data["start_time"])
        if data["end_time"]:
            log.end_time = datetime.fromisoformat(data["end_time"])
        log.status = data["status"]
        log.metadata = data.get("metadata", {})

        for cmd_data in data.get("commands", []):
            record = CommandRecord(
                seq=cmd_data["seq"],
                command=cmd_data["command"],
                exit_code=cmd_data.get("exit_code"),
                stdout=cmd_data.get("stdout", ""),
                stderr=cmd_data.get("stderr", ""),
                duration=cmd_data.get("duration", 0)
            )
            log.commands.append(record)

        return log

    def list_logs(self) -> List[Dict]:
        """列出所有日志"""
        logs = []
        for log_file in self.log_dir.glob("*.json"):
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    logs.append({
                        "execution_id": data["execution_id"],
                        "start_time": data["start_time"],
                        "end_time": data.get("end_time"),
                        "status": data["status"],
                        "total_commands": data.get("total_commands", 0)
                    })
            except:
                continue
        return logs

    def replay_log(self, execution_id: str) -> List[str]:
        """重放日志，返回命令列表"""
        log = self.load_log(execution_id)
        if not log:
            return []

        return [cmd.command for cmd in log.commands]

    def generate_report(self) -> str:
        """生成执行报告"""
        if not self.current_log:
            return ""

        log = self.current_log
        duration = log.get_duration()

        lines = [
            f"## 执行报告",
            f"",
            f"### 基本信息",
            f"- **执行ID**: {log.execution_id}",
            f"- **开始时间**: {log.start_time.isoformat()}",
            f"- **结束时间**: {log.end_time.isoformat() if log.end_time else '进行中'}",
            f"- **总耗时**: {duration:.1f}秒",
            f"- **状态**: {log.status}",
            f"",
            f"### 命令统计",
            f"- **总命令数**: {len(log.commands)}",
            f"- **可回滚命令**: {sum(1 for cmd in log.commands if cmd.reversible)}",
            f"- **成功命令**: {sum(1 for cmd in log.commands if cmd.exit_code == 0)}",
            f"- **失败命令**: {sum(1 for cmd in log.commands if cmd.exit_code and cmd.exit_code != 0)}",
            f"",
            f"### 执行详情",
        ]

        for cmd in log.commands:
            status = "✅" if cmd.exit_code == 0 else "❌" if cmd.exit_code else "⏳"
            lines.append(f"{status} `{cmd.command}` ({cmd.duration:.1f}s)")

        return "\n".join(lines)
