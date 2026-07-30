"""BaseRepository — 数据仓库基类。

职责：
- 统一 CRUD 接口
- 隔离业务逻辑和存储实现
- 支持后续接入多种存储后端（Memory / File / Database）
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseRepository(ABC):
    """数据仓库基类。

    Usage::

        class DocumentRepository(BaseRepository):
            def __init__(self):
                self._store: dict[str, Document] = {}

            def save(self, obj: Document) -> Document:
                self._store[obj.id] = obj
                return obj

            def get(self, id: str) -> Optional[Document]:
                return self._store.get(id)

            def delete(self, id: str) -> bool:
                if id in self._store:
                    del self._store[id]
                    return True
                return False

            def list(self, **filters) -> List[Document]:
                return list(self._store.values())
    """

    @abstractmethod
    def save(self, obj: Any) -> Any:
        """保存对象，返回保存后的对象。"""

    @abstractmethod
    def get(self, id: str) -> Optional[Any]:
        """根据 ID 获取对象，不存在返回 None。"""

    @abstractmethod
    def delete(self, id: str) -> bool:
        """删除对象，成功返回 True，不存在返回 False。"""

    @abstractmethod
    def list(self, **filters: Any) -> List[Any]:
        """列出符合条件的对象，无过滤条件时返回全部。"""
