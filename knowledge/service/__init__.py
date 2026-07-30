"""Knowledge Services — 知识库业务服务层。

提供：
- KnowledgeService : 知识库管理
- DocumentService  : 文档管理
- IndexService     : 索引管理
"""

from .knowledge_service import KnowledgeService
from .document_service import DocumentService
from .index_service import IndexService

__all__ = [
    "KnowledgeService",
    "DocumentService",
    "IndexService",
]
