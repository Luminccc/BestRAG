"""MemoryCacheProvider — 基于内存的缓存 Provider。"""

import time
from typing import Any, Dict, Optional, Tuple

from core.provider.cache import BaseCacheProvider


class CacheEntry:
    """缓存条目，含值和过期时间。"""
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.expires_at = (time.time() + ttl) if ttl else None

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


class MemoryCacheProvider(BaseCacheProvider):
    """内存缓存 Provider。

    支持 TTL 过期和 LRU 淘汰。

    Usage::

        cache = MemoryCacheProvider()
        cache.set("key", "value", ttl=3600)
        val = cache.get("key")
    """

    name = "memory_cache"

    def __init__(self, max_size: int = 10000):
        self._store: Dict[str, CacheEntry] = {}
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expired:
            del self._store[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self._store) >= self._max_size:
            self._evict_one()
        self._store[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        self._store.clear()

    def size(self) -> int:
        """当前条目数。"""
        return len(self._store)

    def _evict_one(self) -> None:
        """淘汰一个条目（简单实现：删除最早的）。"""
        if self._store:
            oldest = next(iter(self._store))
            del self._store[oldest]
