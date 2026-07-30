"""FixedChunkStrategy — 固定长度切分策略。

按 chunk_size 切分，相邻 Chunk 之间保留 overlap 字符作为上下文重叠。
适合通用文本，无需考虑文档结构。
"""

from processor.chunker.model import Chunk
from processor.chunker.strategy.base import BaseChunkStrategy

_DEFAULT_CHUNK_SIZE = 500
_DEFAULT_OVERLAP = 50


class FixedChunkStrategy(BaseChunkStrategy):
    """固定长度切分。

    Usage::

        strategy = FixedChunkStrategy(chunk_size=500, overlap=50)
        chunks = strategy.split(text, document_id="xxx")
    """

    name: str = "fixed"

    def __init__(self, chunk_size: int = _DEFAULT_CHUNK_SIZE, overlap: int = _DEFAULT_OVERLAP):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size 必须 > 0，当前值: {chunk_size}")
        if overlap < 0:
            raise ValueError(f"overlap 必须 >= 0，当前值: {overlap}")
        if overlap >= chunk_size:
            raise ValueError(f"overlap ({overlap}) 不能 >= chunk_size ({chunk_size})")

        self._chunk_size = chunk_size
        self._overlap = overlap

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    @property
    def overlap(self) -> int:
        return self._overlap

    def split(self, text: str, document_id: str) -> list[Chunk]:
        if not text:
            return []

        chunks: list[Chunk] = []
        step = self._chunk_size - self._overlap
        pos = 0
        idx = 0

        while pos < len(text):
            segment = text[pos:pos + self._chunk_size]
            chunk = Chunk(
                document_id=document_id,
                content=segment,
                index=idx,
                metadata={
                    "strategy": "fixed",
                    "start": pos,
                    "end": pos + len(segment),
                    "chunk_size": self._chunk_size,
                    "overlap": self._overlap,
                },
            )
            chunks.append(chunk)
            pos += step
            idx += 1

        return chunks
