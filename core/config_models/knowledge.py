"""v0.3 Phase 1 新增 — Knowledge 配置模型。"""

from dataclasses import dataclass, field


@dataclass
class KnowledgeConfig:
    """知识库配置。"""
    default_chunk_strategy: str = "hierarchical"
    auto_sync: bool = False


@dataclass
class IndexConfig:
    """索引配置（v0.3 Knowledge Layer）。"""
    auto_rebuild: bool = True
    incremental: bool = True
    embedding_model: str = "bge-m3"
