"""MemoryTraceStorage — 基于内存的 Trace 存储（测试/开发用）。"""

from typing import Any, Dict, List, Optional

from core.models.trace import Event, Metric, Span, Trace, TraceType
from trace.storage.base import BaseTraceStorage


class MemoryTraceStorage(BaseTraceStorage):
    """内存 Trace 存储。

    适用于测试和开发环境。
    数据不持久化，进程重启后丢失。
    """

    def __init__(self):
        self._traces: Dict[str, Trace] = {}
        self._spans: Dict[str, Span] = {}
        self._events: Dict[str, Event] = {}
        self._metrics: Dict[str, Metric] = {}

    # ── 保存 ──────────────────────────────────────

    def save(self, trace: Trace) -> None:
        self._traces[trace.id] = trace

    def save_span(self, span: Span) -> None:
        self._spans[span.id] = span

    def save_event(self, event: Event) -> None:
        self._events[event.id] = event

    def save_metric(self, metric: Metric) -> None:
        self._metrics[metric.id] = metric

    # ── 查询 ──────────────────────────────────────

    def get(self, trace_id: str) -> Optional[Trace]:
        return self._traces.get(trace_id)

    def query(self, **filters: Any) -> List[Trace]:
        """查询 Trace，支持按 type 和 status 过滤。"""
        items = list(self._traces.values())
        trace_type = filters.get("trace_type")
        if trace_type:
            if isinstance(trace_type, str):
                from core.models.trace import TraceType
                trace_type = TraceType(trace_type)
            items = [t for t in items if t.trace_type == trace_type]
        status = filters.get("status")
        if status:
            items = [t for t in items if t.status == status]
        # 按时间倒序
        items.sort(key=lambda t: t.created_at, reverse=True)
        return items

    def delete(self, trace_id: str) -> bool:
        if trace_id in self._traces:
            del self._traces[trace_id]
            # 清理关联数据
            self._spans = {k: v for k, v in self._spans.items() if v.trace_id != trace_id}
            self._metrics = {k: v for k, v in self._metrics.items() if v.trace_id != trace_id}
            return True
        return False

    def get_spans(self, trace_id: str) -> List[Span]:
        return [s for s in self._spans.values() if s.trace_id == trace_id]

    def get_metrics(self, trace_id: str) -> List[Metric]:
        return [m for m in self._metrics.values() if m.trace_id == trace_id]

    def clear(self) -> None:
        """清空所有数据（测试用）。"""
        self._traces.clear()
        self._spans.clear()
        self._events.clear()
        self._metrics.clear()
