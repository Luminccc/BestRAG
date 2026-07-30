"""KnowledgeBase Model — 知识库实体。

表示一个知识库，包含元数据、配置和生命周期状态。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from core.models import BaseModel


class KnowledgeBaseStatus(str, Enum):
    """知识库生命周期状态。"""
    CREATED = "created"
    BUILDING = "building"
    READY = "ready"
    UPDATING = "updating"
    FAILED = "failed"
    ARCHIVED = "archived"


class KnowledgeBase(BaseModel):
    """知识库。

    Usage::

        kb = KnowledgeBase(name="技术文档", description="内部技术文档库")
        kb.status = KnowledgeBaseStatus.READY
        kb.to_dict()
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
        status: KnowledgeBaseStatus = KnowledgeBaseStatus.CREATED,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.name = name
        self.description = description
        self.config = config or {}
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d["status"] = self.status.value if isinstance(self.status, Enum) else self.status
        return d
