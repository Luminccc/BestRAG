"""Provider Framework — 统一 Provider 抽象层。

提供：
- BaseProvider              : Provider 基类（生命周期管理）
- BaseEmbeddingProvider     : Embedding Provider
- BaseSimilarityProvider    : 相似度计算 Provider
- BaseRerankerProvider      : Reranker Provider
- BaseLLMProvider           : LLM Provider
- BaseCacheProvider         : v0.3 缓存 Provider
- BaseStorageProvider       : v0.3 存储 Provider
- ProviderFactory           : Provider 工厂

实现：
- JaccardSimilarityProvider : Jaccard 相似度实现
- CosineSimilarityProvider  : 余弦相似度实现
"""

from core.provider.base import BaseProvider
from core.provider.embedding import BaseEmbeddingProvider
from core.provider.similarity import (
    BaseSimilarityProvider,
    CosineSimilarityProvider,
    JaccardSimilarityProvider,
)
from core.provider.reranker import BaseRerankerProvider
from core.provider.llm import BaseLLMProvider
from core.provider.cache import BaseCacheProvider
from core.provider.storage import BaseStorageProvider
from core.provider.factory import ProviderFactory

__all__ = [
    "BaseProvider",
    "BaseEmbeddingProvider",
    "BaseSimilarityProvider",
    "BaseRerankerProvider",
    "BaseLLMProvider",
    "BaseCacheProvider",
    "BaseStorageProvider",
    "ProviderFactory",
    "JaccardSimilarityProvider",
    "CosineSimilarityProvider",
]
