"""DocumentMetadata — 文档属性层。

保存文档的基础信息（文件名、类型、来源、时间等），
不包含文档正文内容。

使用 datetime 而非 str 保证时间字段的类型安全和可排序性。
source 使用 str 而非 Ingress SourceType，保持 Document 与 Ingress 的解耦。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import DocumentType


class DocumentMetadata(BaseModel):
    """文档基础信息。

    Attributes:
        filename:     原始文件名（含扩展名），如 ``report.pdf``
        file_type:    文档类型枚举，与 DocumentType 严格对应
        source:       来源描述（自由字符串），如 ``upload`` / ``crawler``
        created_time: 文档创建/采集时间，可为空
        extra:        扩展属性字典，用于保存未来新增的元数据
    """
    filename: str
    file_type: DocumentType
    source: str | None = None
    created_time: datetime | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
