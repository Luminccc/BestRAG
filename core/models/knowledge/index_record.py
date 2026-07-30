"""IndexRecord — 索引记录。

记录文档的索引状态，用于增量更新和重建追踪。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.models import BaseModel


class IndexStatus(str, Enum):
    """索引状态。"""
    PENDING = "pending"
    BUILDING = "building"
    READY = "ready"
    FAILED = "failed"


class IndexRecord(BaseModel):
    """索引记录。

    属性:
        document_id:        文档 ID
        chunk_count:        切分的 Chunk 数量
        embedding_model:    使用的 Embedding 模型
        index_time:         索引耗时（秒）
        status:             索引状态

        index_version:      索引版本标识（v0.3 Phase 2）
        content_hash:       文档内容哈希（用于增量检测）
        chunk_strategy:     切分策略名称
        embedding_dimension:向量维度
        vector_store:       向量存储后端
        build_duration:     构建耗时（秒）
    """

    def __init__(
        self,
        document_id: str,
        chunk_count: int = 0,
        embedding_model: str = "",
        index_time: float = 0.0,
        status: IndexStatus = IndexStatus.PENDING,
        # v0.3 Phase 2 增强字段
        index_version: str = "",
        content_hash: str = "",
        chunk_strategy: str = "",
        embedding_dimension: int = 0,
        vector_store: str = "",
        build_duration: float = 0.0,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.document_id = document_id
        self.chunk_count = chunk_count
        self.embedding_model = embedding_model
        self.index_time = index_time
        self.status = status
        # v0.3 Phase 2 增强字段
        self.index_version = index_version
        self.content_hash = content_hash
        self.chunk_strategy = chunk_strategy
        self.embedding_dimension = embedding_dimension
        self.vector_store = vector_store
        self.build_duration = build_duration

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        return d
