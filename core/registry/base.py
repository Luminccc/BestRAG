"""BaseRegistry — 所有 Registry 的公共基类。"""

from abc import ABC, abstractmethod
from typing import Any


class BaseRegistry(ABC):
    """注册表基类，定义统一接口。"""

    @abstractmethod
    def register(self, name: str, obj: Any) -> None:
        """注册对象。"""

    @abstractmethod
    def get(self, name: str) -> Any:
        """获取已注册的对象。"""

    @abstractmethod
    def has(self, name: str) -> bool:
        """检查对象是否已注册。"""

    @abstractmethod
    def remove(self, name: str) -> None:
        """移除指定注册项。"""

    @abstractmethod
    def clear(self) -> None:
        """清空所有注册项。"""

    def list(self) -> list[str]:
        """列出所有已注册的名称（子类可选覆盖）。"""
        raise NotImplementedError
