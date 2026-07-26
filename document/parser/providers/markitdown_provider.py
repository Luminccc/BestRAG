"""MarkItDownProvider — Office / 纯文本类文档解析。

基于 markitdown[all] 统一处理：
    .docx / .pptx / .xlsx / .html / .md / .txt

输出 Markdown 文本，封装为 Document 对象。
"""

from pathlib import Path

from document.model import Document, DocumentMetadata, DocumentType

from ..base import BaseParser
from ..exceptions import ParserError

# 扩展名 → DocumentType 映射
_EXT_TO_TYPE: dict[str, DocumentType] = {
    "docx": DocumentType.DOCX,
    "pptx": DocumentType.PPTX,
    "xlsx": DocumentType.XLSX,
    "html": DocumentType.HTML,
    "md":   DocumentType.MARKDOWN,
    "txt":  DocumentType.TXT,
}


class MarkItDownProvider(BaseParser):
    """MarkItDown 解析 Provider — 处理 Office 及纯文本类文件。"""

    def parse(self, file_path: str) -> Document:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ParserError(f"路径不是文件: {file_path}")

        ext = path.suffix.lstrip(".").lower()
        doc_type = _EXT_TO_TYPE.get(ext)
        if doc_type is None:
            raise ParserError(f"MarkItDownProvider 不支持的文件类型: .{ext}")

        try:
            from markitdown import MarkItDown
        except ImportError:
            raise ParserError(
                "markitdown 未安装，请执行: uv add 'markitdown[all]'"
            )

        try:
            md = MarkItDown()
            result = md.convert(str(path))
        except Exception as e:
            raise ParserError(f"MarkItDown 解析失败: {file_path}") from e

        return Document(
            content=result.markdown,
            metadata=DocumentMetadata(
                filename=path.name,
                file_type=doc_type,
            ),
        )
