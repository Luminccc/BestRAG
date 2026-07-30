"""Retrieval Metrics — 检索效果指标。

保留并统一 v0.2 的检索指标：
- Recall@K
- Precision@K
- MRR
- NDCG
"""

from math import log2
from typing import Any, List, Set

from evaluation.metric.base import BaseMetric


class RecallMetric(BaseMetric):
    """Recall@K — 召回率。"""

    def name(self) -> str:
        return "recall"

    def calculate(
        self,
        retrieved: List[str],
        expected: Set[str],
        k: int = 5,
        **kwargs: Any,
    ) -> float:
        if not expected:
            return 0.0
        top_k = set(retrieved[:k])
        hits = len(top_k & expected)
        return hits / len(expected)


class PrecisionMetric(BaseMetric):
    """Precision@K — 精确率。"""

    def name(self) -> str:
        return "precision"

    def calculate(
        self,
        retrieved: List[str],
        expected: Set[str],
        k: int = 5,
        **kwargs: Any,
    ) -> float:
        if not retrieved:
            return 0.0
        top_k = set(retrieved[:k])
        hits = len(top_k & expected)
        return hits / min(k, len(retrieved))


class MRRMetric(BaseMetric):
    """MRR — 平均倒数排名。"""

    def name(self) -> str:
        return "mrr"

    def calculate(
        self,
        retrieved: List[str],
        expected: Set[str],
        **kwargs: Any,
    ) -> float:
        for rank, doc_id in enumerate(retrieved, start=1):
            if doc_id in expected:
                return 1.0 / rank
        return 0.0


class NDCGMetric(BaseMetric):
    """NDCG@K — 归一化折损累计增益。"""

    def name(self) -> str:
        return "ndcg"

    def calculate(
        self,
        retrieved: List[str],
        expected: Set[str],
        k: int = 5,
        **kwargs: Any,
    ) -> float:
        top_k = retrieved[:k]
        dcg = 0.0
        for i, doc_id in enumerate(top_k):
            if doc_id in expected:
                rel = 1.0 if i == 0 else 0.5
                dcg += rel / log2(i + 2)
        ideal_count = min(len(expected), k)
        idcg = sum(1.0 / log2(i + 2) for i in range(ideal_count))
        return dcg / idcg if idcg > 0 else 0.0
