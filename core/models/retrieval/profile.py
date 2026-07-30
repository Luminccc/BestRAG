"""RetrievalProfile — 描述一个完整的检索配置。"""

from typing import Any, Dict, List, Optional

from core.models import BaseModel


class RetrievalProfile(BaseModel):
    """检索配置。

    包含检索相关的所有策略参数。
    """

    def __init__(
        self,
        name: str = "",
        retrievers: Optional[List[str]] = None,
        fusion: str = "rrf",
        reranker: str = "",
        embedding: str = "",
        chunk_strategy: str = "",
        top_k: int = 10,
        parameters: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
    ):
        super().__init__(id=id)
        self.name = name
        self.retrievers = retrievers or ["vector"]
        self.fusion = fusion
        self.reranker = reranker
        self.embedding = embedding
        self.chunk_strategy = chunk_strategy
        self.top_k = top_k
        self.parameters = parameters or {}
