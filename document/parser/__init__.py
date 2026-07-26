"""Document Parser — 文件格式解析层。

职责：将不同格式的文件统一转换为 Document 对象。
不负责：清洗、切片、Metadata 增强。

所有 Provider 遵循 BaseParser 接口，由 Dispatcher 按文件类型选择。
"""

from .base import BaseParser
from .exceptions import ParserError
from .providers import MarkItDownProvider, OpenDataLoaderProvider

__all__ = [
    "BaseParser",
    "ParserError",
    "MarkItDownProvider",
    "OpenDataLoaderProvider",
]
