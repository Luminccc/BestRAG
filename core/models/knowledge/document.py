"""Document Model (v0.3) — 知识库中的文档。

表示知识库内的一篇文档，包含原始内容和元数据。
注意：与 document.model.Document 不同，此模型基于 Core BaseModel。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.models import BaseModel


class DocumentStatus(str, Enum):
    """文档处理状态。"""
    PENDING = "pending"
    PARSING = "parsing"
    READY = "ready"
    FAILED = "failed"


class Document(BaseModel):
    """知识库文档（v0.3 版本）。

    属性:
        knowledge_base_id: 所属知识库 ID
        source:            原始来源（路径/URL）
        content:           文档原始内容
        metadata:          自定义元数据
        version:           当前版本号
        status:            处理状态
    """

    def __init__(
        self,
        knowledge_base_id: str,
        source: str = "",
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        version: int = 1,
        status: DocumentStatus = DocumentStatus.PENDING,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.knowledge_base_id = knowledge_base_id
        self.source = source
        self.content = content
        self.metadata = metadata or {}
        self.version = version
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        return d
