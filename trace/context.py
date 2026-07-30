"""TraceContext — Trace 执行上下文。

提供 with 语句支持的 Trace/Span 上下文管理器，
自动记录开始时间、结束时间和耗时。

用法::

    ctx = TraceContext()
    trace = ctx.start_trace(TraceType.RETRIEVAL, request_id="req-1")

    with ctx.span("query_rewrite") as span:
        span.attributes["query"] = "..."

    with ctx.span("vector_search") as span:
        span.attributes["top_k"] = 10
        # 自动记录 duration
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from core.logger import get_logger
from core.models.trace import (
    Event,
    Metric,
    Span,
    SpanStatus,
    Trace,
    TraceStatus,
    TraceType,
)
from trace.collector import BaseTraceCollector, DefaultTraceCollector

logger = get_logger("trace.context")


class _SpanContext:
    """Span 上下文管理器（内部使用）。"""

    def __init__(self, ctx: "TraceContext", name: str, attributes: Optional[Dict[str, Any]] = None):
        self._ctx = ctx
        self._name = name
        self._attributes = attributes or {}
        self.span: Optional[Span] = None

    def __enter__(self) -> Span:
        self.span = self._ctx._create_span(self._name, self._attributes)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.span:
            self.span.end_time = datetime.now()
            if exc_type:
                self.span.status = SpanStatus.ERROR
                self.span.attributes["error"] = str(exc_val)
            self._ctx._collector.collect_span(self.span)


class TraceContext:
    """Trace 执行上下文。

    管理一次完整执行的 Trace 和 Span 生命周期。
    """

    def __init__(self, collector: Optional[BaseTraceCollector] = None):
        self._collector = collector or DefaultTraceCollector()
        self._current_trace: Optional[Trace] = None
        self._span_stack: list[Span] = []

    # ── Trace 生命周期 ────────────────────────────

    def start_trace(
        self,
        trace_type: TraceType,
        request_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Trace:
        """开始一个新的 Trace。"""
        trace = Trace(
            trace_type=trace_type,
            request_id=request_id,
            metadata=metadata or {},
        )
        trace.start_time = datetime.now()
        self._current_trace = trace
        self._span_stack = []
        logger.info(f"Trace 开始: {trace.id} type={trace_type}")
        return trace

    def end_trace(self, status: TraceStatus = TraceStatus.SUCCESS) -> None:
        """结束当前 Trace。"""
        if self._current_trace is None:
            logger.warning("end_trace 调用时无活跃 Trace")
            return

        trace = self._current_trace
        trace.end_time = datetime.now()
        trace.status = status
        trace.span_count = len(self._span_stack)

        self._collector.collect(trace)
        logger.info(f"Trace 结束: {trace.id} status={status}")

        # 清理
        self._current_trace = None
        self._span_stack = []

    # ── Span 管理 ─────────────────────────────────

    def span(self, name: str, **attributes: Any) -> _SpanContext:
        """创建 Span 上下文管理器。

        Usage::

            with ctx.span("embedding", model="bge-m3") as span:
                span.attributes["dim"] = 1024
        """
        return _SpanContext(self, name, attributes)

    def _create_span(self, name: str, attributes: Dict[str, Any]) -> Span:
        """创建 Span（内部方法）。"""
        trace_id = self._current_trace.id if self._current_trace else ""
        parent_id = self._span_stack[-1].id if self._span_stack else None
        span = Span(
            trace_id=trace_id,
            name=name,
            attributes=attributes,
            parent_id=parent_id,
        )
        span.start_time = datetime.now()
        self._span_stack.append(span)
        return span

    # ── 事件和指标 ────────────────────────────────

    def record_event(self, event_name: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """记录事件。"""
        trace_id = self._current_trace.id if self._current_trace else ""
        span_id = self._span_stack[-1].id if self._span_stack else None
        event = Event(
            trace_id=trace_id,
            event_name=event_name,
            payload=payload,
            span_id=span_id,
        )
        self._collector.collect_event(event)

    def record_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """记录指标。"""
        trace_id = self._current_trace.id if self._current_trace else ""
        span_id = self._span_stack[-1].id if self._span_stack else None
        metric = Metric(
            trace_id=trace_id,
            metric_name=metric_name,
            value=value,
            tags=tags,
            span_id=span_id,
        )
        self._collector.collect_metric(metric)

    # ── 属性 ──────────────────────────────────────

    @property
    def current_trace(self) -> Optional[Trace]:
        return self._current_trace

    @property
    def active(self) -> bool:
        return self._current_trace is not None
