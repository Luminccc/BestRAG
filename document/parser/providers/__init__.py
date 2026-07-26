"""Parser Provider 层 — 唯一解析入口。

Provider 遵循 BaseParser 接口，由 Dispatcher 按文件类型选择。
每个 Provider 封装一个第三方解析库，对外输出统一的 Document 对象。
"""

from .markitdown_provider import MarkItDownProvider
from .opendataloader_provider import OpenDataLoaderProvider

__all__ = [
    "MarkItDownProvider",
    "OpenDataLoaderProvider",
]
