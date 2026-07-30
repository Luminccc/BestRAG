"""Chunk Quality Metrics — Chunk 质量指标采集。

为后续 Evaluation Framework 提供基础数据。
当前只提供采集能力，不做自动评分。
"""

from statistics import stdev
from typing import Any, Dict, List

from processor.chunker.model import Chunk


class ChunkQualityMetrics:
    """Chunk 质量指标采集器。

    用法::

        metrics = ChunkQualityMetrics(chunks)
        report = metrics.compute()
    """

    def __init__(self, chunks: list[Chunk]):
        self._chunks = chunks

    def compute(self) -> Dict[str, Any]:
        """计算所有指标。

        Returns:
            指标字典，包含：
            - size: 平均 token 长度/字符数
            - distribution: 长度分布/方差
            - structure: 标题保留率等
        """
        if not self._chunks:
            return {"error": "empty_chunks", "chunk_count": 0}

        lengths = [len(c.content) for c in self._chunks]

        return {
            "chunk_count": len(self._chunks),
            "size": self._size_metrics(lengths),
            "distribution": self._distribution_metrics(lengths),
            "structure": self._structure_metrics(),
        }

    def _size_metrics(self, lengths: list[int]) -> Dict[str, float]:
        """Chunk 大小相关指标。"""
        return {
            "average_token_length": sum(lengths) / len(lengths) if lengths else 0,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "total_characters": sum(lengths),
        }

    def _distribution_metrics(self, lengths: list[int]) -> Dict[str, float]:
        """Chunk 分布相关指标。"""
        variance = (
            sum((x - sum(lengths) / len(lengths)) ** 2 for x in lengths) / len(lengths)
            if len(lengths) > 1
            else 0
        )
        return {
            "length_variance": variance,
            "length_stddev": variance ** 0.5,
            "uniformity": 1.0 / (1.0 + variance) if variance > 0 else 1.0,
        }

    def _structure_metrics(self) -> Dict[str, Any]:
        """Chunk 结构相关指标。"""
        heading_count = sum(
            1 for c in self._chunks if c.metadata.get("heading")
        )
        strategies = {}
        for c in self._chunks:
            s = c.metadata.get("strategy", "unknown")
            strategies[s] = strategies.get(s, 0) + 1

        return {
            "heading_preservation": heading_count,
            "heading_ratio": heading_count / len(self._chunks) if self._chunks else 0,
            "strategy_distribution": strategies,
        }
