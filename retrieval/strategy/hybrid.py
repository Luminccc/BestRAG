"""HybridRetrievalStrategy — 混合检索策略。

组合 Vector + BM25 多路召回，返回未经融合的原始结果列表。
融合由外部 FusionStrategy 处理。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.strategy.retrieval import BaseRetrievalStrategy
from retrieval.retriever.model import RetrievalResult

logger = get_logger(__name__)


class HybridRetrievalStrategy(BaseRetrievalStrategy):
    """混合检索策略 — 同时执行 Vector + BM25，返回多路结果。"""

    name: str = "hybrid"

    def __init__(self):
        from retrieval.strategy.vector import VectorRetrievalStrategy
        from retrieval.strategy.bm25 import BM25RetrievalStrategy
        self._vector = VectorRetrievalStrategy()
        self._bm25 = BM25RetrievalStrategy()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[RetrievalResult]:
        vector_results = self._vector.retrieve(query, top_k, filters)
        bm25_results = self._bm25.retrieve(query, top_k, filters)
        # 合并去重（保留首次出现的）
        seen = set()
        merged: list[RetrievalResult] = []
        for r in vector_results + bm25_results:
            if r.chunk_id not in seen:
                seen.add(r.chunk_id)
                merged.append(r)
        logger.info(f"HybridRetrievalStrategy: {len(merged)} 条结果 (vector={len(vector_results)}, bm25={len(bm25_results)})")
        return merged
