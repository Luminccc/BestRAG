"""Retrieval Evaluation — 检索效果评测。

核心指标：
- Recall@K: 前 K 个结果中包含正确答案的比例
- Precision@K: 前 K 个结果中正确的比例
- MRR: 第一个正确答案的倒数排名
- NDCG: 归一化折损累计增益
"""

from math import log2
from typing import Any, Dict, List, Set

from evaluation.core.evaluator import BaseEvaluator
from evaluation.core.metric import MetricResult
from retrieval.retriever.model import RetrievalResult


class RetrievalEvaluator(BaseEvaluator):
    """检索效果评测器。

    用法::

        evaluator = RetrievalEvaluator()
        metrics = evaluator.evaluate(results, expected_ids={"doc1", "doc2"}, k=5)
    """

    name: str = "retrieval_evaluator"

    def evaluate(
        self,
        results: List[RetrievalResult],
        expected_ids: Set[str],
        k: int = 5,
        **kwargs: Any,
    ) -> List[MetricResult]:
        metrics: List[MetricResult] = []
        top_k = results[:k]

        # Recall@K
        recall = self._recall(top_k, expected_ids)
        metrics.append(MetricResult(name=f"recall@{k}", value=recall))

        # Precision@K
        precision = self._precision(top_k, expected_ids)
        metrics.append(MetricResult(name=f"precision@{k}", value=precision))

        # MRR
        mrr = self._mrr(results, expected_ids)
        metrics.append(MetricResult(name="mrr", value=mrr))

        # NDCG
        ndcg = self._ndcg(results, expected_ids, k)
        metrics.append(MetricResult(name=f"ndcg@{k}", value=ndcg))

        return metrics

    def _recall(self, top_k: List[RetrievalResult], expected: Set[str]) -> float:
        """Recall@K = 命中的期望文档数 / 总期望文档数。"""
        if not expected:
            return 0.0
        hits = sum(1 for r in top_k if r.chunk_id in expected or r.content in expected)
        return hits / len(expected)

    def _precision(self, top_k: List[RetrievalResult], expected: Set[str]) -> float:
        """Precision@K = 命中的期望文档数 / K。"""
        if not top_k:
            return 0.0
        hits = sum(1 for r in top_k if r.chunk_id in expected or r.content in expected)
        return hits / len(top_k)

    def _mrr(self, results: List[RetrievalResult], expected: Set[str]) -> float:
        """MRR = 第一个正确答案的排名倒数。"""
        for rank, r in enumerate(results, start=1):
            if r.chunk_id in expected or r.content in expected:
                return 1.0 / rank
        return 0.0

    def _ndcg(self, results: List[RetrievalResult], expected: Set[str], k: int) -> float:
        """NDCG@K — 考虑排序质量的指标。"""
        top_k = results[:k]
        dcg = 0.0
        for i, r in enumerate(top_k):
            if r.chunk_id in expected or r.content in expected:
                rel = 1.0 if i == 0 else 0.5
                dcg += rel / log2(i + 2)

        # IDCG（理想排序）
        ideal = sum(1.0 / log2(i + 2) for i in range(min(len(expected), k)))
        return dcg / ideal if ideal > 0 else 0.0
