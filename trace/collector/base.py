"""BaseTraceCollector — Trace 收集器基类。"""

from abc import ABC, abstractmethod
from typing import List

from core.models.trace import Event, Metric, Span, Trace


class BaseTraceCollector(ABC):
    """Trace 收集器基类。

    负责收集 Trace、Span、Event、Metric 数据，
    并转发到 Storage。
    """

    @abstractmethod
    def collect(self, trace: Trace) -> None:
        """收集完整的 Trace。"""

    @abstractmethod
    def collect_span(self, span: Span) -> None:
        """收集 Span。"""

    @abstractmethod
    def collect_event(self, event: Event) -> None:
        """收集事件。"""

    @abstractmethod
    def collect_metric(self, metric: Metric) -> None:
        """收集指标。"""

    def flush(self) -> None:
        """刷新缓冲区（可选覆盖）。"""
