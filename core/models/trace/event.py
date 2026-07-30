"""Event Model — Trace 中的事件记录。"""

from datetime import datetime
from typing import Any, Dict, Optional

from core.models import BaseModel


class Event(BaseModel):
    """Trace 事件。

    记录执行过程中的关键事件，如：
    - chunk_created
    - embedding_failed
    - retrieval_hit
    """

    def __init__(
        self,
        trace_id: str,
        event_name: str,
        payload: Optional[Dict[str, Any]] = None,
        span_id: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.trace_id = trace_id
        self.event_name = event_name
        self.payload = payload or {}
        self.span_id = span_id

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["timestamp"] = self.created_at.isoformat() if self.created_at else None
        return d
