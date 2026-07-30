"""Trace Storages — 存储模块。"""

from .base import BaseTraceStorage
from .memory import MemoryTraceStorage

__all__ = [
    "BaseTraceStorage",
    "MemoryTraceStorage",
]
