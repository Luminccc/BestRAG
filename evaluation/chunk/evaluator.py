"""Chunk Evaluation — Chunk 切分质量评测。"""

from statistics import stdev
from typing import Any, Dict, List

from evaluation.core.evaluator import BaseEvaluator
from evaluation.core.metric import MetricResult
from processor.chunker.model import Chunk


class ChunkEvaluator(BaseEvaluator):
    """Chunk 切分质量评测器。

    统计 chunk 大小分布、结构保留等指标。
    """

    name: str = "chunk_evaluator"

    def evaluate(self, chunks: List[Chunk], **kwargs: Any) -> List[MetricResult]:
        if not chunks:
            return [MetricResult(name="chunk_count", value=0)]

        lengths = [len(c.content) for c in chunks]
        results: List[MetricResult] = []

        # 数量
        results.append(MetricResult(name="chunk_count", value=len(chunks)))

        # 大小指标
        results.append(MetricResult(
            name="avg_chunk_size",
            value=sum(lengths) / len(lengths),
            metadata={"min": min(lengths), "max": max(lengths)},
        ))
        results.append(MetricResult(name="min_chunk_size", value=min(lengths)))
        results.append(MetricResult(name="max_chunk_size", value=max(lengths)))

        # 分布指标
        if len(lengths) > 1:
            variance = sum((x - sum(lengths) / len(lengths)) ** 2 for x in lengths) / len(lengths)
            results.append(MetricResult(name="chunk_size_variance", value=variance))
            results.append(MetricResult(name="chunk_size_stddev", value=variance ** 0.5))

        # 结构指标
        heading_count = sum(1 for c in chunks if c.metadata.get("heading"))
        results.append(MetricResult(
            name="heading_preservation",
            value=heading_count,
            metadata={"total": len(chunks), "ratio": heading_count / len(chunks)},
        ))

        return results


class ChunkCoherenceEvaluator(BaseEvaluator):
    """Chunk 语义连贯性评测器（使用文本相似度估算）。"""

    name: str = "chunk_coherence"

    def __init__(self):
        from core.provider.similarity import CosineSimilarityProvider
        self._similarity = CosineSimilarityProvider()

    def evaluate(self, chunks: List[Chunk], **kwargs: Any) -> List[MetricResult]:
        if len(chunks) < 2:
            return [MetricResult(name="coherence_score", value=1.0)]

        scores = []
        for c in chunks:
            # 将 chunk 前半与后半比较估算内部连贯性
            mid = len(c.content) // 2
            if mid < 5:
                continue
            first_half = c.content[:mid]
            second_half = c.content[mid:]
            sim = self._similarity.similarity(first_half, second_half)
            scores.append(sim)

        avg = sum(scores) / len(scores) if scores else 0
        return [MetricResult(name="coherence_score", value=avg)]
