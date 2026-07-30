"""Evaluation 配置模型。"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class EvaluationConfig:
    """Evaluation 配置。"""
    enabled: bool = False
    metrics: List[str] = field(default_factory=lambda: ["recall", "mrr", "accuracy"])
    dataset_path: str = ""
