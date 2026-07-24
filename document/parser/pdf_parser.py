"""PDFParser — PDF 文件解析器。

使用 PyMuPDF (fitz) 提取 PDF 文档中的文本内容。
PyMuPDF 性能高、API 简单，是 Python 生态中最成熟的 PDF 文本提取方案之一。
"""

from pathlib import Path

from document.model import Document, DocumentMetadata, DocumentType

from .base import BaseParser
from .exceptions import ParserError


class PDFParser(BaseParser):
    """PDF 解析器，对应 DocumentType.PDF。"""

    def parse(self, file_path: str) -> Document:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ParserError(f"路径不是文件: {file_path}")

        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ParserError(
                "PyMuPDF 未安装，请执行: pip install pymupdf"
            )

        try:
            doc = fitz.open(str(path))
        except Exception as e:
            raise ParserError(f"无法打开 PDF 文件: {file_path}") from e

        pages_text: list[str] = []
        try:
            for page in doc:
                text = page.get_text()
                pages_text.append(text)
        except Exception as e:
            raise ParserError(f"提取 PDF 文本时出错: {file_path}") from e
        finally:
            doc.close()

        content = "\n\n".join(pages_text)

        return Document(
            content=content,
            metadata=DocumentMetadata(
                filename=path.name,
                file_type=DocumentType.PDF,
            ),
        )
