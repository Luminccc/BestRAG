"""MetricResult — 统一指标结果模型。"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class MetricResult:
    """单一指标结果。

    Attributes:
        name:     指标名称（如 "recall@5"）。
        value:    指标数值。
        metadata: 额外信息（数据集、策略等）。
    """
    name: str = ""
    value: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
