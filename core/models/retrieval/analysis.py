"""RetrievalAnalysis — 检索分析结果。"""

from typing import Any, Dict, List, Optional

from core.models import BaseModel


class RetrievalAnalysis(BaseModel):
    """一次检索分析结果。

    记录检索质量、失败原因和优化建议。
    """

    def __init__(
        self,
        query: str = "",
        trace_id: str = "",
        retrieval_quality: float = 0.0,
        failure_reason: str = "",
        recommendations: Optional[List[str]] = None,
        id: Optional[str] = None,
    ):
        super().__init__(id=id)
        self.query = query
        self.trace_id = trace_id
        self.retrieval_quality = retrieval_quality
        self.failure_reason = failure_reason
        self.recommendations = recommendations or []
