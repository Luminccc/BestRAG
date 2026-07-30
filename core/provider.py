"""【兼容层】v0.1 BaseProvider 兼容入口。

所有新代码应通过 ``core.provider`` 包访问：:

    from core.provider import BaseEmbeddingProvider, BaseSimilarityProvider
"""

from core.provider.base import BaseProvider

# v0.2.5 新增 Provider 接口 — 方便从旧入口导入
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
