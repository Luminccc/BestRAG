"""v0.3 Phase 3 新增 — Evaluation v3 配置模型。"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class EvaluationConfigV3:
    """Evaluation v3 配置。"""
    enabled: bool = True
    metrics: List[str] = field(default_factory=lambda: ["recall", "ndcg", "latency"])
    trace_analysis: bool = True
    benchmark_dataset_path: str = ""
