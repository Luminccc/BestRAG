"""Feature Layer — BestRAG 业务能力组合层。

提供面向用户任务的统一入口：
- KnowledgeBaseService: 知识库生命周期管理
- QAService:            RAG 问答

Features 层不直接绑定 FastAPI，通过 Bootstrap 注入到 ApplicationContext。
"""

from .knowledge_base import KnowledgeBaseService
from .model import (
    QARequest,
    QAResponse,
    KnowledgeIngestRequest,
    KnowledgeIngestResponse,
    KnowledgeStatusResponse,
)
from .qa import QAService

__all__ = [
    # Services
    "KnowledgeBaseService",
    "QAService",
    # Models
    "QARequest",
    "QAResponse",
    "KnowledgeIngestRequest",
    "KnowledgeIngestResponse",
    "KnowledgeStatusResponse",
]
