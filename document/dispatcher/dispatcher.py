"""DocumentDispatcher — Parser 调度中心。

接收文件路径，识别文件类型，选择对应 Parser 并执行解析。
Dispatcher 只做调度，不做解析。
"""

from pathlib import Path

from document.model import Document

from .exceptions import UnsupportedFileTypeError
from .registry import PARSER_REGISTRY


def _extract_extension(file_path: str) -> str:
    """从文件路径中提取小写扩展名（不含前导点号）。

    Examples:
        "report.pdf"   → "pdf"
        "path/to/a.md" → "md"
        "README"       → ""
    """
    ext = Path(file_path).suffix
    return ext.lstrip(".").lower()


class DocumentDispatcher:
    """文档调度器 — 根据文件扩展名选择 Parser 并执行解析。

    Usage::

        dispatcher = DocumentDispatcher()
        doc = dispatcher.dispatch("/data/report.pdf")
    """

    def dispatch(self, file_path: str) -> Document:
        """执行完整的调度链路：识别类型 → 选择 Parser → 解析 → 返回 Document。

        Args:
            file_path: 待解析文件的路径。

        Returns:
            解析后的 Document 对象。

        Raises:
            FileNotFoundError:          文件不存在。
            UnsupportedFileTypeError:   文件类型无对应 Parser。
            ParserError:                Parser 解析过程中出错。
        """
        ext = _extract_extension(file_path)

        if not ext:
            raise UnsupportedFileTypeError(
                f"无法识别文件类型（无扩展名）: {file_path}"
            )

        parser_class = PARSER_REGISTRY.get(ext)
        if parser_class is None:
            raise UnsupportedFileTypeError(
                f"不支持的文件类型: .{ext}（无对应 Parser）"
            )

        parser = parser_class()
        return parser.parse(file_path)
