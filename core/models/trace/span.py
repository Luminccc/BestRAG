"""Span Model — Trace 内部的步骤追踪。"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.models import BaseModel


class SpanStatus(str, Enum):
    """Span 状态。"""
    OK = "ok"
    ERROR = "error"


class Span(BaseModel):
    """Trace 内的一个步骤。

    例如 Retrieval Trace 包含：
    - QueryRewrite Span
    - VectorSearch Span
    - Fusion Span
    - Rerank Span
    """

    def __init__(
        self,
        trace_id: str,
        name: str,
        status: SpanStatus = SpanStatus.OK,
        attributes: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.trace_id = trace_id
        self.name = name
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.status = status
        self.attributes = attributes or {}
        self.parent_id = parent_id

    @property
    def duration_ms(self) -> float:
        """获取 Span 耗时（毫秒）。"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        d["start_time"] = self.start_time.isoformat() if self.start_time else None
        d["end_time"] = self.end_time.isoformat() if self.end_time else None
        d["duration_ms"] = self.duration_ms
        return d
