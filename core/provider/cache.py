"""BaseCacheProvider — 缓存 Provider 抽象。

提供统一的缓存接口，支持多种后端实现：
- MemoryCacheProvider
- RedisCacheProvider
- LocalCacheProvider
"""

from abc import abstractmethod
from typing import Any, Optional

from core.provider.base import BaseProvider


class BaseCacheProvider(BaseProvider):
    """缓存 Provider 基类。"""

    name: str = "base_cache"

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，不存在返回 None。"""

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值。

        Args:
            key: 缓存键。
            value: 缓存值。
            ttl: 过期时间（秒），None 使用默认 TTL。
        """

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存，成功返回 True。"""

    def clear(self) -> None:
        """清空所有缓存（可选覆盖）。"""
