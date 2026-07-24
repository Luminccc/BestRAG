"""Document Dispatcher — Parser 调度层。

职责：根据文件类型选择正确的 Parser，不参与文件解析。
"""

from .dispatcher import DocumentDispatcher
from .exceptions import ParserNotFoundError, UnsupportedFileTypeError
from .registry import PARSER_REGISTRY

__all__ = [
    "DocumentDispatcher",
    "PARSER_REGISTRY",
    "UnsupportedFileTypeError",
    "ParserNotFoundError",
]
