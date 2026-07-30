"""CacheService — 缓存 Dashboard 数据服务。

提供前端缓存面板所需的统计接口。
"""

from typing import Any, Dict, Optional

from cache.core import CacheManager
from cache.core.metrics import CacheMetrics


class CacheService:
    """缓存服务 — Dashboard API。

    提供缓存运行时数据查询能力。
    """

    def __init__(self, manager: Optional[CacheManager] = None):
        self._manager = manager or CacheManager()
        self._metrics = CacheMetrics(self._manager)

    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存全貌统计。"""
        return self._metrics.to_dict()

    def get_hit_rate(self, namespace: str = "default") -> float:
        """获取命中率。"""
        return self._metrics.get_hit_rate(namespace)

    def get_namespace_stats(self) -> Dict[str, Any]:
        """获取各命名空间统计。"""
        return self._manager.get_namespace_stats()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取 Dashboard 完整数据。"""
        total = self._manager.get_total_stats()
        ns_stats = self._manager.get_namespace_stats()
        return {
            "summary": total,
            "namespaces": ns_stats,
            "total_entries": sum(
                s.get("sets", 0) - s.get("deletes", 0)
                for s in ns_stats.values()
            ),
        }
