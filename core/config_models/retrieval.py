"""Retrieval Pipeline 配置模型。"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class FusionConfig:
    """Fusion 策略配置。"""
    type: str = "rrf"          # "weighted" / "rrf" / "custom"
    weights: List[float] = field(default_factory=lambda: [0.5, 0.5])


@dataclass
class RetrieverPipelineConfig:
    """Retriever Pipeline 配置。"""
    retrievers: List[str] = field(default_factory=lambda: ["vector", "bm25"])
    fusion: FusionConfig = field(default_factory=FusionConfig)
    top_k: int = 10


@dataclass
class QueryRewriteConfig:
    """Query Rewrite 配置。"""
    enabled: bool = False
    strategy: str = "llm"      # "llm" / "rule"


@dataclass
class RetrievalPipelineConfig:
    """检索流水线总配置。"""
    query: QueryRewriteConfig = field(default_factory=QueryRewriteConfig)
    pipeline: RetrieverPipelineConfig = field(default_factory=RetrieverPipelineConfig)
