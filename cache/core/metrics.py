"""CacheMetrics — 缓存指标收集。

提供缓存相关的 Evaluation/Efficiency 指标。
"""

from typing import Any, Dict, List

from cache.core.manager import CacheManager


class CacheMetrics:
    """缓存指标收集器。

    基于 CacheManager 统计数据生成效率指标。
    """

    def __init__(self, manager: CacheManager):
        self._manager = manager

    def get_hit_rate(self, namespace: str = "default") -> float:
        """获取命中率。"""
        return self._manager.get_stats(namespace).hit_rate

    def get_latency_saved(self, avg_latency_ms: float = 100.0) -> float:
        """估算节省延迟（ms）。"""
        total = self._manager.get_total_stats()
        return total["hits"] * avg_latency_ms

    def get_cost_saved(self, avg_cost_per_call: float = 0.01) -> float:
        """估算节省成本。"""
        total = self._manager.get_total_stats()
        return total["hits"] * avg_cost_per_call

    def to_dict(self) -> Dict[str, Any]:
        """输出效率报告。"""
        total = self._manager.get_total_stats()
        return {
            "hit_rate": total.get("hit_rate", 0),
            "total_hits": total.get("hits", 0),
            "total_misses": total.get("misses", 0),
            "estimated_latency_saved_ms": self.get_latency_saved(),
            "estimated_cost_saved": self.get_cost_saved(),
            "namespaces": self._manager.get_namespace_stats(),
        }
