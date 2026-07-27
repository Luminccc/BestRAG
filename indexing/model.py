"""Indexing 域模型 — 索引任务、索引块、索引结果。"""

from typing import Any, Optional

from pydantic import BaseModel, Field

from processor.model import ProcessedDocument


class IndexChunk(BaseModel):
    """最终写入 VectorStore 的索引块。

    Attributes:
        id:          唯一标识，复用 Chunk.id。
        document_id: 来源 Document id。
        content:     原始文本。
        metadata:    扩展元数据（保留 Chunk 原始信息）。
        embedding:   向量嵌入（写入前填充）。
    """
    id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[list[float]] = None


class IndexResult(BaseModel):
    """索引任务结果。

    Attributes:
        success:     是否成功。
        document_id: 来源 Document id。
        chunk_count: 写入的 Chunk 数量。
        error:       失败时的错误信息。
    """
    success: bool
    document_id: str
    chunk_count: int = 0
    error: Optional[str] = None
