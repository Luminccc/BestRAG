"""Knowledge Models — 知识库数据模型。

提供知识库生命周期所需的所有实体：
- KnowledgeBase    : 知识库
- Document         : 知识文档（v0.3）
- DocumentVersion  : 文档版本
- IndexRecord      : 索引记录
"""

from .knowledge_base import KnowledgeBase, KnowledgeBaseStatus
from .document import Document, DocumentStatus
from .document_version import DocumentVersion
from .index_record import IndexRecord, IndexStatus

__all__ = [
    "KnowledgeBase",
    "KnowledgeBaseStatus",
    "Document",
    "DocumentStatus",
    "DocumentVersion",
    "IndexRecord",
    "IndexStatus",
]
