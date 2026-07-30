"""v0.3 新增 — Generation 配置模型。"""

from dataclasses import dataclass, field


@dataclass
class GenerationConfigV3:
    """Generation v0.3 配置（扩展自 v0.2）。"""
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 2048
