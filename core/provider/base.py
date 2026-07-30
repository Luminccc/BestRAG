"""BaseProvider — 所有 Provider 的抽象基类。

与 core/provider.py 中的原始 BaseProvider 保持接口一致。

生命周期::

    provider.initialize()
    provider.do_something()
    provider.close()
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Provider 基类。

    属性:
        name: Provider 名称，用于 Registry 标识。
    """

    name: str = ""

    def initialize(self) -> None:
        """初始化（可选覆盖）。"""

    def close(self) -> None:
        """释放资源（可选覆盖）。"""
