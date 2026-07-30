"""KnowledgeBaseRepository — 知识库数据仓库。"""

from typing import Any, Dict, List, Optional

from core.models.knowledge import KnowledgeBase, KnowledgeBaseStatus
from core.repository import BaseRepository


class KnowledgeBaseRepository(BaseRepository):
    """知识库仓库（内存实现）。

    Usage::

        repo = KnowledgeBaseRepository()
        repo.save(kb)
        kb = repo.get(kb_id)
    """

    def __init__(self):
        self._store: Dict[str, KnowledgeBase] = {}

    def save(self, obj: KnowledgeBase) -> KnowledgeBase:
        """保存知识库。"""
        self._store[obj.id] = obj
        return obj

    def get(self, id: str) -> Optional[KnowledgeBase]:
        """根据 ID 获取知识库。"""
        return self._store.get(id)

    def delete(self, id: str) -> bool:
        """删除知识库。"""
        return self._store.pop(id, None) is not None

    def update(self, kb: KnowledgeBase) -> KnowledgeBase:
        """更新知识库（别名，与 save 相同）。"""
        return self.save(kb)

    def list(self, **filters: Any) -> List[KnowledgeBase]:
        """列出知识库，支持按状态过滤。"""
        items = list(self._store.values())
        status = filters.get("status")
        if status:
            if isinstance(status, str):
                status = KnowledgeBaseStatus(status)
            items = [kb for kb in items if kb.status == status]
        return items
