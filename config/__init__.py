"""BestRAG 配置 — 统一 re-export。

所有配置现已合并至 core.config，本模块保留为兼容入口。
新代码请直接使用 ``from core.config import get_config``。
"""

from core.config import (
    AppConfig,
    ConfigManager,
    CoreConfig,
    EmbeddingConfig,
    GenerationConfig,
    IndexingConfig,
    RetrievalConfig,
    RerankerConfig,
    VectorStoreConfig,
    WorkspaceConfig,
    get_config,
)

__all__ = [
    "AppConfig",
    "ConfigManager",
    "CoreConfig",
    "EmbeddingConfig",
    "GenerationConfig",
    "IndexingConfig",
    "RetrievalConfig",
    "RerankerConfig",
    "VectorStoreConfig",
    "WorkspaceConfig",
    "get_config",
]
