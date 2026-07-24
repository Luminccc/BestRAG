"""Document Service — 文档流程编排层。

对外提供 create_document() 作为 Document 创建的统一入口。
"""

from .document_service import DocumentService

__all__ = [
    "DocumentService",
]
