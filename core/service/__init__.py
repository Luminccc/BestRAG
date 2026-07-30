"""v0.3 Service 框架 — 统一服务层基类。

所有 Domain Service (KnowledgeService / TraceService / EvaluationService)
通过 BaseService 统一生命周期管理。
"""

from .base import BaseService

__all__ = ["BaseService"]
