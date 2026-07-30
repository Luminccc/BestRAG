"""Strategy 配置模型 — 控制策略选择。"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ChunkStrategyConfig:
    """Chunk 策略配置。"""
    type: str = "recursive"
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyConfig:
    """策略总配置。"""
    enabled: bool = True
    chunk: ChunkStrategyConfig = field(default_factory=ChunkStrategyConfig)
