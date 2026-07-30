"""RetrievalCache — 检索结果缓存。

缓存 Query+Profile 的完整检索结果。
Key 绑定 RetrievalProfile，不同 Profile 不共享缓存。
"""

from typing import Any, Dict, List, Optional

from cache.core import CacheKey, CacheManager
from core.logger import get_logger

logger = get_logger("cache.retrieval")


class RetrievalCache:
    """检索结果缓存。

    Usage::

        cache = RetrievalCache(manager)
        results = cache.get("query", top_k=10, profile="tech")
        if results is None:
            results = pipeline.retrieve("query")
            cache.set("query", results, top_k=10, profile="tech")
    """

    def __init__(self, manager: Optional[CacheManager] = None):
        self._manager = manager or CacheManager()
        self._namespace = "retrieval"

    def get(
        self,
        query: str,
        top_k: int = 10,
        profile: str = "default",
    ) -> Optional[Any]:
        key = CacheKey.make(self._namespace, query=query, top_k=top_k, profile=profile)
        return self._manager.get(key, namespace=self._namespace)

    def set(
        self,
        query: str,
        value: Any,
        top_k: int = 10,
        profile: str = "default",
        ttl: Optional[int] = 3600,
    ) -> None:
        key = CacheKey.make(self._namespace, query=query, top_k=top_k, profile=profile)
        self._manager.set(key, value, ttl=ttl, namespace=self._namespace)
        logger.info(f"RetrievalCache SET: query={query[:30]}...")

    def delete(self, query: str, top_k: int = 10, profile: str = "default") -> None:
        key = CacheKey.make(self._namespace, query=query, top_k=top_k, profile=profile)
        self._manager.delete(key, namespace=self._namespace)
