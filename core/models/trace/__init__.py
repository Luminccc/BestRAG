"""Trace Models — 追踪数据模型。

提供执行链路追踪所需的所有实体：
- Trace  : 一次完整执行
- Span   : Trace 内的步骤
- Event  : 执行中的事件
- Metric : 执行指标
"""

from .trace import Trace, TraceType, TraceStatus
from .span import Span, SpanStatus
from .event import Event
from .metric import Metric

__all__ = [
    "Trace",
    "TraceType",
    "TraceStatus",
    "Span",
    "SpanStatus",
    "Event",
    "Metric",
]
