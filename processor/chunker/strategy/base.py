"""BaseChunkStrategy — 所有 Chunk 策略的抽象基类。

每种策略接收清洗后的文本和 Document id，返回 Chunk 列表。
策略只负责切分算法，不负责 Document 解析或调用 Cleaner。

继承自 core.strategy 框架层，保持 v0.1 API 兼容。
"""

from abc import abstractmethod

from core.strategy.chunk import BaseChunkStrategy as CoreBaseChunkStrategy
from processor.chunker.model import Chunk


class BaseChunkStrategy(CoreBaseChunkStrategy):
    """Chunk 策略抽象契约（v0.1 兼容层）。"""

    @abstractmethod
    def split(self, text: str, document_id: str) -> list[Chunk]:
        """将文本切分为 Chunk 列表。

        Args:
            text:        清洗后的 Document.content。
            document_id: 来源 Document 的 id。

        Returns:
            Chunk 列表，每个 Chunk 包含内容、索引、元数据。
        """
