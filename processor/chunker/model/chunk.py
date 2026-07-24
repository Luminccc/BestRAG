"""Chunk — 文档切分后的最小单元。

Chunk 是 Embedding / VectorStore / Retriever 的基础数据结构。
所有 Chunk 策略必须输出 Chunk[]，确保下游模块的稳定性。
"""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """文档切分块。

    Attributes:
        id:          Chunk 唯一标识，由 uuid4() 生成。
        document_id: 来源 Document 的 id，建立 Document → Chunk 关联。
        content:     切分后的文本片段。
        index:       在 Document 中的顺序编号（从 0 开始）。
        metadata:    扩展信息（策略名、起始位置、页码、标题等）。
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    content: str
    index: int
    metadata: dict[str, Any] = Field(default_factory=dict)
