"""BaseMetric — 指标计算基类。"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseMetric(ABC):
    """指标计算基类。

    所有指标必须实现 name() 和 calculate()。
    """

    @abstractmethod
    def name(self) -> str:
        """指标名称。"""

    @abstractmethod
    def calculate(self, **kwargs: Any) -> float:
        """计算指标值。"""
