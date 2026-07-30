"""Retrieval Strategy — 可插拔检索策略集合。

所有策略继承自 BaseRetrievalStrategy，可注册到 RegistryCenter。
"""

from retrieval.strategy.vector import VectorRetrievalStrategy
from retrieval.strategy.bm25 import BM25RetrievalStrategy
from retrieval.strategy.hybrid import HybridRetrievalStrategy
from retrieval.strategy.metadata import MetadataRetrievalStrategy
from retrieval.strategy.context_window import ContextWindowRetrievalStrategy

__all__ = [
    "VectorRetrievalStrategy",
    "BM25RetrievalStrategy",
    "HybridRetrievalStrategy",
    "MetadataRetrievalStrategy",
    "ContextWindowRetrievalStrategy",
]
