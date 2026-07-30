"""BaseEvaluator — 所有 Evaluator 的抽象基类。

Evaluator 负责评测策略输出，生成结构化指标。
继承 BaseProvider 生命周期，可注册到 EvaluatorRegistry。
"""

from abc import abstractmethod
from typing import Any, List

from core.provider.base import BaseProvider
from evaluation.core.metric import MetricResult


class BaseEvaluator(BaseProvider):
    """评测器基类。

    属性:
        name: 评测器名称。
    """

    name: str = "base_evaluator"

    @abstractmethod
    def evaluate(self, *args: Any, **kwargs: Any) -> List[MetricResult]:
        """执行评测，返回指标列表。"""
