"""Feature Layer 统一数据模型。

定义 Feature 层对外暴露的请求/响应模型。
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════
# QA
# ═══════════════════════════════════════════════════

class QARequest(BaseModel):
    """QA 请求。

    Attributes:
        query:           用户问题。
        metadata_filter: 可选的检索过滤条件。
        top_k:           检索返回数量。
    """
    query: str
    metadata_filter: dict[str, Any] = Field(default_factory=dict)
    top_k: int = 5


class QAResponse(BaseModel):
    """QA 响应。

    Attributes:
        answer:          LLM 生成的答案。
        sources:         检索来源列表（含 score / content / metadata）。
        retrieval_time:  检索耗时（ms）。
        generation_time: 生成耗时（ms）。
        total_time:      总耗时（ms）。
    """
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_time: float = 0.0
    generation_time: float = 0.0
    total_time: float = 0.0


# ═══════════════════════════════════════════════════
# Knowledge Base
# ═══════════════════════════════════════════════════

class KnowledgeIngestRequest(BaseModel):
    """知识库摄入请求。

    Attributes:
        file_path: 文件路径（本地文件）。
        strategy:  Chunk 策略（"recursive" / "fixed"）。
        metadata:  自定义元数据。
    """
    file_path: str
    strategy: str = "recursive"
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeIngestResponse(BaseModel):
    """知识库摄入结果。

    Attributes:
        success:      是否成功。
        document_id:  文档 ID。
        chunk_count:  切分的 Chunk 数量。
        message:      状态消息。
    """
    success: bool
    document_id: str = ""
    chunk_count: int = 0
    message: str = ""


class KnowledgeStatusResponse(BaseModel):
    """知识库状态。

    Attributes:
        total_documents: 已索引文档数。
        total_chunks:    已索引 Chunk 数。
        vectorstore:     向量库连接状态。
    """
    total_documents: int = 0
    total_chunks: int = 0
    vectorstore: str = "unknown"
