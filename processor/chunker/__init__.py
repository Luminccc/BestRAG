"""Processor Chunker — 文档切分层。

Strategy Pattern: 所有策略输出统一 Chunk[]，下游模块无需感知切分算法。
"""

from .model import Chunk, ChunkMetadata
from .service import CHUNK_STRATEGIES, ChunkService
from .strategy import (
    BaseChunkStrategy,
    FixedChunkStrategy,
    HeadingChunkStrategy,
    HierarchicalChunkStrategy,
    RecursiveChunkStrategy,
    SemanticChunkStrategy,
)

__all__ = [
    "Chunk",
    "ChunkMetadata",
    "BaseChunkStrategy",
    "FixedChunkStrategy",
    "RecursiveChunkStrategy",
    "HeadingChunkStrategy",
    "SemanticChunkStrategy",
    "HierarchicalChunkStrategy",
    "ChunkService",
    "CHUNK_STRATEGIES",
]
