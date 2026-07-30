"""BaseTraceStorage — Trace 存储基类。"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from core.models.trace import Event, Metric, Span, Trace


class BaseTraceStorage(ABC):
    """Trace 存储抽象。

    支持多种后端：
    - MemoryTraceStorage（测试/开发）
    - LocalTraceStorage（生产/文件）
    """

    @abstractmethod
    def save(self, trace: Trace) -> None:
        """保存 Trace。"""

    @abstractmethod
    def save_span(self, span: Span) -> None:
        """保存 Span。"""

    @abstractmethod
    def save_event(self, event: Event) -> None:
        """保存事件。"""

    @abstractmethod
    def save_metric(self, metric: Metric) -> None:
        """保存指标。"""

    @abstractmethod
    def get(self, trace_id: str) -> Optional[Trace]:
        """获取 Trace。"""

    @abstractmethod
    def query(self, **filters: Any) -> List[Trace]:
        """查询 Trace 列表。"""

    @abstractmethod
    def delete(self, trace_id: str) -> bool:
        """删除 Trace。"""

    def get_spans(self, trace_id: str) -> List[Span]:
        """获取 Trace 的所有 Span（可选覆盖）。"""
        return []

    def get_metrics(self, trace_id: str) -> List[Metric]:
        """获取 Trace 的所有指标（可选覆盖）。"""
        return []
