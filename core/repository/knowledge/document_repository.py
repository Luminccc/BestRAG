"""DocumentRepository — 文档数据仓库。"""

from typing import Any, Dict, List, Optional

from core.models.knowledge import Document
from core.repository import BaseRepository


class DocumentRepository(BaseRepository):
    """文档仓库（内存实现）。

    支持按 knowledge_base_id 过滤查询。
    """

    def __init__(self):
        self._store: Dict[str, Document] = {}

    def save(self, obj: Document) -> Document:
        """保存文档。"""
        self._store[obj.id] = obj
        return obj

    def get(self, id: str) -> Optional[Document]:
        """根据 ID 获取文档。"""
        return self._store.get(id)

    def delete(self, id: str) -> bool:
        """删除文档。"""
        return self._store.pop(id, None) is not None

    def list(self, **filters: Any) -> List[Document]:
        """列出文档，支持按 knowledge_base_id 过滤。"""
        items = list(self._store.values())
        kb_id = filters.get("knowledge_base_id")
        if kb_id:
            items = [d for d in items if d.knowledge_base_id == kb_id]
        status = filters.get("status")
        if status:
            items = [d for d in items if d.status == status]
        return items
