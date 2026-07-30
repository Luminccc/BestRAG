"""OptimizationSuggestion — 优化建议。"""

from typing import Any, Dict, Optional

from core.models import BaseModel


class OptimizationSuggestion(BaseModel):
    """优化建议。

    表示一个可执行的优化操作。
    """

    def __init__(
        self,
        suggestion_type: str = "",
        target: str = "",
        value_from: str = "",
        value_to: str = "",
        reason: str = "",
        score_impact: float = 0.0,
        id: Optional[str] = None,
    ):
        super().__init__(id=id)
        self.suggestion_type = suggestion_type  # embedding_change / chunk_change / retriever_change
        self.target = target
        self.value_from = value_from
        self.value_to = value_to
        self.reason = reason
        self.score_impact = score_impact
