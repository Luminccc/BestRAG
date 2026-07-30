"""Trace Model — 表示一次完整的执行追踪。"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from core.models import BaseModel


class TraceType(str, Enum):
    """Trace 类型。"""
    INDEX = "index"
    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    EVALUATION = "evaluation"


class TraceStatus(str, Enum):
    """Trace 状态。"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class Trace(BaseModel):
    """一次完整执行追踪。

    包含整个请求链路，由多个 Span 组成。
    """

    def __init__(
        self,
        trace_type: TraceType,
        request_id: str = "",
        status: TraceStatus = TraceStatus.PENDING,
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.trace_type = trace_type
        self.request_id = request_id or self.id
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = status
        self.metadata = metadata or {}
        self.span_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["trace_type"] = self.trace_type.value if isinstance(self.trace_type, Enum) else self.trace_type
        d["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        d["start_time"] = self.start_time.isoformat() if self.start_time else None
        d["end_time"] = self.end_time.isoformat() if self.end_time else None
        return d
