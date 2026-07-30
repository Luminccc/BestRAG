"""Knowledge Repositories — 知识库数据访问层。

提供：
- KnowledgeBaseRepository : 知识库 CRUD
- DocumentRepository     : 文档 CRUD
- IndexRepository        : 索引记录 CRUD
"""

from .knowledge_base_repository import KnowledgeBaseRepository
from .document_repository import DocumentRepository
from .index_repository import IndexRepository

__all__ = [
    "KnowledgeBaseRepository",
    "DocumentRepository",
    "IndexRepository",
]
