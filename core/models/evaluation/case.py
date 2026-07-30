"""EvaluationCase — 单条评测样本。"""

from typing import Any, Dict, List, Optional

from core.models import BaseModel


class EvaluationCase(BaseModel):
    """单条评测样本。

    包含查询、期望结果和实际检索结果，用于逐条分析。
    """

    def __init__(
        self,
        query: str,
        expected_documents: Optional[List[str]] = None,
        retrieved_documents: Optional[List[str]] = None,
        answer: str = "",
        feedback: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
    ):
        super().__init__(id=id)
        self.query = query
        self.expected_documents = expected_documents or []
        self.retrieved_documents = retrieved_documents or []
        self.answer = answer
        self.feedback = feedback
        self.metadata = metadata or {}
