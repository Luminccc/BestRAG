"""v0.3 Phase 4 新增 — Retrieval Optimization 配置模型。"""

from dataclasses import dataclass, field


@dataclass
class RetrievalOptimizationConfig:
    """检索优化配置。"""
    enabled: bool = True
    adaptive_selector: bool = True
    knowledge_analysis: bool = True
    feedback_loop: bool = True
