"""IndexRepository — 索引记录数据仓库。"""

from typing import Any, Dict, List, Optional

from core.models.knowledge import IndexRecord, IndexStatus
from core.repository import BaseRepository


class IndexRepository(BaseRepository):
    """索引记录仓库（内存实现）。

    支持按 document_id 查询索引状态。
    """

    def __init__(self):
        self._store: Dict[str, IndexRecord] = {}

    def save(self, obj: IndexRecord) -> IndexRecord:
        """保存索引记录。"""
        self._store[obj.id] = obj
        return obj

    def get(self, id: str) -> Optional[IndexRecord]:
        """根据 ID 获取索引记录。"""
        return self._store.get(id)

    def delete(self, id: str) -> bool:
        """删除索引记录。"""
        return self._store.pop(id, None) is not None

    def list(self, **filters: Any) -> List[IndexRecord]:
        """列出索引记录，支持按 document_id 或 status 过滤。"""
        items = list(self._store.values())
        doc_id = filters.get("document_id")
        if doc_id:
            items = [r for r in items if r.document_id == doc_id]
        status = filters.get("status")
        if status:
            if isinstance(status, str):
                status = IndexStatus(status)
            items = [r for r in items if r.status == status]
        return items

    def find_by_document(self, document_id: str) -> Optional[IndexRecord]:
        """根据文档 ID 查找最新索引记录。"""
        records = [r for r in self._store.values() if r.document_id == document_id]
        if not records:
            return None
        return max(records, key=lambda r: r.created_at)
