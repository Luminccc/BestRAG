"""Embedding 模块初始化文件。"""

from .base import BaseEmbedding
from .model import EmbeddingResult
from .service import EmbeddingService, get_embedding_service

__all__ = [
    "BaseEmbedding",
    "EmbeddingResult",
    "EmbeddingService",
    "get_embedding_service"
]