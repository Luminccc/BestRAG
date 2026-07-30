"""Evaluation Models — 评测数据模型。

提供评测业务所需的实体：
- EvaluationRun     : 评测任务
- EvaluationResult  : 评测结果
- EvaluationCase    : 评测样本
"""

from .run import EvaluationRun, EvaluationRunStatus
from .result import EvaluationResult
from .case import EvaluationCase

__all__ = [
    "EvaluationRun",
    "EvaluationRunStatus",
    "EvaluationResult",
    "EvaluationCase",
]
