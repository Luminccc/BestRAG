"""CacheTrace — 缓存操作 Trace 集成。

记录每一次缓存操作（lookup/hit/miss/refresh/expire），
通过 Phase 2 Trace Framework 可观察。
"""

from typing import Any, Dict, Optional

from core.logger import get_logger
from core.models.trace import Event, Metric, Span, SpanStatus
from trace.context import TraceContext

logger = get_logger("cache.trace")


class CacheTrace:
    """缓存 Trace 助手。

    集成 Phase 2 Trace Framework，记录缓存操作。

    Usage::

        ct = CacheTrace(ctx)
        ct.record_hit("query_cache", "bestrag:query:xxx", latency_ms=0.5)
    """

    def __init__(self, trace_ctx: Optional[TraceContext] = None):
        self._ctx = trace_ctx

    def record_lookup(self, cache_type: str, cache_key: str) -> None:
        """记录缓存查询。"""
        if self._ctx and self._ctx.active:
            self._ctx.record_event("cache_lookup", {
                "cache_type": cache_type,
                "cache_key": cache_key[:40],
            })

    def record_hit(self, cache_type: str, cache_key: str, latency_ms: float = 0.0) -> None:
        """记录缓存命中。"""
        if self._ctx and self._ctx.active:
            self._ctx.record_event("cache_hit", {
                "cache_type": cache_type,
                "cache_key": cache_key[:40],
                "latency_ms": latency_ms,
            })
            self._ctx.record_metric(f"{cache_type}_hit", 1)

    def record_miss(self, cache_type: str, cache_key: str) -> None:
        """记录缓存未命中。"""
        if self._ctx and self._ctx.active:
            self._ctx.record_event("cache_miss", {
                "cache_type": cache_type,
                "cache_key": cache_key[:40],
            })
            self._ctx.record_metric(f"{cache_type}_miss", 1)

    def record_refresh(self, cache_type: str, cache_key: str, saved_ms: float = 0.0) -> None:
        """记录缓存刷新。"""
        if self._ctx and self._ctx.active:
            self._ctx.record_event("cache_refresh", {
                "cache_type": cache_type,
                "cache_key": cache_key[:40],
                "saved_cost_ms": saved_ms,
            })
            self._ctx.record_metric(f"{cache_type}_saved_ms", saved_ms)

    def record_expire(self, cache_type: str, cache_key: str) -> None:
        """记录缓存过期。"""
        if self._ctx and self._ctx.active:
            self._ctx.record_event("cache_expire", {
                "cache_type": cache_type,
                "cache_key": cache_key[:40],
            })
