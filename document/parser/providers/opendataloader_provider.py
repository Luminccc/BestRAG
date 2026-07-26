"""OpenDataLoaderProvider — PDF 文档解析。

基于 opendataloader-pdf，V1 阶段仅使用普通模式（非 Hybrid）。
输出 Markdown 文本，封装为 Document 对象。
"""

import tempfile
from pathlib import Path

from document.model import Document, DocumentMetadata, DocumentType

from ..base import BaseParser
from ..exceptions import ParserError


class OpenDataLoaderProvider(BaseParser):
    """OpenDataLoader 解析 Provider — 处理 PDF 文件。

    V1:
        使用 opendataloader_pdf.convert() 的默认模式（无 hybrid）。
    """

    def parse(self, file_path: str) -> Document:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        if not path.is_file():
            raise ParserError(f"路径不是文件: {file_path}")

        if path.suffix.lstrip(".").lower() != "pdf":
            raise ParserError(
                f"OpenDataLoaderProvider 仅支持 PDF 文件，收到: {path.suffix}"
            )

        try:
            from opendataloader_pdf import convert
        except ImportError:
            raise ParserError(
                "opendataloader-pdf 未安装，请执行: uv add opendataloader-pdf"
            )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                convert(str(path), output_dir=tmpdir, format="markdown")

                # 输出文件名为 原文件名（不含扩展名）+ .md
                output_name = path.stem + ".md"
                output_path = Path(tmpdir) / output_name

                if not output_path.exists():
                    # 某些情况下输出文件名可能略有不同，尝试扫描
                    md_files = list(Path(tmpdir).glob("*.md"))
                    if not md_files:
                        raise ParserError(
                            f"OpenDataLoader 未生成输出文件: {file_path}"
                        )
                    output_path = md_files[0]

                content = output_path.read_text(encoding="utf-8")
        except ParserError:
            raise
        except Exception as e:
            raise ParserError(f"OpenDataLoader 解析失败: {file_path}") from e

        return Document(
            content=content,
            metadata=DocumentMetadata(
                filename=path.name,
                file_type=DocumentType.PDF,
            ),
        )
