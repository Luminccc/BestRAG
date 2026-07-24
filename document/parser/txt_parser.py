"""TxtParser — 纯文本文件解析器。

读取 .txt 文件的全部内容，返回统一的 Document 对象。
是所有 Parser 中最简单的实现，用于验证从文件到 Document 的完整流程。
"""

from pathlib import Path

from document.model import Document, DocumentMetadata, DocumentType

from .base import BaseParser
from .exceptions import ParserError


class TxtParser(BaseParser):
    """纯文本解析器，对应 DocumentType.TXT。"""

    def parse(self, file_path: str) -> Document:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ParserError(f"路径不是文件: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # 尝试常见编码回退
            try:
                content = path.read_text(encoding="gbk")
            except Exception as e:
                raise ParserError(f"无法解码文件: {file_path}") from e
        except Exception as e:
            raise ParserError(f"读取文件失败: {file_path}") from e

        return Document(
            content=content,
            metadata=DocumentMetadata(
                filename=path.name,
                file_type=DocumentType.TXT,
            ),
        )
