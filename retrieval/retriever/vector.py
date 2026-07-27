"""VectorRetriever — 向量检索策略。

封装 Embedding → VectorSearch 流程，通过 Registry 获取 Provider。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.registry import get_service
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class VectorRetriever:
    """向量检索策略 — Query → Embedding → Milvus Search → Results。"""

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """执行向量检索。

        Args:
            query:   查询文本。
            top_k:   返回结果数量。
            filters: 元数据过滤条件（Milvus expr）。

        Returns:
            检索结果列表。
        """
        # 通过 Registry 获取 Provider
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
        logger.info(f"VectorRetriever 返回 {len(results)} 条结果")
        return results
