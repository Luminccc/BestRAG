"""HeadingChunkStrategy — 基于标题结构的文档切分策略。

根据 Markdown/HTML 标题（# / ## / ### 等）切分文档，
每个标题及其下的内容形成一个 Chunk。

适合：技术文档、Markdown 知识库、结构化文档。
"""

import re
from typing import List

from processor.chunker.model import Chunk
from processor.chunker.strategy.base import BaseChunkStrategy

# 匹配 Markdown 标题：可选的 # 前缀 + 1-6 个 # + 空格 + 标题内容
_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

_DEFAULT_CHUNK_SIZE = 1000
_DEFAULT_OVERLAP = 50


class HeadingChunkStrategy(BaseChunkStrategy):
    """基于标题的文档切分。

    Usage::

        strategy = HeadingChunkStrategy()
        chunks = strategy.split(text, document_id="xxx")
    """

    name: str = "heading"

    def __init__(self, chunk_size: int = _DEFAULT_CHUNK_SIZE, overlap: int = _DEFAULT_OVERLAP):
        self._chunk_size = chunk_size
        self._overlap = overlap

    def split(self, text: str, document_id: str) -> list[Chunk]:
        if not text.strip():
            return []

        # Step 1: 找到所有标题及其位置
        sections = self._extract_sections(text)
        if not sections:
            # 没有标题，退化为单块
            return [self._make_chunk(text.strip(), document_id, 0, "", 0)]

        # Step 2: 按标题生成 Chunk
        chunks: list[Chunk] = []
        for idx, (level, heading, content) in enumerate(sections):
            chunk = self._make_chunk(
                content.strip(),
                document_id,
                idx,
                heading,
                level,
            )
            chunks.append(chunk)

        return chunks

    def _extract_sections(self, text: str) -> list[tuple[int, str, str]]:
        """按标题提取章节结构。

        Returns:
            [(level, heading_text, section_content), ...]
        """
        matches = list(_HEADING_PATTERN.finditer(text))
        if not matches:
            return []

        sections: list[tuple[int, str, str]] = []
        for i, match in enumerate(matches):
            level = len(match.group(1))
            heading = match.group(2).strip()

            # 标题内容从标题行之后到下一个标题之前
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()

            sections.append((level, heading, content))

        return sections

    def _make_chunk(self, text: str, document_id: str, index: int,
                    heading: str, level: int) -> Chunk:
        return Chunk(
            document_id=document_id,
            content=text,
            index=index,
            metadata={
                "strategy": "heading",
                "heading": heading,
                "heading_level": level,
                "chunk_size": self._chunk_size,
                "overlap": self._overlap,
            },
        )
