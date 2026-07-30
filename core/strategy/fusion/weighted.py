"""WeightedFusionStrategy — 加权分数融合。

每个检索结果按权重计算融合分数，按总分降序排列。
"""

from typing import Any, Dict, List

from core.strategy.fusion.base import BaseFusionStrategy
from retrieval.retriever.model import RetrievalResult


class WeightedFusionStrategy(BaseFusionStrategy):
    """加权融合策略。"""

    name: str = "weighted"

    def __init__(self, weights: Dict[str, float] | None = None):
        """Args:
            weights: 策略名 → 权重映射，如 {"vector": 0.7, "bm25": 0.3}。
        """
        self._weights = weights or {"vector": 0.7, "bm25": 0.3}

    def fuse(self, results: List[List[RetrievalResult]], **kwargs: Any) -> List[RetrievalResult]:
        merged: Dict[str, RetrievalResult] = {}

        for strategy_results in results:
            for r in strategy_results:
                key = r.chunk_id
                if key in merged:
                    merged[key].score += r.score
                else:
                    merged[key] = RetrievalResult(
                        chunk_id=r.chunk_id,
                        score=r.score,
                        content=r.content,
                        metadata=r.metadata,
                    )

        sorted_results = sorted(merged.values(), key=lambda r: r.score, reverse=True)
        return sorted_results
