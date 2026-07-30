"""EmbeddingCache — Embedding 向量缓存。

缓存 Text → Vector 映射，减少 Embedding 模型调用。
"""

from typing import Any, Dict, List, Optional

from cache.core import CacheKey, CacheManager
from core.logger import get_logger

logger = get_logger("cache.embedding")


class EmbeddingCache:
    """Embedding 缓存。

    Usage::

        cache = EmbeddingCache(manager)
        vec = cache.get("hello world", model="bge-m3")
        if vec is None:
            vec = model.embed("hello world")
            cache.set("hello world", vec, model="bge-m3")
    """

    def __init__(self, manager: Optional[CacheManager] = None):
        self._manager = manager or CacheManager()
        self._namespace = "embedding"

    def get(self, text: str, model: str = "default") -> Optional[List[float]]:
        key = CacheKey.make(self._namespace, text=text, model=model)
        return self._manager.get(key, namespace=self._namespace)

    def set(self, text: str, vector: List[float], model: str = "default",
            ttl: Optional[int] = 86400) -> None:  # 默认 TTL 24h
        key = CacheKey.make(self._namespace, text=text, model=model)
        self._manager.set(key, vector, ttl=ttl, namespace=self._namespace)
