"""BaseService — Service 基类。

所有 Domain Service 继承此基类，保证：
- 统一的生命周期（initialize / close）
- 可被 Registry 管理
- 与 v0.2 BaseProvider 的风格保持一致
"""

from abc import ABC, abstractmethod


class BaseService(ABC):
    """服务基类。

    Usage::

        class KnowledgeService(BaseService):
            name = "knowledge"

            def initialize(self):
                self._db = connect_db()

            def close(self):
                self._db.close()
    """

    name: str = ""

    def initialize(self) -> None:
        """初始化服务（可选覆盖）。"""

    def close(self) -> None:
        """释放资源（可选覆盖）。"""
