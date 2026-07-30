"""Evaluation — 统一评测框架。

通过 Evaluator 评测策略效果，为策略选择提供数据依据。
"""

from evaluation.core.evaluator import BaseEvaluator
from evaluation.core.metric import MetricResult
from evaluation.core.result import EvaluationReport

__all__ = [
    "BaseEvaluator",
    "MetricResult",
    "EvaluationReport",
]
