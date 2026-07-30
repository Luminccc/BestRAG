"""Knowledge 模块入口。

提供 v0.3 Knowledge Management Layer 的完整能力：
- KnowledgeService   : 知识库管理
- DocumentService    : 文档管理
- IndexService       : 索引管理
- IndexPipelineManager: 索引生命周期管理
"""

from .service.knowledge_service import KnowledgeService
from .service.document_service import DocumentService
from .service.index_service import IndexService
from .pipeline_manager import IndexPipelineManager

__all__ = [
    "KnowledgeService",
    "DocumentService",
    "IndexService",
    "IndexPipelineManager",
]