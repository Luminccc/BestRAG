"""EvaluationRun — 表示一次评测任务。"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.models import BaseModel


class EvaluationRunStatus(str, Enum):
    """评测运行状态。"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRun(BaseModel):
    """一次评测任务。

    记录一次评测执行的完整信息。
    """

    def __init__(
        self,
        name: str,
        dataset_id: str = "",
        strategy: str = "",
        profile: Optional[Dict[str, Any]] = None,
        status: EvaluationRunStatus = EvaluationRunStatus.PENDING,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.name = name
        self.dataset_id = dataset_id
        self.strategy = strategy
        self.profile = profile or {}
        self.status = status
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        d["completed_at"] = self.completed_at.isoformat() if self.completed_at else None
        return d
