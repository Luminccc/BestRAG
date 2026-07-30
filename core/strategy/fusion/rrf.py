"""RRFFusionStrategy — Reciprocal Rank Fusion 融合策略。

无需归一化分数，直接使用排名进行融合。
适合融合不同分布的多路检索结果。
"""

from math import log2
from typing import Any, Dict, List

from core.strategy.fusion.base import BaseFusionStrategy
from retrieval.retriever.model import RetrievalResult


class RRFFusionStrategy(BaseFusionStrategy):
    """RRF 融合策略。"""

    name: str = "rrf"

    def __init__(self, k: int = 60):
        """Args:
            k: RRF 常数，通常为 60。
        """
        self._k = k

    def fuse(self, results: List[List[RetrievalResult]], **kwargs: Any) -> List[RetrievalResult]:
        score_map: Dict[str, float] = {}
        result_map: Dict[str, RetrievalResult] = {}

        for strategy_results in results:
            for rank, r in enumerate(strategy_results):
                key = r.chunk_id
                # RRF score = sum of 1/(k + rank)
                score_map[key] = score_map.get(key, 0.0) + 1.0 / (self._k + rank + 1)
                if key not in result_map:
                    result_map[key] = r

        for key in result_map:
            result_map[key].score = score_map[key]

        sorted_results = sorted(result_map.values(), key=lambda r: r.score, reverse=True)
        return sorted_results
