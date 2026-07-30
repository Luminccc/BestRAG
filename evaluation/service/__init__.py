"""Evaluation Service — 评测服务入口。

提供：
- EvaluationService    : v0.2 原始评测服务
- EvaluationServiceV3  : v0.3 增强评测服务（Trace + Debug + Experiment）
"""
from .evaluation_service import EvaluationService
from .evaluation_service_v3 import EvaluationServiceV3

__all__ = [
    "EvaluationService",
    "EvaluationServiceV3",
]
