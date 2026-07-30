"""EvaluationReport — 评测报告模型。"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from evaluation.core.metric import MetricResult


@dataclass
class EvaluationReport:
    """评测报告。

    包含评测场景、策略配置和所有指标结果。

    Attributes:
        scenario:        评测场景名称。
        strategy_profile: 策略配置。
        metrics:         指标列表。
        metadata:        额外信息（耗时、数据集大小等）。
    """
    scenario: str = ""
    strategy_profile: Dict[str, str] = field(default_factory=dict)
    metrics: List[MetricResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转为字典。"""
        return {
            "scenario": self.scenario,
            "strategy_profile": self.strategy_profile,
            "metrics": [
                {"name": m.name, "value": m.value, "metadata": m.metadata}
                for m in self.metrics
            ],
            "metadata": self.metadata,
        }

    def get_metric(self, name: str) -> float:
        """按名称获取指标值。"""
        for m in self.metrics:
            if m.name == name:
                return m.value
        return 0.0
