"""HybridRetriever — 混合检索策略。

组合 Vector + BM25 检索，通过 Fusion 层合并结果。
"""

from typing import Any, Dict, List, Optional

from core.config import get_config
from core.logger import get_logger
from retrieval.fusion.weighted import WeightedFusion
from retrieval.retriever.bm25 import BM25Retriever
from retrieval.retriever.model import RetrievalResult
from retrieval.retriever.vector import VectorRetriever

logger = get_logger(__name__)


class HybridRetriever:
    """混合检索 — Vector + BM25 → Fusion。"""

    def __init__(
        self,
        vector_retriever: Optional[VectorRetriever] = None,
        bm25_retriever: Optional[BM25Retriever] = None,
    ):
        self._vector = vector_retriever or VectorRetriever()
        self._bm25 = bm25_retriever or BM25Retriever()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """执行混合检索。

        Args:
            query:   查询文本。
            top_k:   返回结果数量。
            filters: 元数据过滤条件。

        Returns:
            融合后的检索结果列表。
        """
        cfg = get_config().retrieval

        # Vector
        vector_results = self._vector.retrieve(query, top_k, filters)
        # BM25
        bm25_results = self._bm25.retrieve(query, top_k, filters)

        # Fusion
        fusion = WeightedFusion(
            vector_weight=cfg.hybrid_vector_weight,
            bm25_weight=cfg.hybrid_keyword_weight,
        )
        merged = fusion.fuse(vector_results, bm25_results)

        # 截断到 top_k
        return merged[:top_k]
