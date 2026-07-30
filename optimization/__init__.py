"""Optimization — 自适应 RAG 优化框架。

通过实验比较不同 RAG Profile 的效果，自动推荐最佳策略组合。
"""

from optimization.profile.model import RAGProfile
from optimization.profile.registry import ProfileRegistry
from optimization.optimizer.ranking import RankingEngine
from optimization.optimizer.selector import ProfileSelector
from optimization.service.optimization_service import OptimizationService

__all__ = [
    "RAGProfile",
    "ProfileRegistry",
    "RankingEngine",
    "ProfileSelector",
    "OptimizationService",
]
