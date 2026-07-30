"""VectorRetrievalStrategy — 向量检索策略。

使用 EmbeddingProvider + VectorStoreProvider 执行语义检索。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.registry import get_service
from core.strategy.retrieval import BaseRetrievalStrategy
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class VectorRetrievalStrategy(BaseRetrievalStrategy):
    """向量检索策略。"""

    name: str = "vector"

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        embedding_svc = get_service("embedding")
        vector_result = embedding_svc.embed_text(query)

        vector_store = get_service("vector_store")
        hits = vector_store.search(vector_result.vector, top_k, filters)

        results = [
            RetrievalResult(
                chunk_id=hit[0],
                score=hit[1],
                content=hit[2],
                metadata=hit[3],
            )
            for hit in hits
        ]
        logger.info(f"VectorRetrievalStrategy: {len(results)} 条结果")
        return results
