"""v0.3 Repository 框架 — 数据访问层抽象。

隔离业务逻辑和存储实现，所有数据持久化通过 Repository 完成。
"""

from .base import BaseRepository

__all__ = ["BaseRepository"]
