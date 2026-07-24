"""Document Parser — 文件格式解析层。

职责：将不同格式的文件统一转换为 Document 对象。
不负责：清洗、切片、Metadata 增强。

所有 Parser 遵循 BaseParser 接口，支持按需扩展。
"""

from .base import BaseParser
from .docx_parser import DocxParser
from .exceptions import ParserError
from .markdown_parser import MarkdownParser
from .pdf_parser import PDFParser
from .txt_parser import TxtParser

__all__ = [
    "BaseParser",
    "ParserError",
    "TxtParser",
    "MarkdownParser",
    "PDFParser",
    "DocxParser",
]
