"""IndexPipeline — 索引流程编排核心。

流程::

    ProcessedDocument
        │
        ▼
    Chunk → IndexChunk（元数据映射）
        │
        ▼
    MetadataEnrichmentStage
        │
        ▼
    EmbeddingStage（批量）
        │
        ▼
    WriterStage → VectorStore

每个阶段可独立替换，通过 stages 参数注入。
"""

from typing import List

from core.config import get_config
from core.logger import get_logger
from core.registry import get_service

from indexing.exception import IndexingError
from indexing.model import IndexChunk, IndexResult
from indexing.stages import (
    BaseIndexStage,
    EmbeddingStage,
    MetadataEnrichmentStage,
    WriterStage,
)
from indexing.writer import VectorWriter

logger = get_logger(__name__)

_EMBEDDING_KEY = "embedding"


class IndexPipeline:
    """索引管线 — 串联 Chunk 转换 → 阶段处理 → VectorStore。

    Usage::

        pipeline = IndexPipeline()
        result = pipeline.execute(processed_document)
    """

    def __init__(
        self,
        stages: list[BaseIndexStage] | None = None,
        writer: VectorWriter | None = None,
    ):
        self._stages = stages or [
            MetadataEnrichmentStage(),
            EmbeddingStage(),
            WriterStage(),
        ]
        self._writer = writer or VectorWriter()

    # ── 主入口 ────────────────────────────────────

    def execute(self, document) -> IndexResult:
        """对 ProcessedDocument 执行完整索引流程。

        Args:
            document: ProcessedDocument（含 chunks）。

        Returns:
            IndexResult（success / chunk_count / error）。
        """
        doc_id = document.document.id

        try:
            # Step 1: Chunk → IndexChunk
            index_chunks = self._to_index_chunks(document)

            if not index_chunks:
                return IndexResult(success=True, document_id=doc_id, chunk_count=0)

            # Step 2: 阶段式处理（元数据增强 → Embedding → 写入）
            for stage in self._stages:
                logger.info(f"索引阶段: {stage.name}")
                index_chunks = stage.process(index_chunks)

            # Step 3: 执行写入
            ids = self._writer.write(index_chunks)

            logger.info(f"索引完成: doc={doc_id}, chunks={len(ids)}")
            return IndexResult(success=True, document_id=doc_id, chunk_count=len(ids))

        except Exception as e:
            logger.error(f"索引失败: doc={doc_id}, error={e}")
            return IndexResult(
                success=False,
                document_id=doc_id,
                error=str(e),
            )

    # ── 内部步骤 ──────────────────────────────────

    def _to_index_chunks(self, document) -> list[IndexChunk]:
        """Chunk → IndexChunk，保留原始 metadata。"""
        doc_id = document.document.id
        result: list[IndexChunk] = []
        for c in document.chunks:
            result.append(IndexChunk(
                id=c.id,
                document_id=doc_id,
                content=c.content,
                metadata={**c.metadata, "document_id": doc_id, "chunk_index": c.index},
            ))
        return result
