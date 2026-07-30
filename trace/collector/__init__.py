"""Trace Collectors — 收集器模块。"""

from .base import BaseTraceCollector
from .default import DefaultTraceCollector

__all__ = [
    "BaseTraceCollector",
    "DefaultTraceCollector",
]
