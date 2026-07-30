"""ChunkMetadata — Chunk 结构化元数据。

提供统一的 Chunk 元数据结构，包含位置、标题、来源等信息。
用于检索时的 Filter、Ranking 和 Routing。
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Chunk 结构化元数据。

    Attributes:
        document_id: 来源 Document ID。
        chunk_index: Chunk 在文档中的顺序编号。
        strategy:    切分策略名称。
        page:        来源页码（如有）。
        heading:     所在章节标题（如有）。
        heading_level: 标题层级 1-6（如有）。
        position:    在文档中的字符起始位置。
        token_count: 文本 token 数（近似值）。
    """
    document_id: str = ""
    chunk_index: int = 0
    strategy: str = ""
    page: Optional[int] = None
    heading: str = ""
    heading_level: int = 0
    position: int = 0
    token_count: int = 0
    extra: dict[str, Any] = Field(default_factory=dict)
