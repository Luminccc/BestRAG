"""ParsedDocument — Parser 标准化输出模型。

包含结构化文本块（blocks），为下游 Metadata 提取和 Chunk 策略提供丰富信息。
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class TextBlock(BaseModel):
    """文档内的结构化文本块。

    Attributes:
        type:     块类型（"heading" / "paragraph" / "list" / "table" / "code" / "quote"）。
        level:    层级（heading 的级别 1-6，其他类型为 0）。
        content:  块文本内容。
        metadata: 块级元数据（页码、位置等）。
    """
    type: str = "paragraph"
    level: int = 0
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParsedDocument(BaseModel):
    """Parser 标准化输出。

    所有 Parser 的输出统一为此模型，替代直接输出 Document。

    Attributes:
        content:  原始文档全文。
        metadata: 文档级元数据（来源、类型、时间等）。
        blocks:   结构化文本块列表（为 Chunk 策略提供结构信息）。
    """
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    blocks: list[TextBlock] = Field(default_factory=list)
