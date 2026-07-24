"""MarkdownParser — Markdown 文件解析器。

读取 .md 文件的原始 Markdown 内容，返回统一的 Document 对象。
保留原始 Markdown 文本，不进行 HTML 转换或其他格式化处理。
"""

from pathlib import Path

from document.model import Document, DocumentMetadata, DocumentType

from .base import BaseParser
from .exceptions import ParserError


class MarkdownParser(BaseParser):
    """Markdown 解析器，对应 DocumentType.MARKDOWN。"""

    def parse(self, file_path: str) -> Document:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ParserError(f"路径不是文件: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            raise ParserError(f"读取文件失败: {file_path}") from e

        return Document(
            content=content,
            metadata=DocumentMetadata(
                filename=path.name,
                file_type=DocumentType.MARKDOWN,
            ),
        )
