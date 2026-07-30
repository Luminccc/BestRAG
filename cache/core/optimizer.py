"""CacheOptimizer — 缓存优化引擎。

基于 Trace 和 Evaluation 数据调整缓存策略。
"""

from typing import Any, Dict, List

from cache.core import CacheManager
from cache.core.metrics import CacheMetrics
from core.logger import get_logger

logger = get_logger("cache.optimizer")


class CacheOptimizer:
    """缓存优化引擎。

    分析缓存命中率和 Query 模式，自动调整缓存策略。
    """

    def __init__(self, manager: CacheManager):
        self._manager = manager
        self._metrics = CacheMetrics(manager)

    def suggest_ttl(self, namespace: str, current_ttl: int) -> Dict[str, Any]:
        """基于命中率建议 TTL。"""
        hit_rate = self._metrics.get_hit_rate(namespace)
        suggestion = current_ttl

        if hit_rate > 0.8:
            suggestion = current_ttl * 2  # 高命中率延长 TTL
        elif hit_rate < 0.2:
            suggestion = max(60, current_ttl // 2)  # 低命中率缩短 TTL

        return {
            "namespace": namespace,
            "current_ttl": current_ttl,
            "suggested_ttl": suggestion,
            "hit_rate": hit_rate,
            "reason": "高命中率延长 TTL" if hit_rate > 0.8
                      else "低命中率缩短 TTL" if hit_rate < 0.2
                      else "保持当前 TTL",
        }

    def get_optimization_report(self, namespaces: Dict[str, int]) -> List[Dict[str, Any]]:
        """生成多命名空间的优化报告。"""
        return [self.suggest_ttl(ns, ttl) for ns, ttl in namespaces.items()]
