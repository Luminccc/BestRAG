"""v0.3 模型框架 — 统一数据模型基类。

提供：
- BaseModel  : 所有业务 Model 的父类
- Metadata   : 通用元数据容器
"""

from .base import BaseModel
from .metadata import Metadata

__all__ = [
    "BaseModel",
    "Metadata",
]
