"""Metric Model — Trace 指标记录。"""

from datetime import datetime
from typing import Any, Dict, Optional

from core.models import BaseModel


class Metric(BaseModel):
    """Trace 指标。

    记录执行过程中的关键指标，如：
    - latency: 120.5 (ms)
    - token_usage: 1024
    - chunk_count: 15
    - recall@5: 0.92
    """

    def __init__(
        self,
        trace_id: str,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        span_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.trace_id = trace_id
        self.metric_name = metric_name
        self.value = value
        self.tags = tags or {}
        self.span_id = span_id

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["timestamp"] = self.created_at.isoformat() if self.created_at else None
        return d
