"""BaseStorageProvider — 存储 Provider 抽象。

提供统一的持久化接口，支持多种存储后端：
- LocalStorageProvider
- S3StorageProvider
- MinioStorageProvider
"""

from abc import abstractmethod
from typing import Any, Optional


class BaseStorageProvider:
    """存储 Provider 基类。"""

    name: str = "base_storage"

    @abstractmethod
    def save(self, path: str, data: Any) -> str:
        """保存数据到指定路径，返回完整路径。"""

    @abstractmethod
    def load(self, path: str) -> Optional[Any]:
        """从指定路径加载数据，不存在返回 None。"""

    @abstractmethod
    def delete(self, path: str) -> bool:
        """删除指定路径的数据，成功返回 True。"""
