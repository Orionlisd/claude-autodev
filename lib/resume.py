"""
断点续传模块
支持任务暂停、恢复、回滚
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class TaskStatus:
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    ROLLED_BACK = "rolled_back"

class Checkpoint:
    """检查点"""

    def __init__(self, phase: str, step: str, data: Dict = None):
        self.phase = phase
        self.step = step
        self.data = data or {}
        self.timestamp = datetime.now().isoformat()
        self.status = TaskStatus.COMPLETED

    def to_dict(self) -> Dict:
        return {
            "phase": self.phase,
            "step": self.step,
            "data": self.data,
            "timestamp": self.timestamp,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Checkpoint':
        cp = cls(data["phase"], data["step"], data.get("data", {}))
        cp.timestamp = data["timestamp"]
        cp.status = data["status"]
        return cp


class TaskState:
    """任务状态管理"""

    def __init__(self, task_id: str, description: str = ""):
        self.task_id = task_id
        self.description = description
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.checkpoints: List[Checkpoint] = []
        self.context: Dict = {}
        self.error: Optional[str] = None

    def add_checkpoint(self, phase: str, step: str, data: Dict = None):
        """添加检查点"""
        cp = Checkpoint(phase, step, data)
        self.checkpoints.append(cp)
        self.updated_at = datetime.now().isoformat()

    def get_current_phase(self) -> Optional[str]:
        """获取当前阶段"""
        if self.checkpoints:
            return self.checkpoints[-1].phase
        return None

    def get_completed_steps(self) -> List[str]:
        """获取已完成的步骤"""
        return [cp.step for cp in self.checkpoints if cp.status == TaskStatus.COMPLETED]

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "checkpoints": [cp.to_dict() for cp in self.checkpoints],
            "context": self.context,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'TaskState':
        state = cls(data["task_id"], data.get("description", ""))
        state.status = data["status"]
        state.created_at = data["created_at"]
        state.updated_at = data["updated_at"]
        state.checkpoints = [Checkpoint.from_dict(cp) for cp in data.get("checkpoints", [])]
        state.context = data.get("context", {})
        state.error = data.get("error")
        return state


class ResumeManager:
    """断点续传管理器"""

    def __init__(self, storage_dir: str = ".claude-autodev"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.current_task: Optional[TaskState] = None

    def create_task(self, task_id: str, description: str = "") -> TaskState:
        """创建新任务"""
        self.current_task = TaskState(task_id, description)
        self.current_task.status = TaskStatus.IN_PROGRESS
        self._save_task(self.current_task)
        return self.current_task

    def save_checkpoint(self, phase: str, step: str, data: Dict = None):
        """保存检查点"""
        if not self.current_task:
            raise ValueError("没有活动任务")

        self.current_task.add_checkpoint(phase, step, data)
        self._save_task(self.current_task)

    def pause_task(self):
        """暂停任务"""
        if self.current_task:
            self.current_task.status = TaskStatus.PAUSED
            self._save_task(self.current_task)

    def fail_task(self, error: str):
        """标记任务失败"""
        if self.current_task:
            self.current_task.status = TaskStatus.FAILED
            self.current_task.error = error
            self._save_task(self.current_task)

    def complete_task(self):
        """完成任务"""
        if self.current_task:
            self.current_task.status = TaskStatus.COMPLETED
            self._save_task(self.current_task)

    def resume_task(self, task_id: str) -> Optional[TaskState]:
        """恢复任务"""
        task_file = self.storage_dir / f"{task_id}.json"
        if not task_file.exists():
            return None

        with open(task_file, 'r') as f:
            data = json.load(f)

        self.current_task = TaskState.from_dict(data)
        self.current_task.status = TaskStatus.IN_PROGRESS
        self._save_task(self.current_task)
        return self.current_task

    def get_task(self, task_id: str) -> Optional[TaskState]:
        """获取任务状态"""
        task_file = self.storage_dir / f"{task_id}.json"
        if not task_file.exists():
            return None

        with open(task_file, 'r') as f:
            data = json.load(f)

        return TaskState.from_dict(data)

    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        tasks = []
        for task_file in self.storage_dir.glob("*.json"):
            with open(task_file, 'r') as f:
                data = json.load(f)
                tasks.append({
                    "task_id": data["task_id"],
                    "description": data.get("description", ""),
                    "status": data["status"],
                    "updated_at": data["updated_at"]
                })
        return tasks

    def rollback_to_checkpoint(self, checkpoint_index: int) -> bool:
        """回滚到指定检查点"""
        if not self.current_task:
            return False

        if checkpoint_index < 0 or checkpoint_index >= len(self.current_task.checkpoints):
            return False

        # 保留到指定检查点的内容
        self.current_task.checkpoints = self.current_task.checkpoints[:checkpoint_index + 1]
        self.current_task.status = TaskStatus.IN_PROGRESS
        self._save_task(self.current_task)
        return True

    def rollback_last_checkpoint(self) -> bool:
        """回滚到最后一个检查点"""
        if not self.current_task or not self.current_task.checkpoints:
            return False

        return self.rollback_to_checkpoint(len(self.current_task.checkpoints) - 2)

    def get_resume_point(self) -> Optional[Dict]:
        """获取恢复点信息"""
        if not self.current_task or not self.current_task.checkpoints:
            return None

        last_cp = self.current_task.checkpoints[-1]
        return {
            "phase": last_cp.phase,
            "step": last_cp.step,
            "data": last_cp.data,
            "timestamp": last_cp.timestamp
        }

    def _save_task(self, task: TaskState):
        """保存任务到文件"""
        task_file = self.storage_dir / f"{task.task_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)

    def generate_resume_script(self) -> str:
        """生成恢复脚本"""
        if not self.current_task:
            return ""

        script_lines = [
            f"# 任务恢复脚本",
            f"# 任务ID: {self.current_task.task_id}",
            f"# 状态: {self.current_task.status}",
            f"",
            f"## 已完成步骤:",
        ]

        for i, cp in enumerate(self.current_task.checkpoints):
            script_lines.append(f"{i+1}. [{cp.phase}] {cp.step} - {cp.timestamp}")

        resume_point = self.get_resume_point()
        if resume_point:
            script_lines.extend([
                f"",
                f"## 恢复点:",
                f"阶段: {resume_point['phase']}",
                f"步骤: {resume_point['step']}",
                f"时间: {resume_point['timestamp']}"
            ])

        return "\n".join(script_lines)
