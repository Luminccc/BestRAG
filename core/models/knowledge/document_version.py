"""DocumentVersion — 文档版本记录。

支持文档的多版本管理，每次更新生成一个新版本。
"""

from datetime import datetime
from typing import Any, Dict, Optional

from core.models import BaseModel


class DocumentVersion(BaseModel):
    """文档版本。

    属性:
        document_id:  文档 ID
        version:      版本号（从 1 递增）
        content:      该版本的文档内容
        checksum:     内容校验和（用于增量检测）
        metadata:     版本元数据
    """

    def __init__(
        self,
        document_id: str,
        version: int = 1,
        content: str = "",
        checksum: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self.document_id = document_id
        self.version = version
        self.content = content
        self.checksum = checksum
        self.metadata = metadata or {}
