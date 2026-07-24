"""ProcessedDocument — Processor Pipeline 的统一输出模型。

包含：
- document: 经过 Cleaner + Transformer 处理后的 Document
- chunks:   经过 Chunker 切分后的 Chunk 列表

保留 Document + Chunk[] 双结构，确保下游 Embedding 和 VectorStore
既有原始文档信息又有切分后的数据。
"""

from pydantic import BaseModel

from document.model import Document
from processor.chunker.model import Chunk


class ProcessedDocument(BaseModel):
    """Processor 管线处理结果。

    Attributes:
        document: 标准化后的 Document（已清洗 + 溯源增强）。
        chunks:   从 Document 切分得到的 Chunk 列表。
    """
    document: Document
    chunks: list[Chunk]
