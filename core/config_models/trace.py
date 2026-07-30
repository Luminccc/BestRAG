"""v0.3 新增 — Trace 配置模型。"""

from dataclasses import dataclass, field


@dataclass
class TraceConfig:
    """Trace 配置。"""
    enabled: bool = True
    storage: str = "local"          # local / memory / database
    max_spans: int = 1000           # 最大 Span 数量
