"""ProcessorService — Processor Pipeline 统一编排入口。

标准流程：
    Document → Cleaner → Clean Document
        ↓
    ChunkService → Chunk[]
        ↓
    Transformer → Normalized Document
        ↓
    ProcessedDocument { document, chunks }

不负责：
- Document 创建（属于 DocumentService）
- 文件读取（属于 Parser）
"""

from document.model import Document

from processor.chunker.service import ChunkService
from processor.cleaner import TextCleaner
from processor.model import ProcessedDocument
from processor.transformer import TransformerService


class ProcessorService:
    """Processor Pipeline 编排服务。

    支持默认构造和显式注入：

    Usage::

        # 默认构造（开发方便）
        svc = ProcessorService()

        # 显式注入（测试和替换）
        svc = ProcessorService(cleaner, chunk_service, transformer_service)
    """

    def __init__(
        self,
        cleaner: TextCleaner | None = None,
        chunk_service: ChunkService | None = None,
        transformer_service: TransformerService | None = None,
    ):
        self._cleaner = cleaner or TextCleaner()
        self._chunk_service = chunk_service or ChunkService()
        self._transformer_service = transformer_service or TransformerService()

    def process(self, document: Document, strategy: str = "recursive") -> ProcessedDocument:
        """执行完整 Pipeline：Cleaner → Chunker → Transformer。

        Args:
            document: DocumentService 产出的 Document 对象。
            strategy: Chunk 策略名（"fixed" / "recursive"）。

        Returns:
            包含标准化 Document 和 Chunk 列表的 ProcessedDocument。
        """
        # Step 1: Cleaner
        clean = self._cleaner.clean(document)

        # Step 2: Chunker
        chunks = self._chunk_service.chunk(clean, strategy)

        # Step 3: Transformer（作用于 Document）
        normalized = self._transformer_service.transform(clean)

        return ProcessedDocument(
            document=normalized,
            chunks=chunks,
        )
