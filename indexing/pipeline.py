"""IndexPipeline — 索引流程编排核心。

流程::

    ProcessedDocument
        │
        ▼
    Chunk → IndexChunk（元数据映射）
        │
        ▼
    Embedding（批量，batch_size 可配）
        │
        ▼
    VectorWriter → VectorStore
"""

from core.config import get_config
from core.logger import get_logger
from core.registry import get_service

from indexing.exception import IndexingError
from indexing.model import IndexChunk, IndexResult
from indexing.writer import VectorWriter

logger = get_logger(__name__)

_EMBEDDING_KEY = "embedding"


class IndexPipeline:
    """索引管线 — 串联 Chunk 转换 → Embedding → VectorStore。

    Usage::

        pipeline = IndexPipeline()
        result = pipeline.execute(processed_document)
    """

    def __init__(self, writer: VectorWriter | None = None):
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

            # Step 2: Embedding（批量）
            self._embed_chunks(index_chunks)

            # Step 3: Write
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

    def _embed_chunks(self, chunks: list[IndexChunk]) -> None:
        """批量调用 Embedding Provider 填充向量。"""
        texts = [c.content for c in chunks]
        if not texts:
            return

        cfg = get_config().indexing
        provider = get_service(_EMBEDDING_KEY)

        # 分批处理（provider.embed_documents 返回 List[List[float]] 或 List[EmbeddingResult]）
        all_vectors: list[list[float]] = []
        for i in range(0, len(texts), cfg.batch_size):
            batch = texts[i:i + cfg.batch_size]
            raw = provider.embed_documents(batch)
            # 兼容两种返回类型：list of vectors 或 list of EmbeddingResult
            if raw and hasattr(raw[0], 'vector'):
                all_vectors.extend(r.vector for r in raw)
            else:
                all_vectors.extend(raw)

        if len(all_vectors) != len(chunks):
            raise IndexingError(
                f"Embedding 数量不匹配: 期望 {len(chunks)}, 实际 {len(all_vectors)}"
            )

        for chunk, vec in zip(chunks, all_vectors):
            chunk.embedding = vec
