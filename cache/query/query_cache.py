"""QueryCache — 查询结果缓存。

缓存 Retrieval Result，适用于 FAQ/重复查询场景。
Key 绑定 Query + RetrievalProfile，不同 Profile 不共享。
"""

from typing import Any, Dict, List, Optional

from cache.core import CacheKey, CacheManager
from core.logger import get_logger

logger = get_logger("cache.query")


class QueryCache:
    """查询缓存。

    缓存完整检索结果，减少重复计算。

    Usage::

        cache = QueryCache(manager)
        results = cache.get("什么是 RAG?", profile="default")
        if results is None:
            results = do_retrieval(query)
            cache.set("什么是 RAG?", results, profile="default")
    """

    def __init__(self, manager: Optional[CacheManager] = None):
        self._manager = manager or CacheManager()
        self._namespace = "query"

    def get(
        self,
        query: str,
        profile: str = "default",
    ) -> Optional[Any]:
        key = CacheKey.make(self._namespace, query=query, profile=profile)
        return self._manager.get(key, namespace=self._namespace)

    def set(
        self,
        query: str,
        value: Any,
        profile: str = "default",
        ttl: Optional[int] = 3600,
    ) -> None:
        key = CacheKey.make(self._namespace, query=query, profile=profile)
        self._manager.set(key, value, ttl=ttl, namespace=self._namespace)
        logger.info(f"QueryCache SET: query={query[:30]}...")

    def delete(self, query: str, profile: str = "default") -> None:
        key = CacheKey.make(self._namespace, query=query, profile=profile)
        self._manager.delete(key, namespace=self._namespace)
