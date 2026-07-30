"""Trace 模块入口。

提供统一的执行追踪能力：
- TraceContext  : 执行上下文（with 支持）
- TraceService  : 可视化数据 API
- EvaluationTrace: 评测 Trace
- GenerationTrace: 生成 Trace
"""

from .context import TraceContext
from .service import TraceService
from .evaluation import EvaluationTrace
from .generation import GenerationTrace
from .collector import BaseTraceCollector, DefaultTraceCollector
from .storage import BaseTraceStorage, MemoryTraceStorage

__all__ = [
    "TraceContext",
    "TraceService",
    "EvaluationTrace",
    "GenerationTrace",
    "BaseTraceCollector",
    "DefaultTraceCollector",
    "BaseTraceStorage",
    "MemoryTraceStorage",
]