"""WeightedFusion — 加权分数融合。

V1: Weighted Score Fusion（向量分数 × weight + BM25 分数 × weight）
"""

from typing import Dict, List

from retrieval.retriever.model import RetrievalResult


class WeightedFusion:
    """加权分数融合器。

    Usage::

        fusion = WeightedFusion(vector_weight=0.7, bm25_weight=0.3)
        results = fusion.fuse(vector_results, bm25_results)
    """

    def __init__(self, vector_weight: float = 0.7, bm25_weight: float = 0.3):
        self._vector_weight = vector_weight
        self._bm25_weight = bm25_weight

    def fuse(
        self,
        vector_results: List[RetrievalResult],
        bm25_results: List[RetrievalResult],
    ) -> List[RetrievalResult]:
        """融合两组检索结果，加权合并后按总分降序排列。

        Args:
            vector_results: Vector Retriever 的结果。
            bm25_results:   BM25 Retriever 的结果。

        Returns:
            融合后的结果列表，按融合分数降序。
        """
        merged: Dict[str, RetrievalResult] = {}

        # Vector 结果
        for r in vector_results:
            key = r.chunk_id
            merged[key] = RetrievalResult(
                chunk_id=r.chunk_id,
                score=r.score * self._vector_weight,
                content=r.content,
                metadata=r.metadata,
            )

        # BM25 结果
        for r in bm25_results:
            key = r.chunk_id
            bm25_score = r.score * self._bm25_weight
            if key in merged:
                merged[key].score += bm25_score
            else:
                merged[key] = RetrievalResult(
                    chunk_id=r.chunk_id,
                    score=bm25_score,
                    content=r.content,
                    metadata=r.metadata,
                )

        # 按融合分降序
        sorted_results = sorted(merged.values(), key=lambda r: r.score, reverse=True)
        return sorted_results
