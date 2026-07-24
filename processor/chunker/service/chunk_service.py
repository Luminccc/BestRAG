"""ChunkService — Chunk 编排层 + Strategy Registry。

调用方只传策略名，ChunkService 负责查找 Strategy 并执行切分。
类似 DocumentDispatcher 的 Registry 模式：新增策略无需改 ChunkService。
"""

from document.model import Document

from processor.chunker.model import Chunk
from processor.chunker.strategy import (
    BaseChunkStrategy,
    FixedChunkStrategy,
    RecursiveChunkStrategy,
)

# Strategy Registry — 策略名字符串 → 策略实例
CHUNK_STRATEGIES: dict[str, BaseChunkStrategy] = {
    "fixed": FixedChunkStrategy(),
    "recursive": RecursiveChunkStrategy(),
}


class ChunkService:
    """Chunk 编排服务。

    Usage::

        service = ChunkService()
        chunks = service.chunk(document, strategy="recursive")
    """

    def chunk(self, document: Document, strategy: str) -> list[Chunk]:
        """将 Document 按指定策略切分为 Chunk 列表。

        Args:
            document: Document 对象（通常来自 Cleaner 的输出）。
            strategy: 策略名，Registry 中的键（如 "fixed" / "recursive"）。

        Returns:
            Chunk 列表，每个 Chunk 的 document_id 指向来源 Document.id。

        Raises:
            ValueError: strategy 不在 Registry 中。
        """
        strategy_instance = CHUNK_STRATEGIES.get(strategy)
        if strategy_instance is None:
            available = ", ".join(CHUNK_STRATEGIES.keys())
            raise ValueError(
                f"未知策略: '{strategy}'，可用策略: [{available}]"
            )

        return strategy_instance.split(document.content, document.id)
