"""DefaultTraceCollector — 默认 Trace 收集器。

将 Trace 数据转发到已注册的 TraceStorage。
同时通过 Logger 输出关键信息。
"""

from typing import List, Optional

from core.logger import get_logger
from core.models.trace import Event, Metric, Span, Trace
from trace.collector.base import BaseTraceCollector
from trace.storage import BaseTraceStorage, MemoryTraceStorage

logger = get_logger("trace.collector")


class DefaultTraceCollector(BaseTraceCollector):
    """默认收集器 — 转发到 Storage + Logger 输出。"""

    def __init__(self, storage: Optional[BaseTraceStorage] = None):
        self._storage = storage or MemoryTraceStorage()
        self._buffer: list = []

    def collect(self, trace: Trace) -> None:
        """收集 Trace（立刻写入 Storage）。"""
        self._storage.save(trace)
        logger.info(f"Trace 已存储: {trace.id} type={trace.trace_type}")

    def collect_span(self, span: Span) -> None:
        """收集 Span（写入 Storage）。"""
        self._storage.save_span(span)

    def collect_event(self, event: Event) -> None:
        """收集事件。"""
        self._storage.save_event(event)

    def collect_metric(self, metric: Metric) -> None:
        """收集指标。"""
        self._storage.save_metric(metric)

    def flush(self) -> None:
        """刷新缓冲区。"""
        self._buffer.clear()
