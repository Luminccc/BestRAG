"""Evaluation Metrics — 统一指标模块。

提供：
- BaseMetric         : 指标基类
- RecallMetric       : 召回率
- PrecisionMetric    : 精确率
- MRRMetric          : 平均倒数排名
- NDCGMetric         : 归一化折损累计增益
- HitRateMetric      : 命中率（v0.3 Phase 3）
- DiversityScore     : 多样性评分（v0.3 Phase 3）
- CoverageScore      : 覆盖评分（v0.3 Phase 3）
"""

from .base import BaseMetric
from .retrieval import RecallMetric, PrecisionMetric, MRRMetric, NDCGMetric
from .quality import HitRateMetric, DiversityScore, CoverageScore

__all__ = [
    "BaseMetric",
    "RecallMetric",
    "PrecisionMetric",
    "MRRMetric",
    "NDCGMetric",
    "HitRateMetric",
    "DiversityScore",
    "CoverageScore",
]
