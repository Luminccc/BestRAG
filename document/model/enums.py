"""DocumentType — 支持的文档类型枚举。

作为 Parser 和 Processor 之间的受控协议，
确保 file_type 字段的值是预定义集合中的一种。
"""

from enum import Enum


class DocumentType(str, Enum):
    """受支持的文档类型。

    扩展方式：在 Enum 末尾追加新成员即可，
    不会影响已有的 Document 数据结构和下游处理逻辑。
    """
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    MARKDOWN = "markdown"
    TXT = "txt"
    HTML = "html"
