"""CacheManager — 统一缓存管理器。

管理多个缓存 Provider，支持多级缓存（L1/L2/L3）。
"""

from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.provider.cache import BaseCacheProvider

logger = get_logger("cache.manager")


class CacheStats:
    """缓存统计信息。"""
    def __init__(self):
        self.hits: int = 0
        self.misses: int = 0
        self.sets: int = 0
        self.deletes: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "hit_rate": self.hit_rate,
        }


class CacheManager:
    """缓存管理器。

    支持多级缓存：
    - L1: Memory（最快）
    - L2: Local（可选）
    - L3: Redis/Distributed（可选）

    Usage::

        mgr = CacheManager(memory_provider)
        mgr.set("key", "value", ttl=3600)
        val = mgr.get("key")
    """

    def __init__(
        self,
        providers: Optional[List[BaseCacheProvider]] = None,
    ):
        self._providers = providers or []
        self._stats: Dict[str, CacheStats] = {}
        self._namespace_stats: Dict[str, CacheStats] = {}

    def add_provider(self, provider: BaseCacheProvider, name: str = "") -> None:
        """添加缓存 Provider。"""
        self._providers.append(provider)

    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """获取缓存（按 L1→L2→L3 顺序查询）。"""
        for provider in self._providers:
            val = provider.get(key)
            if val is not None:
                self._record_hit(namespace)
                # 回填到上层 Provider
                return val
        self._record_miss(namespace)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> None:
        """设置缓存（写入所有 Provider）。"""
        for provider in self._providers:
            provider.set(key, value, ttl)
        self._record_set(namespace)

    def delete(self, key: str, namespace: str = "default") -> bool:
        """删除缓存。"""
        result = False
        for provider in self._providers:
            if provider.delete(key):
                result = True
        if result:
            self._record_delete(namespace)
        return result

    def clear(self) -> None:
        """清空所有缓存。"""
        for provider in self._providers:
            provider.clear()

    # ── 统计 ──────────────────────────────────────

    def get_stats(self, namespace: str = "default") -> CacheStats:
        """获取指定命名空间的统计。"""
        return self._namespace_stats.setdefault(namespace, CacheStats())

    def get_total_stats(self) -> Dict[str, Any]:
        """获取全局统计。"""
        total = CacheStats()
        for ns, stats in self._namespace_stats.items():
            total.hits += stats.hits
            total.misses += stats.misses
            total.sets += stats.sets
            total.deletes += stats.deletes
        return total.to_dict()

    def get_namespace_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取各命名空间统计。"""
        return {ns: stats.to_dict() for ns, stats in self._namespace_stats.items()}

    def _record_hit(self, namespace: str) -> None:
        self.get_stats(namespace).hits += 1

    def _record_miss(self, namespace: str) -> None:
        self.get_stats(namespace).misses += 1

    def _record_set(self, namespace: str) -> None:
        self.get_stats(namespace).sets += 1

    def _record_delete(self, namespace: str) -> None:
        self.get_stats(namespace).deletes += 1
