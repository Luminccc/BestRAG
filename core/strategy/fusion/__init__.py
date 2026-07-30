"""Fusion Strategy — 检索结果融合策略集合。

所有融合策略继承自 BaseFusionStrategy。
"""

from core.strategy.fusion.base import BaseFusionStrategy
from core.strategy.fusion.weighted import WeightedFusionStrategy
from core.strategy.fusion.rrf import RRFFusionStrategy

__all__ = [
    "BaseFusionStrategy",
    "WeightedFusionStrategy",
    "RRFFusionStrategy",
]
