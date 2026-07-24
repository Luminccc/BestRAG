"""Document Model — 统一数据协议。

所有 Parser 输出 Document，所有 Processor 消费 Document。
"""

from .document import Document
from .enums import DocumentType
from .metadata import DocumentMetadata

__all__ = [
    "Document",
    "DocumentType",
    "DocumentMetadata",
]
