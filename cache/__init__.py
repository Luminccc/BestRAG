"""Cache Framework — 统一运行时缓存体系。

提供：
- CacheManager          : 缓存管理器（多级缓存）
- MemoryCacheProvider   : 内存缓存 Provider
- CacheKey              : 缓存 Key 生成器
- QueryCache            : 查询结果缓存
- EmbeddingCache        : Embedding 向量缓存
- RetrievalCache        : 检索结果缓存
- CacheStats            : 缓存统计
"""

from .core import CacheKey, CacheManager, CacheStats, MemoryCacheProvider
from .query import QueryCache
from .embedding import EmbeddingCache
from .retrieval import RetrievalCache

__all__ = [
    "CacheKey",
    "CacheManager",
    "CacheStats",
    "MemoryCacheProvider",
    "QueryCache",
    "EmbeddingCache",
    "RetrievalCache",
]
