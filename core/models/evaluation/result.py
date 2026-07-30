"""EvaluationResult — 表示一次评测结果。"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from core.models import BaseModel


class EvaluationResult(BaseModel):
    """一次评测结果。

    包含评测任务的所有指标和关联 Trace。
    """

    def __init__(
        self,
        run_id: str,
        metrics: Optional[Dict[str, float]] = None,
        trace_ids: Optional[List[str]] = None,
        summary: str = "",
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at)
        self.run_id = run_id
        self.metrics = metrics or {}
        self.trace_ids = trace_ids or []
        self.summary = summary
