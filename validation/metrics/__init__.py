"""Validation Metrics — 指标采集模块。

用于 Chunk 质量和后续 Evaluation Framework 的基础数据。
"""

from validation.metrics.chunk_metrics import ChunkQualityMetrics

__all__ = [
    "ChunkQualityMetrics",
]
